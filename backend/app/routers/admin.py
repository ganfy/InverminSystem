"""
Router de administración del sistema.
- Configuración de constantes de cálculo (factor_oz_tc, umbral_volado, blank_correction_ag)
- Configuración de notificaciones por Telegram
"""

from app.core.deps import get_current_user, get_db
from app.models.models import Usuario
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


# ── Guards de rol ─────────────────────────────────────────────────────────────


def _require_admin(current_user: Usuario = Depends(get_current_user)) -> Usuario:
    if current_user.rol.codigo not in ("Admin",):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo Admin puede modificar esta configuración",
        )
    return current_user


def _require_admin_o_gerencia(current_user: Usuario = Depends(get_current_user)) -> Usuario:
    if current_user.rol.codigo not in ("Admin", "Gerencia"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso denegado")
    return current_user


# ── Constantes de cálculo ─────────────────────────────────────────────────────


class ConstanteUpdate(BaseModel):
    valor: str


@router.get("/config-public")
def get_config_public(
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    """
    Retorna las configuraciones públicas del sistema (unidades, datos de empresa, etc.).
    Accesible por cualquier usuario autenticado.
    """
    return get_config_public_dict(db)


@router.get("/config-calculo")
def get_config_calculo(
    db: Session = Depends(get_db),
    _: Usuario = Depends(_require_admin_o_gerencia),
):
    """Lista las constantes de cálculo metalúrgico con sus valores actuales."""
    return listar_constantes(db)


@router.put("/config-calculo/{clave}")
def put_config_calculo(
    clave: str,
    body: ConstanteUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(_require_admin),
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
    _: Usuario = Depends(_require_admin_o_gerencia),
):
    """Devuelve la configuración de Telegram. El token se enmascara."""
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
    _: Usuario = Depends(_require_admin),
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
    _: Usuario = Depends(_require_admin),
):
    """Envía un mensaje de prueba al chat configurado."""
    result = enviar_test(db)
    if not result["ok"]:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=result.get("error", "Error desconocido al enviar mensaje"),
        )
    return {"mensaje": "Mensaje de prueba enviado correctamente"}
