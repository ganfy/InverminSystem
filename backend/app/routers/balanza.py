"""
Router — Módulo Balanza
Endpoints para sesiones de descarga, lotes, y tickets PDF.

Permisos (RBAC del documento):
  - Crear sesión / Editar lote   → Admin, OperadorBalanza
  - Eliminar lote (soft delete)  → Admin, Gerencia, Comercial
  - Ver tickets                  → Admin, Gerencia, Comercial, OperadorBalanza
  - Ver lotes eliminados         → Admin, Gerencia, Comercial
"""

from app.core.database import get_db
from app.core.deps import check_permiso
from app.schemas.balanza import (
    EliminarLoteRequest,
    LoteCrear,
    LoteDetalle,
    LoteEditar,
    ProvAcopDropdown,
    SesionCrear,
    SesionDetalle,
    SesionEditar,
    SesionLista,
)
from app.services import balanza as svc
from app.services import balanza_pdf as pdf_svc
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import HTMLResponse, StreamingResponse
from sqlalchemy.orm import Session

router = APIRouter(prefix="/balanza", tags=["Balanza"])


# =============================================================================
# PROVEEDORES-ACOPIADORES (autocomplete en formulario nueva sesión)
# =============================================================================


@router.get("/provacop", response_model=list[ProvAcopDropdown])
def listar_provacop(
    busqueda: str | None = Query(None, description="Filtrar por razón social proveedor"),
    current_user=Depends(check_permiso("BALANZA", "CREATE")),
    db: Session = Depends(get_db),
):
    """
    Lista relaciones proveedor-acopiador activas para el autocomplete
    del formulario de nueva sesión.
    """
    return svc.listar_provacop_activos(db, busqueda=busqueda)


# =============================================================================
# SESIONES
# =============================================================================


@router.get("", response_model=list[SesionLista])
def listar_sesiones(
    estado: str | None = Query(None, description="EN_PROCESO | COMPLETO | PAUSADO"),
    fecha_desde: str | None = Query(None, description="ISO 8601: 2026-01-05T00:00:00"),
    fecha_hasta: str | None = Query(None, description="ISO 8601: 2026-01-05T23:59:59"),
    busqueda: str | None = Query(None, description="IP, proveedor, placa, GRE"),
    current_user=Depends(check_permiso("BALANZA", "VIEW")),
    db: Session = Depends(get_db),
):
    """Lista de sesiones con filtros. Orden: más reciente primero."""
    from datetime import datetime

    fecha_desde_dt = datetime.fromisoformat(fecha_desde) if fecha_desde else None
    fecha_hasta_dt = datetime.fromisoformat(fecha_hasta) if fecha_hasta else None

    return svc.listar_sesiones(
        db,
        estado=estado,
        fecha_desde=fecha_desde_dt,
        fecha_hasta=fecha_hasta_dt,
        busqueda=busqueda,
    )


