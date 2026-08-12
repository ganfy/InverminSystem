from datetime import date

from app.core.database import get_db
from app.core.deps import check_permiso, get_current_user
from app.models.models import AnalisisLey, AnalisisRecuperacion, Lote, MapeoCIP, Muestreo, Usuario
from app.schemas.muestreo import (
    ActualizarLabCIPRequest,
    GenerarCipsRequest,
    MapeoCIPOut,
    MuestreoCreate,
    MuestreoOut,
    MuestreoUpdate,
    SyncCipResult,
    SyncCipsRequest,
    SyncCipsResponse,
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
@router.patch("/{muestreo_id}", response_model=MuestreoOut, status_code=status.HTTP_200_OK)
def actualizar_muestreo(
    muestreo_id: int,
    datos: MuestreoUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(check_permiso("MUESTREO", "UPDATE")),
):
    """Actualiza un intento de humedad dentro de la ventana permitida (1 hora)."""
    return sample_service.actualizar_muestreo(
        db=db, muestreo_id=muestreo_id, usuario_id=current_user.id, datos=datos
    )


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


@router.post(
    "/lotes/{ip_lote}/batch", response_model=list[MuestreoOut], status_code=status.HTTP_201_CREATED
)
def registrar_muestreo_batch(
    ip_lote: str,
    datos_list: list[MuestreoCreate],
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Registra múltiples intentos de determinación de humedad para un lote simultáneamente."""
    return sample_service.registrar_muestreo_batch(
        db=db, ip_lote=ip_lote, usuario_id=current_user.id, datos_list=datos_list
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
# 2b. SINCRONIZACIÓN DE CIPs OFFLINE
# ==========================================
@router.post("/sync-cips", response_model=SyncCipsResponse)
def sync_cips_offline(
    payload: SyncCipsRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Registra en BD los CIPs generados offline por la tablet.

    Idempotente: si el codigo_cip ya existe en mapeo_cip, retorna el server_id
    del registro existente sin crear duplicado ni retornar error.

    Seguridad: valida que el codigo_cip recibido sea igual al que el algoritmo
    del servidor hubiera generado para ese lote+correlativo (anti-manipulación).
    """
    from datetime import date

    from app.services.muestreo import generar_base_cip

    resultados = []
    for item in payload.cips:
        try:
            lote = db.query(Lote).filter(Lote.ip == item.ip).first()
            if not lote:
                resultados.append(
                    SyncCipResult(
                        offline_id=item.offline_id,
                        error=f"Lote {item.ip} no encontrado",
                    )
                )
                continue

            # Idempotencia: si ya existe este código exacto, retornar el existente
            existente = db.query(MapeoCIP).filter(MapeoCIP.codigo_cip == item.codigo_cip).first()
            if existente:
                resultados.append(SyncCipResult(offline_id=item.offline_id, server_id=existente.id))
                continue

            # Seguridad: verificar que el CIP fue generado con el algoritmo correcto
            base_esperada = generar_base_cip(lote.id, salt=item.correlativo)
            codigo_esperado = f"CIP-{base_esperada}-A{item.correlativo}"
            if item.codigo_cip != codigo_esperado:
                resultados.append(
                    SyncCipResult(
                        offline_id=item.offline_id,
                        error="CIP inválido: no coincide con el algoritmo del servidor",
                    )
                )
                continue

            nuevo = MapeoCIP(
                lote_id=lote.id,
                codigo_cip=item.codigo_cip,
                laboratorio=item.laboratorio,
                tipo_muestra=item.tipo_muestra,
                fecha_envio=date.today(),
            )
            db.add(nuevo)
            db.commit()
            db.refresh(nuevo)
            resultados.append(SyncCipResult(offline_id=item.offline_id, server_id=nuevo.id))

        except Exception as e:
            db.rollback()
            resultados.append(
                SyncCipResult(offline_id=item.offline_id, error=f"Error interno: {str(e)}")
            )

    return SyncCipsResponse(resultados=resultados)


@router.post(
    "/lotes/{ip_lote}/etiquetas",
    response_model=list[MapeoCIPOut],
    status_code=status.HTTP_201_CREATED,
)
def generar_cips(
    ip_lote: str,
    solicitud: GenerarCipsRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),  # Descomentar cuando uses auth
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
def listar_cips_lote(
    ip_lote: str, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)
):
    """Devuelve los códigos CIP ya generados para un lote (Reimpresión / Vista)."""
    lote = db.query(Lote).filter(Lote.ip == ip_lote).first()
    if not lote:
        raise HTTPException(status_code=404, detail="Lote no encontrado")

    cips = db.query(MapeoCIP).filter(MapeoCIP.lote_id == lote.id).all()
    resultado = []
    for cip in cips:
        tiene_ley = (
            db.query(AnalisisLey)
            .filter(AnalisisLey.cip == cip.codigo_cip, AnalisisLey.vigente)
            .first()
            is not None
        )
        tiene_rec = (
            db.query(AnalisisRecuperacion)
            .filter(AnalisisRecuperacion.cip == cip.codigo_cip, AnalisisRecuperacion.vigente)
            .first()
            is not None
        )
        resultado.append(
            MapeoCIPOut(
                id=cip.id,
                lote_id=cip.lote_id,
                codigo_cip=cip.codigo_cip,
                laboratorio=cip.laboratorio,
                tipo_muestra=cip.tipo_muestra,
                tiene_analisis_ley=tiene_ley,
                tiene_analisis_recuperacion=tiene_rec,
            )
        )
    return resultado


@router.get("/lotes", status_code=status.HTTP_200_OK)
def listar_lotes_muestreo(
    db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)
):
    """
    Devuelve la lista de lotes listos para el muestreo (sesiones finalizadas).
    """
    return sample_service.obtener_lotes_para_muestreo(db)


@router.get("/lotes/{ip_lote}/muestreos", response_model=list[MuestreoOut])
def listar_muestreos_lote(
    ip_lote: str, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)
):
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


@router.patch("/cips/{cip_id}/laboratorio", response_model=MapeoCIPOut)
def actualizar_laboratorio_cip(
    cip_id: int,
    datos: ActualizarLabCIPRequest,
    db: Session = Depends(get_db),
    current_user=Depends(check_permiso("MUESTREO", "UPDATE")),
):
    """Asigna el laboratorio destino a un CIP. Solo roles con permiso MUESTREO/UPDATE."""
    cip = db.query(MapeoCIP).filter(MapeoCIP.id == cip_id).first()
    if not cip:
        raise HTTPException(status_code=404, detail="CIP no encontrado")
    cip.laboratorio = datos.laboratorio
    if not cip.fecha_envio:
        cip.fecha_envio = date.today()
    db.commit()
    db.refresh(cip)
    return cip


@router.get("/labs", response_model=list[str])
def listar_laboratorios(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Lista de laboratorios configurados. Solo Admin/Gerencia/Comercial."""
    from app.models.models import Configuracion

    cfg = db.query(Configuracion).filter(Configuracion.clave == "labs_lista").first()
    if cfg:
        import json

        try:
            return json.loads(cfg.valor)
        except Exception:
            pass
    # fallback hardcodeado si no existe la config
    return ["Minares South S.R.L.", "El Dorado - Invermin Paititi", "Quantum", "Otro"]
