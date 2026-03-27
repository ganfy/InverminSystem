from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.models import Lote, MapeoCIP, Muestreo, Usuario
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

router = APIRouter(prefix="/muestreo", tags=["Muestreo"])


# ==========================================
# 1. REGISTRO INDIVIDUAL (ONLINE)
# ==========================================
@router.post("/lotes/{ip_lote}", response_model=MuestreoOut, status_code=status.HTTP_201_CREATED)
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
@router.post("/sync", response_model=SyncMuestreosResponse)
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
    "/lotes/{ip_lote}/etiquetas",
    response_model=list[MapeoCIPOut],
    status_code=status.HTTP_201_CREATED,
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
    try:
        return sample_service.generar_cips_para_lote(
            db=db, ip_lote=ip_lote, cantidad=solicitud.cantidad
        )
    except HTTPException:
        # Si es un error de negocio controlado (ej. 404), lo dejamos pasar
        raise
    except Exception as e:
        # Si algo explota (ej. error de SQL), forzamos la liberación de la base de datos
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado al generar etiquetas: {str(e)}",
        ) from e


@router.get(
    "/lotes/{ip_lote}/etiquetas", response_model=list[MapeoCIPOut], status_code=status.HTTP_200_OK
)
def listar_cips_lote(ip_lote: str, db: Session = Depends(get_db)):
    """Devuelve los códigos CIP ya generados para un lote (Reimpresión / Vista)."""
    lote = db.query(Lote).filter(Lote.ip == ip_lote).first()
    if not lote:
        raise HTTPException(status_code=404, detail="Lote no encontrado")

    cips = db.query(MapeoCIP).filter(MapeoCIP.lote_id == lote.id).all()
    return cips


@router.get("/lotes", status_code=status.HTTP_200_OK)
def listar_lotes_muestreo(db: Session = Depends(get_db)):
    """
    Devuelve la lista de lotes listos para el muestreo (sesiones finalizadas).
    """
    return sample_service.obtener_lotes_para_muestreo(db)


@router.get("/lotes/{ip_lote}/muestreos", response_model=list[MuestreoOut])
def listar_muestreos_lote(ip_lote: str, db: Session = Depends(get_db)):
    """Obtiene el historial de intentos de humedad de un lote específico."""
    lote = db.query(Lote).filter(Lote.ip == ip_lote).first()
    if not lote:
        raise HTTPException(status_code=404, detail="Lote no encontrado")

    return (
        db.query(Muestreo)
        .filter(Muestreo.lote_id == lote.id)
        .order_by(Muestreo.intento.asc())
        .all()
    )
