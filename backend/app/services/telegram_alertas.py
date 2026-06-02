"""
telegram_alertas.py — Resumen diario de alertas operativas por Telegram.

Flujo:
  1. El scheduler corre cada minuto y comprueba si la hora actual == hora configurada.
  2. Si sí (y no se envió ya hoy), llama a obtener_alertas(db).
  3. Agrupa por severidad y formatea un único mensaje con todas las alertas activas.
  4. Si una alerta tiene observación de operador guardada, la incluye en el mensaje.
  5. Envía el mensaje y registra que ya se envió hoy (en memoria — se restablece al
     día siguiente o al reiniciar el servidor, lo cual es correcto: siempre reporta).

Config en tabla `configuraciones`:
  telegram_bot_token      → Token del bot (@BotFather)
  telegram_chat_id        → ID del chat/usuario destino
  telegram_hora_resumen   → Hora del resumen diario en formato HH:MM (default: 07:00)
"""

import asyncio
import logging
from datetime import date, datetime

import requests
from app.core.config import get_settings
from app.core.database import SessionLocal
from app.models.models import Configuracion
from app.services.dashboard import obtener_alertas

logger = logging.getLogger(__name__)

# ── Claves de configuración ───────────────────────────────────────────────────
_KEY_TOKEN = "telegram_bot_token"
_KEY_CHAT = "telegram_chat_id"
_KEY_HORA = "telegram_hora_resumen"

_HORA_DEFAULT = "07:00"

_SEVERIDAD_EMOJI = {
    "CRITICA": "🔴",
    "ALTA": "🟠",
    "MEDIA": "🟡",
}
_TIPO_LABEL = {
    "VOLADO_STOCK": "Lote volado en stock",
    "RETRASO_MUESTREO": "Retraso en muestreo",
    "RETRASO_LEY": "Retraso en análisis de ley",
    "RETRASO_RECUPERACION": "Retraso en recuperación",
}

# ── Estado en memoria (se restablece al reiniciar = envía siempre) ────────────
_ultimo_envio: date | None = None


# ── Helpers de configuración ──────────────────────────────────────────────────


def _get_cfg(db, clave: str, default: str = "") -> str:
    row = db.query(Configuracion).filter(Configuracion.clave == clave).first()
    return row.valor if row else default


def _set_cfg(db, clave: str, valor: str, descripcion: str = "") -> None:
    row = db.query(Configuracion).filter(Configuracion.clave == clave).first()
    if row:
        row.valor = valor
    else:
        db.add(Configuracion(clave=clave, valor=valor, descripcion=descripcion))
    db.commit()


def get_telegram_config(db) -> dict:
    settings = get_settings()
    token_env = settings.telegram_bot_token
    token_db = _get_cfg(db, _KEY_TOKEN)
    bot_token = token_env or token_db
    return {
        "bot_token": bot_token,
        "chat_id": _get_cfg(db, _KEY_CHAT),
        "hora_resumen": _get_cfg(db, _KEY_HORA, _HORA_DEFAULT),
        "configurado": bool(bot_token and _get_cfg(db, _KEY_CHAT)),
        "desde_env": bool(token_env),
    }


def set_telegram_config(
    db,
    bot_token: str,
    chat_id: str,
    hora_resumen: str = _HORA_DEFAULT,
) -> dict:
    settings = get_settings()
    # Solo guardamos en base de datos si NO está configurado vía variables de entorno (.env)
    if not settings.telegram_bot_token:
        if bot_token and bot_token != "(mantener)":
            _set_cfg(db, _KEY_TOKEN, bot_token, "Token del bot de Telegram")
    _set_cfg(db, _KEY_CHAT, chat_id, "Chat ID destino de alertas")
    _set_cfg(db, _KEY_HORA, hora_resumen, "Hora del resumen diario (HH:MM)")
    return get_telegram_config(db)


# ── Envío de mensajes ─────────────────────────────────────────────────────────


def _enviar_mensaje(bot_token: str, chat_id: str, texto: str) -> bool:
    """Envía un mensaje vía Telegram Bot API. Retorna True si fue exitoso."""
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    try:
        r = requests.post(
            url,
            json={"chat_id": chat_id, "text": texto, "parse_mode": "HTML"},
            timeout=10,
        )
        if not r.ok:
            logger.warning("Telegram API error %s: %s", r.status_code, r.text[:200])
        return r.ok
    except Exception as e:
        logger.error("Error enviando mensaje Telegram: %s", e)
        return False


