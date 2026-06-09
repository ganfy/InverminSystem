"""
Permisos RBAC (RF-SYS-001):
  LIQUIDACIONES VIEW   → Admin, Gerencia, Comercial
  LIQUIDACIONES CREATE → Admin, Gerencia, Comercial
  LIQUIDACIONES UPDATE → Admin, Gerencia, Comercial
"""

import os

from app.core.database import get_db
from app.core.deps import check_permiso
from app.models.enums import RolSistema
from app.models.models import Liquidacion
from app.schemas.liquidaciones import (
    LiquidacionCreate,
    LiquidacionDetalleOut,
    LiquidacionesKPIOut,
    LiquidacionEstadoUpdate,
    LiquidacionLoteParamsUpdate,
    LiquidacionPreviewOut,
    LiquidacionPreviewRequest,
    LiquidacionResumenOut,
    LoteDisponible,
)
from app.services import liquidaciones as svc
from app.services.liquidaciones_ag import obtener_ultimo_valor_plata_noon
from app.services.liquidaciones_au import obtener_ultimo_valor_oro_pm
from app.services.liquidaciones_pdf import guardar_pdf_liquidacion
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

router = APIRouter(prefix="/liquidaciones", tags=["Liquidaciones"])

# Precio del oro para liquidaciones - se obtiene en tiempo real desde LBMA Fix (Gold PM) usando web scraping.


@router.get("/precio-oro", response_model=float | None)
def precio_oro(
    current_user=Depends(check_permiso("LIQUIDACIONES", "VIEW")),
):
    """Obtiene el último valor del Gold PM desde LBMA Fix. Retorna null si falla."""
    return obtener_ultimo_valor_oro_pm()


@router.get("/precio-plata", response_model=float | None)
def precio_plata(
    current_user=Depends(check_permiso("LIQUIDACIONES", "VIEW")),
):
    """Obtiene el último valor de Plata Noon Fix. Retorna null si falla."""
    return obtener_ultimo_valor_plata_noon()


# ── Lotes disponibles para liquidar ──────────────────────────────────────────


@router.get("/lotes-disponibles", response_model=list[LoteDisponible])
def lotes_disponibles(
    provacop_id: int = Query(...),
    current_user=Depends(check_permiso("LIQUIDACIONES", "VIEW")),
    db: Session = Depends(get_db),
):
    """
    Lista lotes en RECEPCIONADO del proveedor-acopiador listos para liquidar.
    Incluye flags de volado y alertas de vencimiento.
    """
    return svc.lotes_disponibles_para_liquidar(db, provacop_id)


# ── Preview (calculo sin guardar) ─────────────────────────────────────────────


@router.post("/preview", response_model=LiquidacionPreviewOut)
def preview(
    req: LiquidacionPreviewRequest,
    current_user=Depends(check_permiso("LIQUIDACIONES", "VIEW")),
    db: Session = Depends(get_db),
):
    """
    Calcula valores financieros de la liquidacion sin guardar.
    Usar antes de confirmar para mostrar tabla de preview al usuario.
    """
    try:
        return svc.preview_liquidacion(db, req)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e


# ── CRUD ──────────────────────────────────────────────────────────────────────


@router.get("/kpis", response_model=LiquidacionesKPIOut)
def kpis(
    current_user=Depends(check_permiso("LIQUIDACIONES", "VIEW")),
    db: Session = Depends(get_db),
):
    liquidaciones = svc.obtener_liquidaciones(db)
    borradores = sum(1 for liq in liquidaciones if liq.estado == "BORRADOR")
    generadas = sum(1 for liq in liquidaciones if liq.estado == "GENERADA")
    pendiente = sum(
        float(liq.total_usd) for liq in liquidaciones if liq.estado in ("GENERADA", "FACTURADA")
    )
    # lotes liquidables: count across all provacops — costoso, cachear en producción
    from app.models.models import SesionDescarga

    provacop_ids = [row[0] for row in db.query(SesionDescarga.provacop_id).distinct()]
    lotes_liq = sum(
        sum(
            1
            for lot in svc.lotes_disponibles_para_liquidar(db, pid)
            if lot.get("listo_para_liquidar")
        )
        for pid in provacop_ids
    )

    return LiquidacionesKPIOut(
        borradores=borradores,
        generadas=generadas,
        lotes_liquidables=lotes_liq,
        valor_pendiente_usd=round(pendiente, 2),
    )


@router.get("/", response_model=list[LiquidacionResumenOut])
def listar(
    provacop_id: int | None = Query(None),
    estado: str | None = Query(None),
    current_user=Depends(check_permiso("LIQUIDACIONES", "VIEW")),
    db: Session = Depends(get_db),
):
    return svc.obtener_liquidaciones(db, provacop_id=provacop_id, estado=estado)


