from app.core.database import get_db
from app.core.deps import check_permiso
from app.schemas.pruebas import (
    EtiquetadoPruebaOut,
    LotePruebaList,
    PruebaMetalurgicaCreate,
    PruebaMetalurgicaOut,
    PruebaRecuperacionItem,
    SyncPruebasRequest,
    SyncPruebasResponse,
)
from app.services import pruebas as pruebas_service
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

router = APIRouter(prefix="/pruebas", tags=["Pruebas Metalúrgicas"])


@router.get("/lista", response_model=list[LotePruebaList])
def listar_pruebas(
    current_user=Depends(check_permiso("PRUEBAS", "VIEW")),
    db: Session = Depends(get_db),
):
    """Lista todos los lotes y su estado en pruebas metalúrgicas."""
    return pruebas_service.obtener_lista_pruebas(db)


@router.get("/{ip_lote}", response_model=PruebaMetalurgicaOut)
def obtener_detalle_prueba(
    ip_lote: str,
    current_user=Depends(check_permiso("PRUEBAS", "VIEW")),
    db: Session = Depends(get_db),
):
    prueba = pruebas_service.obtener_prueba_por_ip(db, ip_lote)
    if not prueba:
        raise HTTPException(status_code=404, detail="No hay prueba metalúrgica para este lote")
    return prueba


@router.post("/{ip_lote}", response_model=PruebaMetalurgicaOut, status_code=status.HTTP_201_CREATED)
def registrar_prueba(
    ip_lote: str,
    datos: PruebaMetalurgicaCreate,
    current_user=Depends(check_permiso("PRUEBAS", "CREATE")),
    db: Session = Depends(get_db),
):
    try:
        prueba, warning = pruebas_service.registrar_prueba(db, ip_lote, datos, current_user.id)
        db.commit()
        response = PruebaMetalurgicaOut.model_validate(prueba)
        if warning:
            response.__pydantic_extra__ = {"warning": warning}
        return response
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e)) from e


# ── Etiquetado (nuevo) ────────────────────────────────────────────────────────


@router.post(
    "/{ip_lote}/etiquetar",
    response_model=EtiquetadoPruebaOut,
    status_code=status.HTTP_201_CREATED,
    summary="Genera CIP de recuperación para una prueba completada",
)
def etiquetar_prueba(
    ip_lote: str,
    current_user=Depends(check_permiso("PRUEBAS", "UPDATE")),
    db: Session = Depends(get_db),
):
    """
    Genera y asigna un CIP de recuperación a la prueba metalúrgica del lote.
    Solo disponible cuando la prueba tiene 48h completadas.
    Roles: TécnicoMuestreo, Admin.
    """
    try:
        resultado = pruebas_service.etiquetar_prueba(db, ip_lote, current_user.id)
        db.commit()
        return resultado
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e)) from e


# ── Pruebas listas para recuperación (nuevo) ─────────────────────────────────


@router.get(
    "/para-recuperacion",
    response_model=list[PruebaRecuperacionItem],
    summary="Pruebas completadas con ley planta disponible (listas para análisis de recuperación)",
)
def pruebas_para_recuperacion(
    current_user=Depends(check_permiso("PRUEBAS", "VIEW")),
    db: Session = Depends(get_db),
):
    """
    Retorna pruebas COMPLETADO + CIP asignado + ley_cabeza pre-calculada.
    Usado por Laboratorio para pre-llenar el formulario de recuperación.
    Visible para Laboratorista, Comercial, Admin.
    """
    return pruebas_service.obtener_pruebas_para_recuperacion(db)


# ── Sync Offline ──────────────────────────────────────────────────────────────


@router.post("/sync", response_model=SyncPruebasResponse)
def sync_pruebas(
    payload: SyncPruebasRequest,
    current_user=Depends(check_permiso("PRUEBAS", "CREATE")),
    db: Session = Depends(get_db),
):
    """Sincroniza pruebas registradas offline."""
    return pruebas_service.sync_batch(db, payload.pruebas, current_user.id)
