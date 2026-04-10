"""
Permisos RBAC (desde seed.py):
  LABORATORIO VIEW   → Laboratorista, Comercial, Gerencia, Admin
  LABORATORIO CREATE → Laboratorista, Comercial, Admin
  LABORATORIO UPDATE → Comercial, Admin  (certificados, completar pendientes, enviar a recuperación)
  LABORATORIO DELETE → Comercial, Gerencia, Admin  (descartar)

Separación de vistas:
  GET /laboratorio/cips           → Laboratorista/todos (no incluye IP por defecto)
  GET /laboratorio/lotes          → Comercial+ (incluye IP, organizado por lote)
  GET /laboratorio/lotes/{ip}     → Comercial+ (detalle completo por lote)

Flujo de recuperación interna:
  POST /laboratorio/lotes/{ip}/enviar-recuperacion  → Comercial crea PENDIENTE con snapshot ley_cabeza
  PATCH /laboratorio/recuperacion/{id}/completar    → Laboratorista ingresa ley_cola + ley_liquido
"""

from app.core.database import get_db
from app.core.deps import check_permiso
from app.models.enums import RolSistema
from app.models.models import Lote
from app.schemas.laboratorio import (
    AnalisisLeyCreate,
    AnalisisLeyOut,
    AnalisisRecuperacionCreate,
    AnalisisRecuperacionOut,
    CIPAnalisisOut,
    CompletarRecuperacionRequest,
    DescartarRequest,
    EnviarRecuperacionInternaRequest,
    LoteLabOut,
    SyncLaboratorioRequest,
    SyncLaboratorioResponse,
)
from app.services import laboratorio as svc
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi import UploadFile as FastAPIFile
from sqlalchemy.orm import Session

router = APIRouter(prefix="/laboratorio", tags=["Laboratorio"])

_ROLES_COMERCIAL = {RolSistema.ADMIN, RolSistema.GERENCIA, RolSistema.COMERCIAL}


def _puede_ver_ip(current_user) -> bool:
    rol = current_user.rol.codigo if current_user.rol else None
    return rol in {r.value for r in _ROLES_COMERCIAL}


# ── Vista por CIP (Laboratorista y Comercial) ────────────────────────────────


@router.get("/cips", response_model=list[CIPAnalisisOut])
def listar_cips(
    current_user=Depends(check_permiso("LABORATORIO", "VIEW")),
    db: Session = Depends(get_db),
):
    """
    Lista todos los CIPs con su estado de análisis.
    Laboratorista: no recibe IPs (confidencialidad muestreo ciego).
    Comercial/Gerencia/Admin: recibe lote_ip en cada CIP.
    CIPs de recuperación PENDIENTE aparecen destacados para laboratorista.
    """
    incluir_ip = _puede_ver_ip(current_user)
    return svc.obtener_cips_laboratorio(db, incluir_ip=incluir_ip)


# ── Vista por Lote/IP (solo Comercial, Gerencia, Admin) ──────────────────────


@router.get("/lotes", response_model=list[LoteLabOut])
def listar_lotes(
    current_user=Depends(check_permiso("LABORATORIO", "UPDATE")),
    db: Session = Depends(get_db),
):
    """Lista lotes con análisis. Incluye ley_planta y ley_minero calculados. Solo Comercial+."""
    return svc.obtener_lotes_laboratorio(db)


@router.get("/lotes/{ip}", response_model=LoteLabOut)
def detalle_lote(
    ip: str,
    current_user=Depends(check_permiso("LABORATORIO", "UPDATE")),
    db: Session = Depends(get_db),
):
    """Detalle completo de un lote: todos sus análisis, vigentes y descartados."""
    result = svc.obtener_detalle_lote(db, ip)
    if not result:
        raise HTTPException(status_code=404, detail=f"Lote {ip} no encontrado o sin CIPs")
    return result


# ── Registrar Análisis de Ley ────────────────────────────────────────────────


@router.post("/ley", response_model=AnalisisLeyOut, status_code=201)
def registrar_ley(
    datos: AnalisisLeyCreate,
    current_user=Depends(check_permiso("LABORATORIO", "CREATE")),
    db: Session = Depends(get_db),
):
    """
    Registra un análisis de ley (Fire Assay triple sampling) para un CIP tipo Laboratorio.
    Accesible por Laboratorista y Comercial.
    """
    try:
        nuevo = svc.registrar_analisis_ley(db, datos, usuario_id=current_user.id)
        db.commit()
        lote = db.query(Lote).filter(Lote.id == nuevo.lote_id).first()
        ip = lote.ip if lote else None
        return svc._ley_out(nuevo, ip)
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.patch("/ley/{analisis_id}/descartar", response_model=AnalisisLeyOut)
def descartar_ley(
    analisis_id: int,
    datos: DescartarRequest,
    current_user=Depends(check_permiso("LABORATORIO", "DELETE")),
    db: Session = Depends(get_db),
):
    try:
        resultado = svc.descartar_analisis_ley(
            db, analisis_id, datos.justificacion, current_user.id
        )
        db.commit()
        return svc._ley_out(resultado)
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.post("/ley/{analisis_id}/certificado")
async def subir_certificado_ley(
    analisis_id: int,
    archivo: UploadFile = File(...),
    current_user=Depends(check_permiso("LABORATORIO", "UPDATE")),
    db: Session = Depends(get_db),
):
    try:
        url = svc.subir_certificado(db, analisis_id, archivo, tipo="ley")
        db.commit()
        return {"certificado_url": url}
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e)) from e


