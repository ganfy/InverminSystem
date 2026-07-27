"""
Router: Módulo Rumas y Campañas.

Permisos (RBAC según RF-SYS-001):
  - Crear/cerrar campaña, editar meta → Admin, Gerencia
  - Crear ruma, asignar lotes, cerrar ruma → Admin, Gerencia, Comercial
  - Ver → Admin, Gerencia, Comercial
  - Habilitar lote manualmente → Admin, Gerencia, Comercial
"""

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.enums import RolSistema
from app.models.models import Usuario
from app.schemas.rumas import (
    AsignarLotesRequest,
    CampanaCerrarRequest,
    CampanaCreate,
    CampanaEditarMeta,
    CampanaOut,
    HabilitarRumaRequest,
    LoteDisponibleOut,
    RumaLista,
    RumaOut,
)
from app.services import rumas as ruma_service
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

router = APIRouter(tags=["Rumas y Campañas"])

_ROLES_GERENCIA = {RolSistema.ADMIN, RolSistema.GERENCIA}
_ROLES_COMERCIAL = {
    RolSistema.ADMIN,
    RolSistema.GERENCIA,
    RolSistema.COMERCIAL,
    RolSistema.JEFE_COMERCIAL,
}


def _require(user: Usuario, roles: set[RolSistema]) -> None:
    if user.rol.codigo not in {r.value for r in roles}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Sin permisos para esta acción"
        )


# ── CAMPAÑAS ──────────────────────────────────────────────────────────────────


@router.get("/campanas/activa", response_model=CampanaOut)
def get_campana_activa(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Retorna la campaña activa con métricas y progreso."""
    _require(current_user, _ROLES_COMERCIAL)
    return ruma_service.obtener_campana_activa(db)


@router.get("/campanas", response_model=list[CampanaOut])
def listar_campanas(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Lista todas las campañas (activa + historial)."""
    _require(current_user, _ROLES_COMERCIAL)
    return ruma_service.listar_campanas(db)


@router.post("/campanas", response_model=CampanaOut, status_code=status.HTTP_201_CREATED)
def crear_campana(
    datos: CampanaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Crea una campaña nueva (solo si no hay una activa)."""
    _require(current_user, _ROLES_GERENCIA)
    return ruma_service.crear_campana(db, datos, current_user)


@router.patch("/campanas/{campana_id}/cerrar", response_model=CampanaOut)
def cerrar_campana(
    campana_id: int,
    datos: CampanaCerrarRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Cierra la campaña activa y crea automáticamente la siguiente
    con la meta indicada en el body.
    """
    _require(current_user, _ROLES_GERENCIA)
    return ruma_service.cerrar_campana(db, campana_id, datos, current_user)


@router.patch("/campanas/{campana_id}/meta", response_model=CampanaOut)
def editar_meta(
    campana_id: int,
    datos: CampanaEditarMeta,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Edita la meta de oro fino de una campaña."""
    _require(current_user, _ROLES_GERENCIA)
    return ruma_service.editar_meta_campana(db, campana_id, datos, current_user)


@router.post("/campanas/{campana_id}/rumas/{ruma_id}", response_model=CampanaOut)
def asignar_ruma_campana(
    campana_id: int,
    ruma_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Asigna una ruma independiente a una campaña."""
    _require(current_user, _ROLES_GERENCIA)  # O el rol que prefieras
    return ruma_service.asignar_ruma_a_campana(db, campana_id, ruma_id, current_user)


# ── RUMAS ─────────────────────────────────────────────────────────────────────


@router.get("/rumas", response_model=list[RumaLista])
def listar_rumas(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Lista rumas de la campaña activa."""
    _require(current_user, _ROLES_COMERCIAL)
    return ruma_service.listar_rumas(db)


@router.post("/rumas", response_model=RumaOut, status_code=status.HTTP_201_CREATED)
def crear_ruma(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Crea una ruma vacía en la campaña activa."""
    _require(current_user, _ROLES_COMERCIAL)
    return ruma_service.crear_ruma(db, current_user)


@router.get("/rumas/lotes-disponibles", response_model=list[LoteDisponibleOut])
def lotes_disponibles(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Lotes habilitados para ruma que aún no tienen ruma asignada."""
    _require(current_user, _ROLES_COMERCIAL)
    return ruma_service.listar_lotes_disponibles(db)


@router.get("/rumas/{ruma_id}", response_model=RumaOut)
def obtener_ruma(
    ruma_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Detalle de una ruma con sus lotes y totales ponderados."""
    _require(current_user, _ROLES_COMERCIAL)
    return ruma_service.obtener_ruma(db, ruma_id)


@router.put("/rumas/{ruma_id}/lotes", response_model=RumaOut)
def asignar_lotes(
    ruma_id: int,
    datos: AsignarLotesRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Reemplaza la lista de lotes de la ruma (PUT semántica: enviar la lista
    completa deseada). Valida habilitado_ruma y sin otra ruma.
    """
    _require(current_user, _ROLES_COMERCIAL)
    return ruma_service.asignar_lotes(db, ruma_id, datos, current_user)


@router.patch("/rumas/{ruma_id}/cerrar", response_model=RumaOut)
def cerrar_ruma(
    ruma_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Cierra la ruma. Una ruma cerrada no acepta más cambios."""
    _require(current_user, _ROLES_COMERCIAL)
    return ruma_service.cerrar_ruma(db, ruma_id, current_user)


@router.patch("/lotes/{ip}/habilitar-ruma", status_code=status.HTTP_200_OK)
def habilitar_lote_para_ruma(
    ip: str,
    datos: HabilitarRumaRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Habilita manualmente un lote para ser asignado a una ruma.
    Solo Admin, Gerencia y Comercial.
    """
    _require(current_user, _ROLES_COMERCIAL)
    return ruma_service.habilitar_lote_manual(db, ip, current_user, datos.motivo)
