from app.core.database import get_db
from app.core.deps import check_permiso
from app.schemas.pruebas import (
    EtiquetadoPruebaOut,
    EtiquetarPruebaRequest,
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
    return pruebas_service.obtener_lista_pruebas(db)


# IMPORTANTE: rutas estáticas ANTES de /{ip_lote} para que FastAPI no las capture como param
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
    Retorna pruebas COMPLETADO + CIP interno + ley_cabeza calculada.
    Solo aparecen si el lote ya tiene análisis de ley vigentes (ley planta calculable).
    Usado por Comercial para crear el registro pendiente en laboratorio.
    """
    return pruebas_service.obtener_pruebas_para_recuperacion(db)


@router.post("/sync", response_model=SyncPruebasResponse)
def sync_pruebas(
    payload: SyncPruebasRequest,
    current_user=Depends(check_permiso("PRUEBAS", "CREATE")),
    db: Session = Depends(get_db),
):
    return pruebas_service.sync_batch(db, payload.pruebas, current_user.id)


# ── Rutas con path param ──────────────────────────────────────────────────────


@router.get("/{ip_lote}", response_model=PruebaMetalurgicaOut)
def obtener_detalle_prueba(
    ip_lote: str,
    current_user=Depends(check_permiso("PRUEBAS", "VIEW")),
    db: Session = Depends(get_db),
):
    from app.models.enums import TipoMuestra
    from app.models.models import MapeoCIP

    prueba = pruebas_service.obtener_prueba_por_ip(db, ip_lote)
    if not prueba:
        raise HTTPException(status_code=404, detail="No hay prueba metalúrgica para este lote")

    out = PruebaMetalurgicaOut.model_validate(prueba)
    # Poblar CIPs de recuperación desde mapeo_cip (el modelo ya no tiene columna cip)
    cips_rec = (
        db.query(MapeoCIP)
        .filter(
            MapeoCIP.lote_id == prueba.lote_id,
            MapeoCIP.tipo_muestra.in_(
                [
                    TipoMuestra.RECUPERACION_INTERNO,
                    TipoMuestra.RECUPERACION_EXTERNO,
                ]
            ),
        )
        .order_by(MapeoCIP.id)
        .all()
    )
    out.cips_recuperacion = [c.codigo_cip for c in cips_rec]
    return out


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


@router.post(
    "/{ip_lote}/etiquetar",
    response_model=EtiquetadoPruebaOut,
    status_code=status.HTTP_201_CREATED,
    summary="Genera CIP de recuperación para una prueba completada",
)
def etiquetar_prueba(
    ip_lote: str,
    datos: EtiquetarPruebaRequest = EtiquetarPruebaRequest(),
    current_user=Depends(check_permiso("PRUEBAS", "UPDATE")),
    db: Session = Depends(get_db),
):
    """
    Genera un CIP de recuperación. Puede llamarse múltiples veces
    para generar CIPs adicionales (ej: interno + externo).
    tipo: RecuperacionInterno (default) | RecuperacionExterno
    """
    try:
        resultado = pruebas_service.etiquetar_prueba(db, ip_lote, current_user.id, tipo=datos.tipo)
        db.commit()
        return resultado
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e)) from e