@router.post("", response_model=SesionDetalle, status_code=status.HTTP_201_CREATED)
def crear_sesion(
    datos: SesionCrear,
    current_user=Depends(check_permiso("BALANZA", "CREATE")),
    db: Session = Depends(get_db),
):
    """
    Crea una nueva sesión de descarga EN_PROCESO (RF-BAL-001).
    Múltiples sesiones pueden estar abiertas en paralelo.
    """
    try:
        sesion = svc.crear_sesion(db, datos, usuario_id=current_user.id)
        db.commit()
        return sesion
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.get("/{sesion_id}", response_model=SesionDetalle)
def obtener_sesion(
    sesion_id: int,
    current_user=Depends(check_permiso("BALANZA", "VIEW")),
    db: Session = Depends(get_db),
):
    """Detalle completo de sesión: datos de transporte + lista de lotes."""
    try:
        return svc.obtener_sesion(db, sesion_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.patch("/{sesion_id}", response_model=SesionDetalle)
def editar_sesion(
    sesion_id: int,
    datos: SesionEditar,
    current_user=Depends(check_permiso("BALANZA", "UPDATE")),
    db: Session = Depends(get_db),
):
    """
    Edita la cabecera de una sesión: proveedor/acopiador y datos de transporte.
    PATCH parcial — solo se actualizan los campos enviados.
    Si provacop_id cambia, se valida que la relación exista.
    """
    try:
        sesion = svc.editar_sesion(db, sesion_id, datos, usuario_id=current_user.id)
        db.commit()
        return sesion
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.patch("/{sesion_id}/finalizar", response_model=SesionDetalle)
def finalizar_sesion(
    sesion_id: int,
    current_user=Depends(check_permiso("BALANZA", "UPDATE")),
    db: Session = Depends(get_db),
):
    """
    Marca la sesión como COMPLETO.
    Requiere al menos 1 lote activo. No reversible desde la UI.
    """
    try:
        sesion = svc.finalizar_sesion(db, sesion_id, usuario_id=current_user.id)
        db.commit()
        return sesion
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.patch("/{sesion_id}/pausar", response_model=SesionDetalle)
def pausar_sesion(
    sesion_id: int,
    current_user=Depends(check_permiso("BALANZA", "UPDATE")),
    db: Session = Depends(get_db),
):
    """Pausa una sesión EN_PROCESO (el camión regresa más tarde)."""
    try:
        sesion = svc.pausar_sesion(db, sesion_id, usuario_id=current_user.id)
        db.commit()
        return sesion
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.patch("/{sesion_id}/reanudar", response_model=SesionDetalle)
def reanudar_sesion(
    sesion_id: int,
    current_user=Depends(check_permiso("BALANZA", "UPDATE")),
    db: Session = Depends(get_db),
):
    """Reanuda una sesión PAUSADA → EN_PROCESO."""
    try:
        sesion = svc.reanudar_sesion(db, sesion_id, usuario_id=current_user.id)
        db.commit()
        return sesion
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


# =============================================================================
# LOTES
# =============================================================================


@router.post(
    "/{sesion_id}/lotes",
    response_model=LoteDetalle,
    status_code=status.HTTP_201_CREATED,
)
def agregar_lote(
    sesion_id: int,
    datos: LoteCrear,
    current_user=Depends(check_permiso("BALANZA", "CREATE")),
    db: Session = Depends(get_db),
):
    """
    Agrega un lote con pesaje a una sesión activa (RF-BAL-002).
    Genera IP secuencial automáticamente.
    Valida: peso_inicial > peso_final (bruto > tara).
    """
    try:
        lote = svc.agregar_lote(db, sesion_id, datos, usuario_id=current_user.id)
        db.commit()
        return lote
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.delete(
    "/{sesion_id}/lotes/{lote_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def eliminar_lote(
    sesion_id: int,
    lote_id: int,
    datos: EliminarLoteRequest,
    current_user=Depends(check_permiso("BALANZA", "DELETE")),
    db: Session = Depends(get_db),
):
    """
    Soft delete de lote con snapshot de auditoría (RF-BAL-004).
    Bloqueado si estado == PAGADO.
    Requiere motivo obligatorio.
    """
    try:
        svc.eliminar_lote(db, sesion_id, lote_id, datos, usuario_id=current_user.id)
        db.commit()
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.patch(
    "/{sesion_id}/lotes/{lote_id}",
    response_model=LoteDetalle,
)
def editar_lote(
    sesion_id: int,
    lote_id: int,
    datos: LoteEditar,
    current_user=Depends(check_permiso("BALANZA", "ADMIN")),  # solo Admin
    db: Session = Depends(get_db),
):
    """
    Admin: edita tipo_material y/o datos de pesaje de un lote.
    peso_neto se recalcula automáticamente (columna GENERATED en PG).
    """
    try:
        lote = svc.editar_lote(db, sesion_id, lote_id, datos, usuario_id=current_user.id)
        db.commit()
        return lote
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


# =============================================================================
# TICKET PDF  (RF-BAL-003)
# =============================================================================


@router.get("/{sesion_id}/lotes/{lote_id}/ticket")
def descargar_ticket(
    sesion_id: int,
    lote_id: int,
    current_user=Depends(check_permiso("BALANZA", "VIEW")),
    db: Session = Depends(get_db),
):
    """
    Genera y descarga el ticket PDF de un lote (RF-BAL-003).
    Formato A5 landscape con: IP, pesos, proveedor/acopiador, fecha.
    """
    try:
        pdf_bytes = pdf_svc.generar_ticket_pdf(db, sesion_id, lote_id)
        nombre = pdf_svc.nombre_archivo_ticket(db, lote_id)
        return StreamingResponse(
            iter([pdf_bytes]),
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{nombre}"'},
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e)) from e


@router.get("/{sesion_id}/tickets", summary="PDF con todos los tickets de la sesión")
def descargar_tickets_sesion(
    sesion_id: int,
    current_user=Depends(check_permiso("BALANZA", "VIEW")),
    db: Session = Depends(get_db),
):
    """
    Genera un único PDF con los tickets de todos los lotes activos de la sesión,
    ordenados por número de lote. Útil para entregar al transportista de una vez.
    """
    try:
        pdf_bytes = pdf_svc.generar_tickets_sesion_pdf(db, sesion_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    filename = pdf_svc.nombre_archivo_sesion(sesion_id)
    return StreamingResponse(
        iter([pdf_bytes]),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get(
    "/{sesion_id}/lotes/{lote_id}/ticket/preview",
    response_class=HTMLResponse,
    summary="Preview HTML del ticket (sin generar PDF)",
)
def preview_ticket(
    sesion_id: int,
    lote_id: int,
    current_user=Depends(check_permiso("BALANZA", "VIEW")),
    db: Session = Depends(get_db),
):
    """
    Devuelve el HTML del ticket para visualizar en el navegador.
    El cliente abre esta URL en una nueva pestaña — el usuario ve el ticket
    y puede imprimirlo con Ctrl+P o guardarlo desde el navegador.
    No genera ni almacena ningún archivo en el servidor.
    """
    try:
        html = pdf_svc.generar_ticket_html(db, sesion_id, lote_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return HTMLResponse(content=html)
