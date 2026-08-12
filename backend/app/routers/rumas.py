"""
Router: Módulo Rumas y Campañas.

Permisos (RF-SYS-001, gestionados en tabla permisos):
  - Crear/cerrar campaña, editar meta → CAMPANAS CREATE/UPDATE (Admin, Gerencia)
  - Ver campañas               → CAMPANAS VIEW (Admin, Gerencia, JefeComercial, Comercial, OperadorBalanza, TecnicoMuestreo)
  - Crear/asignar/cerrar rumas  → RUMAS CREATE/UPDATE (Admin, Gerencia, JefeComercial, Comercial)
  - Ver rumas                   → RUMAS VIEW
  - Habilitar lote para ruma    → RUMAS UPDATE
"""

from app.core.database import get_db
from app.core.deps import check_permiso
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
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

router = APIRouter(tags=["Rumas y Campañas"])


# ── CAMPAÑAS ──────────────────────────────────────────────────────────────────


@router.get("/campanas/activa", response_model=CampanaOut)
def get_campana_activa(
    db: Session = Depends(get_db),
    current_user=Depends(check_permiso("CAMPANAS", "VIEW")),
):
    """Retorna la campaña activa con métricas y progreso."""
    return ruma_service.obtener_campana_activa(db)


@router.get("/campanas", response_model=list[CampanaOut])
def listar_campanas(
    db: Session = Depends(get_db),
    current_user=Depends(check_permiso("CAMPANAS", "VIEW")),
):
    """Lista todas las campañas (activa + historial)."""
    return ruma_service.listar_campanas(db)


@router.post("/campanas", response_model=CampanaOut, status_code=status.HTTP_201_CREATED)
def crear_campana(
    datos: CampanaCreate,
    db: Session = Depends(get_db),
    current_user=Depends(check_permiso("CAMPANAS", "CREATE")),
):
    """Crea una campaña nueva (solo si no hay una activa)."""
    return ruma_service.crear_campana(db, datos, current_user)


@router.patch("/campanas/{campana_id}/cerrar", response_model=CampanaOut)
def cerrar_campana(
    campana_id: int,
    datos: CampanaCerrarRequest,
    db: Session = Depends(get_db),
    current_user=Depends(check_permiso("CAMPANAS", "UPDATE")),
):
    """
    Cierra la campaña activa y crea automáticamente la siguiente
    con la meta indicada en el body.
    """
    return ruma_service.cerrar_campana(db, campana_id, datos, current_user)


@router.patch("/campanas/{campana_id}/meta", response_model=CampanaOut)
def editar_meta(
    campana_id: int,
    datos: CampanaEditarMeta,
    db: Session = Depends(get_db),
    current_user=Depends(check_permiso("CAMPANAS", "UPDATE")),
):
    """Edita la meta de oro fino de una campaña."""
    return ruma_service.editar_meta_campana(db, campana_id, datos, current_user)


@router.post("/campanas/{campana_id}/rumas/{ruma_id}", response_model=CampanaOut)
def asignar_ruma_campana(
    campana_id: int,
    ruma_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(check_permiso("CAMPANAS", "UPDATE")),
):
    """Asigna una ruma independiente a una campaña."""
    return ruma_service.asignar_ruma_a_campana(db, campana_id, ruma_id, current_user)


# ── RUMAS ─────────────────────────────────────────────────────────────────────


@router.get("/rumas", response_model=list[RumaLista])
def listar_rumas(
    db: Session = Depends(get_db),
    current_user=Depends(check_permiso("RUMAS", "VIEW")),
):
    """Lista rumas de la campaña activa."""
    return ruma_service.listar_rumas(db)


@router.post("/rumas", response_model=RumaOut, status_code=status.HTTP_201_CREATED)
def crear_ruma(
    db: Session = Depends(get_db),
    current_user=Depends(check_permiso("RUMAS", "CREATE")),
):
    """Crea una ruma vacía en la campaña activa."""
    return ruma_service.crear_ruma(db, current_user)


@router.get("/rumas/lotes-disponibles", response_model=list[LoteDisponibleOut])
def lotes_disponibles(
    db: Session = Depends(get_db),
    current_user=Depends(check_permiso("RUMAS", "VIEW")),
):
    """Lotes habilitados para ruma que aún no tienen ruma asignada."""
    return ruma_service.listar_lotes_disponibles(db)


@router.get("/rumas/{ruma_id}", response_model=RumaOut)
def obtener_ruma(
    ruma_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(check_permiso("RUMAS", "VIEW")),
):
    """Detalle de una ruma con sus lotes y totales ponderados."""
    return ruma_service.obtener_ruma(db, ruma_id)


@router.put("/rumas/{ruma_id}/lotes", response_model=RumaOut)
def asignar_lotes(
    ruma_id: int,
    datos: AsignarLotesRequest,
    db: Session = Depends(get_db),
    current_user=Depends(check_permiso("RUMAS", "UPDATE")),
):
    """
    Reemplaza la lista de lotes de la ruma (PUT semántica: enviar la lista
    completa deseada). Valida habilitado_ruma y sin otra ruma.
    """
    return ruma_service.asignar_lotes(db, ruma_id, datos, current_user)


@router.patch("/rumas/{ruma_id}/cerrar", response_model=RumaOut)
def cerrar_ruma(
    ruma_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(check_permiso("RUMAS", "UPDATE")),
):
    """Cierra la ruma. Una ruma cerrada no acepta más cambios."""
    return ruma_service.cerrar_ruma(db, ruma_id, current_user)


@router.patch("/lotes/{ip}/habilitar-ruma", status_code=status.HTTP_200_OK)
def habilitar_lote_para_ruma(
    ip: str,
    datos: HabilitarRumaRequest,
    db: Session = Depends(get_db),
    current_user=Depends(check_permiso("RUMAS", "UPDATE")),
):
    """
    Habilita manualmente un lote para ser asignado a una ruma.
    Solo roles con permiso RUMAS/UPDATE: Admin, Gerencia, JefeComercial, Comercial.
    """
    return ruma_service.habilitar_lote_manual(db, ip, current_user, datos.motivo)
