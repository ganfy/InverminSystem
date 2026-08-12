"""
Router de administración del sistema.
- Configuración de constantes de cálculo (factor_oz_tc, umbral_volado, blank_correction_ag)
- Configuración de notificaciones por Telegram

Permisos (tabla permisos):
  ADMINISTRACION VIEW   → Admin, Gerencia  (leer config de cálculo y Telegram)
  ADMINISTRACION UPDATE → solo Admin        (modificar constantes y Telegram)
"""

from app.core.deps import check_permiso, get_current_user, get_db
from app.services.config_calculo import (
    actualizar_constante,
    get_config_public_dict,
    listar_constantes,
)
from app.services.telegram_alertas import (
    enviar_test,
    get_telegram_config,
    set_telegram_config,
)
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

router = APIRouter(prefix="/admin", tags=["Administración"])


# ── Constantes de cálculo ─────────────────────────────────────────────────────


class ConstanteUpdate(BaseModel):
    valor: str


@router.get("/config-public")
def get_config_public(
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    """
    Retorna las configuraciones públicas del sistema (unidades, datos de empresa, etc.).
    Accesible por cualquier usuario autenticado.
    """
    return get_config_public_dict(db)


@router.get("/config-calculo")
def get_config_calculo(
    db: Session = Depends(get_db),
    _=Depends(check_permiso("ADMINISTRACION", "VIEW")),
):
    """Lista las constantes de cálculo metalúrgico con sus valores actuales. Admin y Gerencia."""
    return listar_constantes(db)


@router.put("/config-calculo/{clave}")
def put_config_calculo(
    clave: str,
    body: ConstanteUpdate,
    db: Session = Depends(get_db),
    _=Depends(check_permiso("ADMINISTRACION", "UPDATE")),
):
    """Actualiza el valor de una constante de cálculo. Solo Admin."""
    try:
        return actualizar_constante(db, clave, body.valor)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)) from e


# ── Telegram ──────────────────────────────────────────────────────────────────


class TelegramConfig(BaseModel):
    bot_token: str | None = Field(None, description="Token del bot de Telegram")
    chat_id: str = Field(..., min_length=1, description="ID del chat o usuario destino")
    hora_resumen: str = Field(
        "07:00", pattern=r"^\d{2}:\d{2}$", description="Hora del resumen diario en formato HH:MM"
    )


@router.get("/telegram")
def get_telegram(
    db: Session = Depends(get_db),
    _=Depends(check_permiso("ADMINISTRACION", "VIEW")),
):
    """Devuelve la configuración de Telegram. El token se enmascara. Admin y Gerencia."""
    cfg = get_telegram_config(db)
    # Enmascarar token: solo mostrar los primeros 8 caracteres
    if cfg["bot_token"]:
        tok = cfg["bot_token"]
        cfg["bot_token"] = tok[:8] + "..." if len(tok) > 8 else "***"
    return cfg


@router.put("/telegram")
def put_telegram(
    body: TelegramConfig,
    db: Session = Depends(get_db),
    _=Depends(check_permiso("ADMINISTRACION", "UPDATE")),
):
    """Guarda la configuración del bot de Telegram. Solo Admin."""
    cfg = set_telegram_config(db, body.bot_token or "", body.chat_id, body.hora_resumen)
    if cfg["bot_token"]:
        tok = cfg["bot_token"]
        cfg["bot_token"] = tok[:8] + "..." if len(tok) > 8 else "***"
    return cfg


@router.post("/telegram/test")
def post_telegram_test(
    db: Session = Depends(get_db),
    _=Depends(check_permiso("ADMINISTRACION", "UPDATE")),
):
    """Envía un mensaje de prueba al chat configurado. Solo Admin."""
    result = enviar_test(db)
    if not result["ok"]:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=result.get("error", "Error desconocido al enviar mensaje"),
        )
    return {"mensaje": "Mensaje de prueba enviado correctamente"}
