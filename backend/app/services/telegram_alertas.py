"""
telegram_alertas.py — Notificaciones de alertas operativas por Telegram.

Flujo:
  1. Cada N minutos (configurable), se llaman obtener_alertas(db).
  2. Se calcula un "fingerprint" por alerta: "{tipo}:{ip}".
  3. Se compara con los fingerprints ya enviados (guardados en configuraciones).
  4. Solo las alertas nuevas se envían por Telegram.
  5. Si una alerta desaparece, se elimina del registro → si vuelve, se reenvía.

Config en tabla `configuraciones`:
  telegram_bot_token        → Token del bot (@BotFather)
  telegram_chat_id          → ID del chat/usuario destino
  telegram_intervalo_min    → Minutos entre revisiones (default: 30)
  telegram_alertas_enviadas → JSON interno; no editar manualmente
"""

import asyncio
import json
import logging
from datetime import datetime

import requests
from app.core.database import SessionLocal
from app.models.models import Configuracion
from app.services.dashboard import obtener_alertas

logger = logging.getLogger(__name__)

# ── Claves de configuración ───────────────────────────────────────────────────
_KEY_TOKEN = "telegram_bot_token"
_KEY_CHAT = "telegram_chat_id"
_KEY_INTERVALO = "telegram_intervalo_min"
_KEY_ENVIADAS = "telegram_alertas_enviadas"

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
    return {
        "bot_token": _get_cfg(db, _KEY_TOKEN),
        "chat_id": _get_cfg(db, _KEY_CHAT),
        "intervalo_min": int(_get_cfg(db, _KEY_INTERVALO, "30")),
        "configurado": bool(_get_cfg(db, _KEY_TOKEN) and _get_cfg(db, _KEY_CHAT)),
    }


def set_telegram_config(db, bot_token: str, chat_id: str, intervalo_min: int = 30) -> dict:
    _set_cfg(db, _KEY_TOKEN, bot_token, "Token del bot de Telegram")
    _set_cfg(db, _KEY_CHAT, chat_id, "Chat ID destino de alertas")
    _set_cfg(db, _KEY_INTERVALO, str(intervalo_min), "Minutos entre revisiones de alertas")
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


def _formatear_alerta(alerta) -> str:
    emoji = _SEVERIDAD_EMOJI.get(alerta.severidad, "⚪")
    tipo = _TIPO_LABEL.get(alerta.tipo, alerta.tipo)
    return (
        f"{emoji} <b>{tipo}</b>\n"
        f"📋 Lote: <code>{alerta.ip}</code>\n"
        f"🏭 Proveedor: {alerta.proveedor}\n"
        f"⏱ Retraso: {alerta.horas_retraso:.1f}h\n"
        f"ℹ️ {alerta.descripcion}"
    )


def enviar_test(db) -> dict:
    """Envía un mensaje de prueba al chat configurado."""
    cfg = get_telegram_config(db)
    if not cfg["configurado"]:
        return {"ok": False, "error": "Bot no configurado (falta token o chat_id)"}
    texto = (
        "✅ <b>Paititi ERP — Conexión verificada</b>\n"
        f"🕐 {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
        "Las alertas operativas llegarán a este chat."
    )
    ok = _enviar_mensaje(cfg["bot_token"], cfg["chat_id"], texto)
    return {"ok": ok, "error": None if ok else "No se pudo enviar el mensaje"}


# ── Lógica de deduplicación ───────────────────────────────────────────────────


def _fingerprint(alerta) -> str:
    """Identificador único de una alerta activa."""
    return f"{alerta.tipo}:{alerta.ip}"


def _cargar_enviadas(db) -> set[str]:
    raw = _get_cfg(db, _KEY_ENVIADAS, "[]")
    try:
        return set(json.loads(raw))
    except Exception:
        return set()


def _guardar_enviadas(db, enviadas: set[str]) -> None:
    _set_cfg(db, _KEY_ENVIADAS, json.dumps(sorted(enviadas)))


# ── Ciclo principal del scheduler ─────────────────────────────────────────────


async def scheduler_loop() -> None:
    """
    Loop asíncrono que corre en background durante la vida de la app.
    Revisa alertas cada N minutos y envía por Telegram solo las nuevas.
    """
    logger.info("Telegram alertas scheduler iniciado")
    while True:
        try:
            _revisar_y_enviar()
        except Exception as e:
            logger.error("Error en scheduler de alertas: %s", e)

        db = SessionLocal()
        try:
            intervalo = int(_get_cfg(db, _KEY_INTERVALO, "30"))
        except Exception:
            intervalo = 30
        finally:
            db.close()

        await asyncio.sleep(intervalo * 60)


def _revisar_y_enviar() -> None:
    db = SessionLocal()
    try:
        cfg = get_telegram_config(db)
        if not cfg["configurado"]:
            return  # Sin config → no hacer nada

        respuesta = obtener_alertas(db)
        actuales = {_fingerprint(a): a for a in respuesta.alertas}
        ya_enviadas = _cargar_enviadas(db)

        nuevas = [a for fp, a in actuales.items() if fp not in ya_enviadas]

        if not nuevas:
            # Actualizar estado: eliminar fingerprints que ya no existen
            _guardar_enviadas(db, ya_enviadas & set(actuales.keys()))
            return

        # Enviar un mensaje por alerta nueva
        enviadas_ok = set(ya_enviadas)
        for alerta in nuevas:
            texto = _formatear_alerta(alerta)
            ok = _enviar_mensaje(cfg["bot_token"], cfg["chat_id"], texto)
            if ok:
                enviadas_ok.add(_fingerprint(alerta))
                logger.info("Alerta enviada: %s %s", alerta.tipo, alerta.ip)

        # Limpiar las que ya no están activas + guardar nuevas enviadas
        _guardar_enviadas(db, enviadas_ok & set(actuales.keys()))
        db.commit()

    except Exception as e:
        logger.error("Error en _revisar_y_enviar: %s", e)
    finally:
        db.close()
