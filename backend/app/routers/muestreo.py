from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.models import Usuario
from app.schemas.muestreo import (
    GenerarCipsRequest,
    MapeoCIPOut,
    MuestreoCreate,
    MuestreoOut,
    SyncMuestreosRequest,
    SyncMuestreosResponse,
    SyncResult,
)
from app.services import muestreo as sample_service
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

router = APIRouter(prefix="/laboratorio", tags=["Laboratorio y Muestreo"])


# ==========================================
# 1. REGISTRO INDIVIDUAL (ONLINE)
# ==========================================
@router.post(
    "/lotes/{ip_lote}/muestreos", response_model=MuestreoOut, status_code=status.HTTP_201_CREATED
)
def registrar_muestreo(
    ip_lote: str,
    datos: MuestreoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Registra un nuevo intento de determinación de humedad para un lote."""
    return sample_service.registrar_muestreo(
        db=db, ip_lote=ip_lote, usuario_id=current_user.id, datos=datos
    )


# ==========================================
# 2. SINCRONIZACIÓN BATCH (OFFLINE A ONLINE)
# ==========================================
@router.post("/muestreos/sync", response_model=SyncMuestreosResponse)
def sync_muestreos_offline(
    payload: SyncMuestreosRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Sincroniza un lote de muestreos registrados offline desde la tablet."""
    resultados = []
    for item in payload.muestreos:
        try:
            nuevo_muestreo = sample_service.registrar_muestreo(
                db=db, ip_lote=item.ip, usuario_id=current_user.id, datos=item.datos
            )
            resultados.append(SyncResult(offline_id=item.offline_id, server_id=nuevo_muestreo.id))

        except HTTPException as e:
            # Si el backend rechaza el dato (ej. humedad > 50%), capturamos el error para la UI
            db.rollback()
            resultados.append(SyncResult(offline_id=item.offline_id, error=str(e.detail)))

        except Exception as e:
            # Errores no controlados de base de datos
            db.rollback()
            resultados.append(
                SyncResult(offline_id=item.offline_id, error=f"Error interno: {str(e)}")
            )

    return SyncMuestreosResponse(resultados=resultados)


# ==========================================
# 3. GENERACIÓN DE CÓDIGOS (CIP)
# ==========================================
@router.post(
    "/lotes/{ip_lote}/cips", response_model=list[MapeoCIPOut], status_code=status.HTTP_201_CREATED
)
def generar_cips(
    ip_lote: str,
    solicitud: GenerarCipsRequest,
    db: Session = Depends(get_db),
    # current_user: Usuario = Depends(get_current_user) # Descomentar cuando uses auth
):
    """
    Genera códigos CIP anónimos y seguros (Muestreo Ciego) para las muestras de laboratorio.
    """
    return sample_service.generar_cips_para_lote(
        db=db, ip_lote=ip_lote, cantidad=solicitud.cantidad
    )