@router.post("/", response_model=LiquidacionDetalleOut, status_code=201)
def crear(
    req: LiquidacionCreate,
    current_user=Depends(check_permiso("LIQUIDACIONES", "CREATE")),
    db: Session = Depends(get_db),
):
    """
    Crea la liquidacion, genera snapshot financiero y actualiza estado de lotes a LIQUIDADO.
    Genera PDF automaticamente y lo guarda en disco.
    """
    try:
        liq = svc.crear_liquidacion(db, req, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e

    # Generar PDF y guardar ruta
    try:
        storage = os.getenv("STORAGE_PATH", "storage")
        ruta_pdf = guardar_pdf_liquidacion(db, liq.id, storage)
        liq.pdf_url = ruta_pdf
        db.commit()
        db.refresh(liq)
    except Exception:
        pass  # PDF falla silenciosamente - se puede regenerar

    return svc.obtener_liquidacion(db, liq.id)


@router.patch("/{liquidacion_id}/estado", response_model=LiquidacionDetalleOut)
def cambiar_estado(
    liquidacion_id: int,
    body: LiquidacionEstadoUpdate,
    current_user=Depends(check_permiso("LIQUIDACIONES", "UPDATE")),
    db: Session = Depends(get_db),
):
    """Cambia el estado de la liquidacion (GENERADA → FACTURADA → PAGADA)."""
    try:
        liq = svc.cambiar_estado(db, liquidacion_id, body.estado, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    return svc.obtener_liquidacion(db, liq.id)


@router.post("/{liquidacion_id}/emitir", response_model=LiquidacionDetalleOut)
def emitir(
    liquidacion_id: int,
    current_user=Depends(check_permiso("LIQUIDACIONES", "UPDATE")),
    db: Session = Depends(get_db),
):
    """Emite un borrador: BORRADOR → GENERADA, actualiza lotes y genera PDF."""
    try:
        liq = svc.emitir_liquidacion(db, liquidacion_id, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e

    try:
        storage = os.getenv("STORAGE_PATH", "storage")
        ruta_pdf = guardar_pdf_liquidacion(db, liq.id, storage)
        liq.pdf_url = ruta_pdf
        db.commit()
        db.refresh(liq)
    except Exception:
        pass

    return svc.obtener_liquidacion(db, liq.id)


# ── PDF ───────────────────────────────────────────────────────────────────────


@router.get("/{liquidacion_id}/pdf")
def descargar_pdf(
    liquidacion_id: int,
    current_user=Depends(check_permiso("LIQUIDACIONES", "VIEW")),
    db: Session = Depends(get_db),
):
    """Descarga el PDF de liquidacion. Si no existe lo genera en el momento."""
    liq_db = db.query(Liquidacion).filter(Liquidacion.id == liquidacion_id).first()
    if not liq_db:
        raise HTTPException(status_code=404, detail="Liquidacion no encontrada")

    if liq_db.pdf_url and os.path.exists(liq_db.pdf_url):

        def iterfile():
            with open(liq_db.pdf_url, "rb") as f:
                yield from f

        nombre = f"Liquidacion_{liq_db.numero_liquidacion}.pdf"
        return StreamingResponse(
            iterfile(),
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{nombre}"'},
        )

    try:
        storage = os.getenv("STORAGE_PATH", "storage")
        ruta_pdf = guardar_pdf_liquidacion(db, liquidacion_id, storage)
        liq_db.pdf_url = ruta_pdf
        db.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando PDF: {e}") from e

    nombre = f"Liquidacion_{liq_db.numero_liquidacion or liquidacion_id}.pdf"

    def iterfile():
        with open(liq_db.pdf_url, "rb") as f:
            yield from f

    return StreamingResponse(
        iterfile(),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{nombre}"'},
    )


@router.patch(
    "/{liquidacion_id}/lotes/{ip}/parametros",
    response_model=LiquidacionDetalleOut,
    summary="Admin/Gerencia editan parámetros de un lote en la liquidación",
)
def editar_params_lote(
    liquidacion_id: int,
    ip: str,
    body: LiquidacionLoteParamsUpdate,
    current_user=Depends(check_permiso("LIQUIDACIONES", "UPDATE")),
    db: Session = Depends(get_db),
):
    rol = current_user.rol.codigo if current_user.rol else None
    if rol not in {RolSistema.ADMIN.value, RolSistema.GERENCIA.value}:
        raise HTTPException(
            status_code=403, detail="Solo Admin y Gerencia pueden editar parámetros"
        )
    try:
        svc.editar_params_lote(db, liquidacion_id, ip, body, current_user.id)
        db.commit()
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=422, detail=str(e)) from e

    # Regenerar PDF con nuevos valores
    try:
        storage = os.getenv("STORAGE_PATH", "storage")
        ruta_pdf = guardar_pdf_liquidacion(db, liquidacion_id, storage)
        liq_db = db.query(Liquidacion).filter(Liquidacion.id == liquidacion_id).first()
        liq_db.pdf_url = ruta_pdf
        db.commit()
    except Exception:
        pass  # PDF falla silenciosamente

    return svc.obtener_liquidacion(db, liquidacion_id)


@router.get("/{liquidacion_id}", response_model=LiquidacionDetalleOut)
def detalle(
    liquidacion_id: int,
    current_user=Depends(check_permiso("LIQUIDACIONES", "VIEW")),
    db: Session = Depends(get_db),
):
    result = svc.obtener_liquidacion(db, liquidacion_id)
    if not result:
        raise HTTPException(status_code=404, detail="Liquidacion no encontrada")
    return result