def enviar_test(db) -> dict:
    """Envía un mensaje de prueba al chat configurado."""
    cfg = get_telegram_config(db)
    if not cfg["configurado"]:
        return {"ok": False, "error": "Bot no configurado (falta token o chat_id)"}
    texto = (
        "✅ <b>INVERMIN Paititi — Conexión verificada</b>\n"
        f"🕐 {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
        f"📊 El resumen diario de alertas se enviará a las <b>{cfg['hora_resumen']}</b>."
    )
    ok = _enviar_mensaje(cfg["bot_token"], cfg["chat_id"], texto)
    return {"ok": ok, "error": None if ok else "No se pudo enviar el mensaje"}


# ── Formato del resumen ───────────────────────────────────────────────────────


def _obtener_observacion(db, tipo: str, ip: str) -> str | None:
    """Lee la última observación de operador para esta alerta, si existe."""
    clave = f"obs_alerta:{tipo}:{ip}"
    row = db.query(Configuracion).filter(Configuracion.clave == clave).first()
    if not row or not row.valor:
        return None
    # Retorna solo la última línea (la más reciente)
    lineas = [li.strip() for li in row.valor.strip().splitlines() if li.strip()]
    return lineas[-1] if lineas else None


def _formatear_resumen(db, alertas: list) -> str:
    """Construye el mensaje de resumen agrupado por severidad."""
    ahora = datetime.now().strftime("%d/%m/%Y %H:%M")
    total = len(alertas)

    if not alertas:
        return f"📊 <b>RESUMEN DIARIO — {ahora}</b>\n\n" "✅ Sin alertas activas. Todo en orden."

    # Agrupar por severidad
    por_sev: dict[str, list] = {"CRITICA": [], "ALTA": [], "MEDIA": []}
    for a in alertas:
        por_sev.setdefault(a.severidad, []).append(a)

    lineas = [f"📊 <b>RESUMEN DIARIO DE ALERTAS — {ahora}</b>\n"]

    for sev in ("CRITICA", "ALTA", "MEDIA"):
        grupo = por_sev.get(sev, [])
        if not grupo:
            continue
        emoji = _SEVERIDAD_EMOJI[sev]
        lineas.append(f"{emoji} <b>{sev}S ({len(grupo)})</b>")
        for a in grupo:
            tipo_lbl = _TIPO_LABEL.get(a.tipo, a.tipo)
            lineas.append(
                f"  • <b>{tipo_lbl}</b> — Lote <code>{a.ip}</code> "
                f"({a.proveedor}) — {a.horas_retraso:.1f}h"
            )
            obs = _obtener_observacion(db, a.tipo, a.ip)
            if obs:
                lineas.append(f"    └ <i>{obs}</i>")
        lineas.append("")  # línea en blanco entre grupos

    lineas.append(
        f"<b>Total: {total} alerta{'s' if total != 1 else ''} activa{'s' if total != 1 else ''}</b>"
    )
    return "\n".join(lineas)


# ── Ciclo principal del scheduler ─────────────────────────────────────────────


async def scheduler_loop() -> None:
    """
    Loop asíncrono que corre en background durante la vida de la app.
    Revisa cada minuto si llegó la hora configurada para el resumen diario.
    """
    global _ultimo_envio
    logger.info("Telegram alertas scheduler iniciado (modo resumen diario)")

    while True:
        await asyncio.sleep(60)  # revisar cada minuto
        try:
            _revisar_y_enviar_si_corresponde()
        except Exception as e:
            logger.error("Error en scheduler de alertas: %s", e)


def _revisar_y_enviar_si_corresponde() -> None:
    global _ultimo_envio

    ahora = datetime.now()
    hoy = ahora.date()

    # Si ya enviamos hoy, no hacer nada
    if _ultimo_envio == hoy:
        return

    db = SessionLocal()
    try:
        cfg = get_telegram_config(db)
        if not cfg["configurado"]:
            return  # Sin config → no hacer nada

        # Verificar si la hora actual coincide con la hora configurada (HH:MM)
        hora_cfg = cfg["hora_resumen"].strip() or _HORA_DEFAULT
        hora_actual = ahora.strftime("%H:%M")

        if hora_actual != hora_cfg:
            return  # Todavía no es la hora

        # ¡Es la hora! Obtener alertas y enviar resumen
        respuesta = obtener_alertas(db)
        texto = _formatear_resumen(db, respuesta.alertas)
        ok = _enviar_mensaje(cfg["bot_token"], cfg["chat_id"], texto)

        if ok:
            _ultimo_envio = hoy
            logger.info(
                "Resumen diario enviado: %d alertas activas",
                len(respuesta.alertas),
            )
        else:
            logger.warning("No se pudo enviar el resumen diario por Telegram")

    except Exception as e:
        logger.error("Error en _revisar_y_enviar_si_corresponde: %s", e)
    finally:
        db.close()
