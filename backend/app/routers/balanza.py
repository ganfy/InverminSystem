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
from app.core.deps import check_permiso, get_current_user
from app.models.models import Usuario
from app.schemas.balanza import (
    DatosExtraidos,
    DocumentoRespuesta,
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
from app.schemas.balanza_offline import (
    BloqueIPRespuesta,
    CacheProvacopsRespuesta,
    SyncBatchRequest,
    SyncBatchRespuesta,
)
from app.services import balanza as svc
from app.services import balanza_documentos as doc_svc
from app.services import balanza_offline as offline_svc
from app.services import balanza_pdf as pdf_svc
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse
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
# DOCUMENTOS DE SESIÓN
# =============================================================================
@router.post("/documentos/extraer-preview", response_model=DatosExtraidos)
async def extraer_datos_preview(
    archivos: list[UploadFile] = File(...),
    current_user=Depends(check_permiso("BALANZA", "READ")),
):
    """Extrae datos de archivos sin sesión — para pre-llenar el form de registro."""
    try:
        return doc_svc.extraer_datos_archivos_directos(archivos)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post(
    "/{sesion_id}/documentos",
    response_model=DocumentoRespuesta,
    status_code=status.HTTP_201_CREATED,
)
async def subir_documento(
    sesion_id: int,
    archivo: UploadFile = File(...),
    tipo_documento: str = Form(...),
    current_user=Depends(check_permiso("BALANZA", "CREATE")),
    db: Session = Depends(get_db),
):
    """
    Adjunta un documento (PDF o imagen) a una sesión.
    tipo_documento: GUIA_REMISION | GUIA_TRANSPORTE | LICENCIA_CONDUCIR | OTRO
    """
    try:
        doc = doc_svc.subir_documento(
            db, sesion_id, archivo, tipo_documento, usuario_id=current_user.id
        )
        db.commit()
        return doc
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.get(
    "/{sesion_id}/documentos",
    response_model=list[DocumentoRespuesta],
)
def listar_documentos(
    sesion_id: int,
    current_user=Depends(check_permiso("BALANZA", "READ")),
    db: Session = Depends(get_db),
):
    """Lista todos los documentos adjuntos a una sesión."""
    return doc_svc.listar_documentos(db, sesion_id)


@router.get("/{sesion_id}/documentos/{doc_id}/download")
def descargar_documento(
    sesion_id: int,
    doc_id: int,
    current_user=Depends(check_permiso("BALANZA", "READ")),
    db: Session = Depends(get_db),
):
    """Descarga el archivo de un documento adjunto."""
    try:
        ruta, nombre = doc_svc.obtener_archivo(db, sesion_id, doc_id)
        return FileResponse(
            path=str(ruta),
            filename=nombre,
            media_type="application/octet-stream",
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.delete(
    "/{sesion_id}/documentos/{doc_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def eliminar_documento(
    sesion_id: int,
    doc_id: int,
    current_user=Depends(check_permiso("BALANZA", "DELETE")),
    db: Session = Depends(get_db),
):
    """
    Elimina un documento adjunto (solo Admin y Gerencia — RBAC).
    Borra el archivo de disco y el registro de BD.
    """
    try:
        doc_svc.eliminar_documento(db, sesion_id, doc_id)
        db.commit()
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.post(
    "/{sesion_id}/documentos/extraer",
    response_model=DatosExtraidos,
)
def extraer_datos(
    sesion_id: int,
    current_user=Depends(check_permiso("BALANZA", "READ")),
    db: Session = Depends(get_db),
):
    """
    Analiza todos los documentos adjuntos con Claude API y extrae
    datos estructurados (placa, conductor, guías, etc.) para pre-llenar
    los campos de la sesión.
    """
    try:
        return doc_svc.extraer_datos_documentos(db, sesion_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en extracción: {str(e)}",
        ) from e


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


# =============================================================================
# MODO OFFLINE — ENDPOINTS AUXILIARES PARA FRONTEND
# =============================================================================

# ── RF-BAL-005: Reserva de bloque IP ──────────────────────


@router.post(
    "/offline/ip-range",
    response_model=BloqueIPRespuesta,
    summary="Reservar bloque de IPs para operación offline",
)
def reservar_bloque_ip(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Reserva un bloque de IPs consecutivos para que el dispositivo
    pueda asignarlos offline sin colisiones.

    El tamaño del bloque se lee de configuracion.tamano_bloque_ip (default 50).
    Se llama automáticamente al iniciar sesión o al sincronizar.
    """
    return offline_svc.reservar_bloque_ip(db)


# ── RF-BAL-005: Caché de provacops ─────────────────────────


@router.get(
    "/offline/provacops",
    response_model=CacheProvacopsRespuesta,
    summary="Obtener caché de relaciones proveedor-acopiador para uso offline",
)
def obtener_cache_provacops(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Devuelve todas las relaciones proveedor-acopiador activas.
    El frontend las almacena en IndexedDB para validar offline.
    Se debe llamar en cada login y al sincronizar.
    """
    from datetime import UTC, datetime

    items = offline_svc.obtener_cache_provacops(db)
    return CacheProvacopsRespuesta(
        total=len(items),
        items=items,
        ts_servidor=datetime.now(UTC).isoformat(),
    )


# ── RF-BAL-005: Sync batch ─────────────────────────────────


@router.post(
    "/offline/sync",
    response_model=SyncBatchRespuesta,
    summary="Sincronizar sesiones y lotes creados offline",
)
def sincronizar_batch(
    payload: SyncBatchRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Recibe el batch de sesiones+lotes creados offline y los persiste.

    - Idempotente: re-enviar el mismo batch no duplica datos.
    - Nunca aborta el batch completo por un error individual.
    - Retorna el resultado item por item con el server_id asignado
      para que el frontend actualice su IndexedDB local.

    Orden interno de procesamiento: sesiones → lotes → pesajes.
    """
    return offline_svc.sincronizar_batch(db, payload, current_user.id)
