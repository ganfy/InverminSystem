"""
Router de administración del sistema.
Actualmente: configuración de constantes de cálculo.
Requiere rol Admin (GET también accesible a Gerencia).
"""

from app.core.deps import get_current_user, get_db
from app.models.models import Usuario
from app.services.config_calculo import actualizar_constante, listar_constantes
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

router = APIRouter(prefix="/admin", tags=["Administración"])


class ConstanteUpdate(BaseModel):
    valor: str


def _require_admin(current_user: Usuario = Depends(get_current_user)) -> Usuario:
    if current_user.rol not in ("Admin",):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo Admin puede modificar constantes de cálculo",
        )
    return current_user


def _require_admin_o_gerencia(current_user: Usuario = Depends(get_current_user)) -> Usuario:
    if current_user.rol not in ("Admin", "Gerencia"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso denegado")
    return current_user


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