# ── Flujo de recuperación interna ────────────────────────────────────────────


@router.post(
    "/lotes/{ip}/enviar-recuperacion",
    response_model=AnalisisRecuperacionOut,
    status_code=201,
    summary="Comercial crea registro PENDIENTE de recuperación para laboratorio interno",
)
def enviar_recuperacion_interna(
    ip: str,
    datos: EnviarRecuperacionInternaRequest = EnviarRecuperacionInternaRequest(),
    current_user=Depends(check_permiso("LABORATORIO", "UPDATE")),
    db: Session = Depends(get_db),
):
    """
    Crea un análisis de recuperación en estado PENDIENTE.
    - Snapshot de ley_cabeza = ley planta calculada en este momento.
    - El laboratorista lo completa con ley_cola y ley_liquido.
    - Requiere que el lote tenga CIPs de RecuperacionInterno y análisis de ley vigentes.
    Solo Comercial/Gerencia/Admin.
    """
    try:
        nuevo = svc.enviar_recuperacion_interna(db, ip, datos, current_user.id)
        db.commit()
        lote = db.query(Lote).filter(Lote.id == nuevo.lote_id).first()
        ip_lote = lote.ip if lote else None
        return svc._rec_out(nuevo, ip_lote)
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.patch(
    "/recuperacion/{analisis_id}/completar",
    response_model=AnalisisRecuperacionOut,
    summary="Laboratorista completa un análisis de recuperación PENDIENTE",
)
def completar_recuperacion(
    analisis_id: int,
    datos: CompletarRecuperacionRequest,
    current_user=Depends(check_permiso("LABORATORIO", "UPDATE")),
    db: Session = Depends(get_db),
):
    """
    Ingresa ley_cola y ley_liquido en un análisis PENDIENTE.
    La recuperación se calcula automáticamente.
    Accesible por Laboratorista, Comercial, Admin.
    """
    try:
        resultado = svc.completar_recuperacion(db, analisis_id, datos, current_user.id)
        db.commit()
        return svc._rec_out(resultado)
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e)) from e


# ── Registro directo de recuperación (flujo externo / sin pending) ────────────


@router.post("/recuperacion", response_model=AnalisisRecuperacionOut, status_code=201)
def registrar_recuperacion(
    datos: AnalisisRecuperacionCreate,
    current_user=Depends(check_permiso("LABORATORIO", "CREATE")),
    db: Session = Depends(get_db),
):
    """
    Registro directo COMPLETADO de recuperación (sin pending previo).
    Usado para: certificados de laboratorio externo donde Comercial ingresa todos los datos.
    El CIP debe ser de tipo RecuperacionExterno o RecuperacionInterno.
    """
    try:
        nuevo = svc.registrar_analisis_recuperacion(db, datos, usuario_id=current_user.id)
        db.commit()
        lote = db.query(Lote).filter(Lote.id == nuevo.lote_id).first()
        ip = lote.ip if lote else None
        return svc._rec_out(nuevo, ip)
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.patch("/recuperacion/{analisis_id}/descartar", response_model=AnalisisRecuperacionOut)
def descartar_recuperacion(
    analisis_id: int,
    datos: DescartarRequest,
    current_user=Depends(check_permiso("LABORATORIO", "DELETE")),
    db: Session = Depends(get_db),
):
    try:
        resultado = svc.descartar_analisis_recuperacion(
            db, analisis_id, datos.justificacion, current_user.id
        )
        db.commit()
        return svc._rec_out(resultado)
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.post("/recuperacion/{analisis_id}/certificado")
async def subir_certificado_recuperacion(
    analisis_id: int,
    archivo: UploadFile = File(...),
    current_user=Depends(check_permiso("LABORATORIO", "UPDATE")),
    db: Session = Depends(get_db),
):
    try:
        url = svc.subir_certificado(db, analisis_id, archivo, tipo="recuperacion")
        db.commit()
        return {"certificado_url": url}
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post("/certificado/extraer-ley")
async def extraer_certificado_ley(
    archivo: UploadFile = FastAPIFile(...),
    current_user=Depends(check_permiso("LABORATORIO", "CREATE")),
):
    """OCR de certificado PDF → devuelve campos pre-llenados para análisis de ley."""
    contenido = await archivo.read()
    resultado = svc.extraer_certificado_ley(contenido, archivo.filename or "cert.pdf")
    return resultado


@router.post("/certificado/extraer-recuperacion")
async def extraer_certificado_recuperacion(
    archivo: UploadFile = FastAPIFile(...),
    current_user=Depends(check_permiso("LABORATORIO", "CREATE")),
):
    """OCR de certificado PDF → devuelve campos pre-llenados para análisis de recuperación."""
    contenido = await archivo.read()
    resultado = svc.extraer_certificado_recuperacion(contenido, archivo.filename or "cert.pdf")
    return resultado


# ── Sync Offline ─────────────────────────────────────────────────────────────


@router.post("/sync", response_model=SyncLaboratorioResponse)
def sync_batch(
    payload: SyncLaboratorioRequest,
    current_user=Depends(check_permiso("LABORATORIO", "CREATE")),
    db: Session = Depends(get_db),
):
    """Sincroniza análisis registrados offline desde tablet de laboratorio."""
    return svc.sincronizar_batch(db, payload, current_user.id)
