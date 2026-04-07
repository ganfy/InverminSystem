from app.core.database import get_db
from app.core.deps import check_permiso
from app.schemas.laboratorio import (
    AnalisisLeyCreate,
    AnalisisLeyOut,
    AnalisisRecuperacionCreate,
    AnalisisRecuperacionOut,
    MuestraLaboratorioItem,
    SyncLaboratorioRequest,
)
from app.services import laboratorio as svc
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

router = APIRouter(prefix="/laboratorio", tags=["Laboratorio"])

# --- ANÁLISIS DE LEY ---


@router.post("/ley", response_model=AnalisisLeyOut, status_code=status.HTTP_201_CREATED)
def registrar_analisis_ley(
    datos: AnalisisLeyCreate,
    current_user=Depends(check_permiso("LABORATORIO", "CREATE")),
    db: Session = Depends(get_db),
):
    """Registra un análisis de Ley (Fire Assay) para un código CIP."""
    try:
        resultado = svc.registrar_analisis_ley(db, datos, usuario_id=current_user.id)
        return resultado
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.post("/ley/{analisis_id}/certificado")
def subir_certificado_ley(
    analisis_id: int,
    archivo: UploadFile = File(...),
    current_user=Depends(check_permiso("LABORATORIO", "UPDATE")),
    db: Session = Depends(get_db),
):
    """Sube el certificado en PDF/Imagen para un análisis de Ley."""
    try:
        url = svc.subir_certificado(db, analisis_id, archivo, tipo="ley")
        return {"mensaje": "Certificado subido correctamente", "url": url}
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


# --- ANÁLISIS DE RECUPERACIÓN ---


@router.post(
    "/recuperacion", response_model=AnalisisRecuperacionOut, status_code=status.HTTP_201_CREATED
)
def registrar_analisis_recuperacion(
    datos: AnalisisRecuperacionCreate,
    current_user=Depends(check_permiso("LABORATORIO", "CREATE")),
    db: Session = Depends(get_db),
):
    """Registra un análisis de Recuperación (Prueba de Botella) para un CIP."""
    try:
        resultado = svc.registrar_analisis_recuperacion(db, datos, usuario_id=current_user.id)
        return resultado
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.post("/recuperacion/{analisis_id}/certificado")
def subir_certificado_recuperacion(
    analisis_id: int,
    archivo: UploadFile = File(...),
    current_user=Depends(check_permiso("LABORATORIO", "UPDATE")),
    db: Session = Depends(get_db),
):
    """Sube el certificado en PDF/Imagen para un análisis de Recuperación."""
    try:
        url = svc.subir_certificado(db, analisis_id, archivo, tipo="recuperacion")
        return {"mensaje": "Certificado subido correctamente", "url": url}
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


# --- SYNC OFFLINE ---


@router.post("/offline/sync")
def sincronizar_batch(
    payload: SyncLaboratorioRequest,
    current_user=Depends(check_permiso("LABORATORIO", "CREATE")),
    db: Session = Depends(get_db),
):
    """Sincroniza un lote de análisis guardados offline en la tablet."""
    return svc.sincronizar_batch(db, payload, usuario_id=current_user.id)


@router.get("/muestras", response_model=list[MuestraLaboratorioItem])
def listar_muestras(
    current_user=Depends(check_permiso("LABORATORIO", "VIEW")),
    db: Session = Depends(get_db),
):
    """Obtiene el listado de códigos CIP y su estado de análisis."""
    return svc.obtener_muestras_laboratorio(db)
