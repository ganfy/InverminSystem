"""
Permisos RBAC (desde seed.py):
  LABORATORIO VIEW   → Laboratorista, Comercial, Gerencia, Admin
  LABORATORIO CREATE → Laboratorista, Comercial, Admin
  LABORATORIO UPDATE → Comercial, Admin  (certificados)
  LABORATORIO DELETE → Comercial, Gerencia, Admin  (descartar)

Separación de vistas:
  GET /laboratorio/cips           → Laboratorista/todos (no incluye IP por defecto)
  GET /laboratorio/lotes          → Comercial+ (incluye IP, organizado por lote)
  GET /laboratorio/lotes/{ip}     → Comercial+ (detalle completo por lote)
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
    DescartarRequest,
    LoteLabOut,
    SyncLaboratorioRequest,
    SyncLaboratorioResponse,
)
from app.services import laboratorio as svc
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

router = APIRouter(prefix="/laboratorio", tags=["Laboratorio"])

_ROLES_COMERCIAL = {RolSistema.ADMIN, RolSistema.GERENCIA, RolSistema.COMERCIAL}


def _puede_ver_ip(current_user) -> bool:
    """Determina si el rol del usuario puede ver IPs (confidencialidad CIP)."""
    rol = current_user.rol.codigo if current_user.rol else None
    return rol in {r.value for r in _ROLES_COMERCIAL}


# ── Vista por CIP (Laboratorista y Comercial) ────────────────────────────────


@router.get("/cips", response_model=list[CIPAnalisisOut])
def listar_cips(
    current_user=Depends(check_permiso("LABORATORIO", "VIEW")),
    db: Session = Depends(get_db),
):
    """
    Lista todos los CIPs generados con su estado de análisis.
    Laboratorista: no recibe IPs (confidencialidad muestreo ciego).
    Comercial/Gerencia/Admin: recibe lote_ip en cada CIP.
    """
    incluir_ip = _puede_ver_ip(current_user)
    return svc.obtener_cips_laboratorio(db, incluir_ip=incluir_ip)


# ── Vista por Lote/IP (solo Comercial, Gerencia, Admin) ──────────────────────


@router.get("/lotes", response_model=list[LoteLabOut])
def listar_lotes(
    current_user=Depends(check_permiso("LABORATORIO", "UPDATE")),
    db: Session = Depends(get_db),
):
    """Lista lotes con análisis. Solo Comercial/Gerencia/Admin (ven IPs)."""
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
    Registra un análisis de ley (Fire Assay triple sampling) para un CIP.
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
    """
    Descarta/invalida un análisis de ley. Requiere justificación.
    Comercial lo usa para solicitar remuestreo al marcar como descartado.
    """
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
    """Adjunta el PDF/imagen del certificado a un análisis de ley. Solo Comercial+."""
    try:
        url = svc.subir_certificado(db, analisis_id, archivo, tipo="ley")
        db.commit()
        return {"certificado_url": url}
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e)) from e


# ── Registrar Análisis de Recuperación ───────────────────────────────────────


@router.post("/recuperacion", response_model=AnalisisRecuperacionOut, status_code=201)
def registrar_recuperacion(
    datos: AnalisisRecuperacionCreate,
    current_user=Depends(check_permiso("LABORATORIO", "CREATE")),
    db: Session = Depends(get_db),
):
    """Registra un análisis de recuperación (Prueba de Botella) para un CIP."""
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
    """Descarta un análisis de recuperación. Comercial/Gerencia/Admin."""
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
    """Adjunta certificado a un análisis de recuperación. Solo Comercial+."""
    try:
        url = svc.subir_certificado(db, analisis_id, archivo, tipo="recuperacion")
        db.commit()
        return {"certificado_url": url}
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e)) from e


# ── Sync Offline ─────────────────────────────────────────────────────────────


@router.post("/sync", response_model=SyncLaboratorioResponse)
def sync_batch(
    payload: SyncLaboratorioRequest,
    current_user=Depends(check_permiso("LABORATORIO", "CREATE")),
    db: Session = Depends(get_db),
):
    """Sincroniza análisis registrados offline desde tablet de laboratorio."""
    return svc.sincronizar_batch(db, payload, current_user.id)
