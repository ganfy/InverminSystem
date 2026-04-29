"""
Permisos RBAC (RF-SYS-001):
  LIQUIDACIONES VIEW   → Admin, Gerencia, Comercial
  LIQUIDACIONES CREATE → Admin, Gerencia, Comercial
  LIQUIDACIONES UPDATE → Admin, Gerencia, Comercial
"""

import io
import os

from app.core.database import get_db
from app.core.deps import check_permiso, get_current_user
from app.models.enums import RolSistema
from app.models.models import Liquidacion, Usuario
from app.schemas.liquidaciones import (
    CambiarEstadoRequest,
    LiquidacionCreate,
    LiquidacionDetalleOut,
    LiquidacionesKPIOut,
    LiquidacionEstadoUpdate,
    LiquidacionListItem,
    LiquidacionOut,
    LiquidacionPreviewOut,
    LiquidacionPreviewRequest,
    LiquidacionResumenOut,
    LoteLiquidableOut,
    ProvacoPSelectorOut,
)
from app.services import liquidaciones as svc
from app.services.liquidaciones_pdf import generar_liquidacion_pdf, guardar_pdf_liquidacion
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

router = APIRouter(prefix="/liquidaciones", tags=["Liquidaciones"])

_ROLES_COMERCIAL = {RolSistema.ADMIN, RolSistema.GERENCIA, RolSistema.COMERCIAL}


def _verificar_rol(user: Usuario) -> None:
    rol = user.rol.codigo if user.rol else None
    if rol not in {r.value for r in _ROLES_COMERCIAL}:
        raise HTTPException(status_code=403, detail="Sin permiso para gestionar liquidaciones")


# ── Lotes disponibles para liquidar ──────────────────────────────────────────


@router.get("/lotes-disponibles")
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


@router.get("/", response_model=list[LiquidacionResumenOut])
def listar(
    provacop_id: int | None = Query(None),
    estado: str | None = Query(None),
    current_user=Depends(check_permiso("LIQUIDACIONES", "VIEW")),
    db: Session = Depends(get_db),
):
    return svc.obtener_liquidaciones(db, provacop_id=provacop_id, estado=estado)


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

    result = svc.obtener_liquidacion(db, liq.id)
    return result


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

    # Intentar servir desde archivo guardado
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

    # Generar en el momento
    try:
        pdf_bytes = generar_liquidacion_pdf(db, liquidacion_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando PDF: {e}") from e

    nombre = f"Liquidacion_{liq_db.numero_liquidacion or liquidacion_id}.pdf"
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{nombre}"'},
    )


# ── KPIs ──────────────────────────────────────────────────────────────────────


@router.get("/kpis", response_model=LiquidacionesKPIOut)
def get_kpis(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    _verificar_rol(current_user)
    return svc.obtener_kpis(db)


# ── Selector provacops para wizard paso 1 ─────────────────────────────────────


@router.get("/provacops", response_model=list[ProvacoPSelectorOut])
def get_provacops_con_lotes(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Retorna relaciones proveedor-acopiador que tienen al menos 1 lote liquidable."""
    _verificar_rol(current_user)
    return svc.listar_provacops_con_lotes_liquidables(db)


# ── Lotes liquidables ─────────────────────────────────────────────────────────


@router.get("/lotes-liquidables", response_model=list[LoteLiquidableOut])
def get_lotes_liquidables(
    provacop_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Lotes con ley comercial + recuperación + TMS completos, listos para liquidar.
    Opcional: filtrar por provacop_id para el wizard paso 2.
    """
    _verificar_rol(current_user)
    return svc.listar_lotes_liquidables(db, provacop_id=provacop_id)


# ── Lista de liquidaciones ────────────────────────────────────────────────────


@router.get("", response_model=list[LiquidacionListItem])
def listar_liquidaciones(
    estado: str | None = None,
    provacop_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    _verificar_rol(current_user)
    return svc.listar_liquidaciones(db, estado=estado, provacop_id=provacop_id)


# ── Crear liquidación (BORRADOR) ──────────────────────────────────────────────


@router.post("", response_model=LiquidacionOut, status_code=status.HTTP_201_CREATED)
def crear_liquidacion(
    datos: LiquidacionCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Crea una nueva liquidación en estado BORRADOR con cálculos automáticos.
    RF-LIQ-003: todos los valores son calculados por el sistema.
    """
    _verificar_rol(current_user)
    return svc.crear_liquidacion(db, datos, current_user.id)


# ── Detalle de liquidación ────────────────────────────────────────────────────


@router.get("/{liquidacion_id}", response_model=LiquidacionOut)
def get_liquidacion(
    liquidacion_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    _verificar_rol(current_user)
    return svc.obtener_liquidacion(db, liquidacion_id)


# ── Cambiar estado ────────────────────────────────────────────────────────────


@router.patch("/{liquidacion_id}/estado", response_model=LiquidacionOut)
def cambiar_estado(
    liquidacion_id: int,
    body: CambiarEstadoRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Transiciones permitidas:
    BORRADOR → GENERADA (emite PDF y marca lotes como LIQUIDADO)
    GENERADA → FACTURADA
    FACTURADA → PAGADA (irreversible, RF-SYS-001 regla 5)
    """
    _verificar_rol(current_user)
    return svc.cambiar_estado(db, liquidacion_id, body.estado, current_user.id)


# ── Eliminar borrador ─────────────────────────────────────────────────────────


@router.delete("/{liquidacion_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_liquidacion(
    liquidacion_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Solo se pueden eliminar liquidaciones en estado BORRADOR."""
    _verificar_rol(current_user)
    svc.eliminar_liquidacion(db, liquidacion_id)
