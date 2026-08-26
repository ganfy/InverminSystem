from datetime import timedelta

from app.core.database import get_db
from app.core.deps import check_permiso
from app.models.enums import TipoMuestra
from app.models.models import MapeoCIP
from app.schemas.laboratorio import AnalisisRecuperacionOut
from app.schemas.pruebas import (
    AdicionRequest,
    DescartarPruebaRequest,
    EnviarLaboratorioRequest,
    EtiquetadoPruebaOut,
    EtiquetarPruebaRequest,
    LotePruebaList,
    PruebaMetalurgicaCreate,
    PruebaMetalurgicaOut,
    PruebaRecuperacionItem,
    RecuperacionItem,
    SyncCipPruebaResult,
    SyncCipsPruebasRequest,
    SyncCipsPruebasResponse,
    SyncPruebasRequest,
    SyncPruebasResponse,
)
from app.services import pruebas as pruebas_service
from app.services.config_calculo import get_pruebas_usa_cip
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

router = APIRouter(prefix="/pruebas", tags=["Pruebas Metalúrgicas"])


@router.get("/lista", response_model=list[LotePruebaList])
def listar_pruebas(
    current_user=Depends(check_permiso("PRUEBAS_MET", "VIEW")),
    db: Session = Depends(get_db),
):
    return pruebas_service.obtener_lista_pruebas(db)


@router.get(
    "/para-recuperacion",
    response_model=list[PruebaRecuperacionItem],
    summary="Pruebas completadas con ley planta disponible (listas para análisis de recuperación)",
)
def pruebas_para_recuperacion(
    current_user=Depends(check_permiso("PRUEBAS_MET", "VIEW")),
    db: Session = Depends(get_db),
):
    """
    Retorna pruebas COMPLETADO + CIP interno + ley_cabeza calculada.
    Solo aparecen si el lote ya tiene análisis de ley vigentes (ley planta calculable).
    Usado por Comercial para crear el registro pendiente en laboratorio.
    """
    return pruebas_service.obtener_pruebas_para_recuperacion(db)


@router.post("/sync", response_model=SyncPruebasResponse)
def sync_pruebas(
    payload: SyncPruebasRequest,
    current_user=Depends(check_permiso("PRUEBAS_MET", "CREATE")),
    db: Session = Depends(get_db),
):
    return pruebas_service.sync_batch(db, payload.pruebas, current_user.id)


@router.post("/sync-cips", response_model=SyncCipsPruebasResponse)
def sync_cips_pruebas_offline(
    payload: SyncCipsPruebasRequest,
    current_user=Depends(check_permiso("PRUEBAS_MET", "UPDATE")),
    db: Session = Depends(get_db),
):
    """
    Registra en BD los CIPs de recuperación generados offline.

    Idempotente: si el codigo_cip ya existe, retorna su server_id sin duplicar.
    Seguridad: valida que los códigos coincidan con el algoritmo del servidor.
    - Modo CIP (pruebas_usa_cip=true): verifica contra generar_base_cip.
    - Modo IP (pruebas_usa_cip=false): verifica formato {ip}-{sufijo}{correlativo}.
    """
    from app.models.models import Lote, PruebaMetalurgica
    from app.services.muestreo import generar_base_cip

    resultados = []
    sufijos = {
        TipoMuestra.RECUPERACION_INTERNO: "R",
        TipoMuestra.RECUPERACION_EXTERNO: "E",
    }

    # Leer configuración de modo de identificación una sola vez para todo el batch
    usa_cip = get_pruebas_usa_cip(db)

    for item in payload.cips:
        try:
            lote = db.query(Lote).filter(Lote.ip == item.ip).first()
            if not lote:
                resultados.append(
                    SyncCipPruebaResult(
                        offline_id=item.offline_id,
                        error=f"Lote {item.ip} no encontrado",
                    )
                )
                continue

            sufijo = sufijos.get(item.tipo, "R")

            if usa_cip:
                # Modo CIP: validar que coincidan con el algoritmo del servidor
                base1_esperada = generar_base_cip(lote.id, salt=item.correlativo1)
                cip1_esperado = f"CIP-{base1_esperada}-{sufijo}{item.correlativo1}"
                if item.codigo_cip1 != cip1_esperado:
                    resultados.append(
                        SyncCipPruebaResult(
                            offline_id=item.offline_id,
                            error="CIP1 inválido: no coincide con el algoritmo del servidor",
                        )
                    )
                    continue

                base2_esperada = generar_base_cip(lote.id, salt=item.correlativo2)
                cip2_esperado = f"CIP-{base2_esperada}-{sufijo}{item.correlativo2}"
                if item.codigo_cip2 != cip2_esperado:
                    resultados.append(
                        SyncCipPruebaResult(
                            offline_id=item.offline_id,
                            error="CIP2 inválido: no coincide con el algoritmo del servidor",
                        )
                    )
                    continue
            else:
                # Modo IP: validar formato {ip}-{sufijo}{correlativo}
                ip1_esperado = f"{item.ip}-{sufijo}{item.correlativo1}"
                if item.codigo_cip1 != ip1_esperado:
                    resultados.append(
                        SyncCipPruebaResult(
                            offline_id=item.offline_id,
                            error="Código1 inválido: no coincide con el formato IP esperado",
                        )
                    )
                    continue

                ip2_esperado = f"{item.ip}-{sufijo}{item.correlativo2}"
                if item.codigo_cip2 != ip2_esperado:
                    resultados.append(
                        SyncCipPruebaResult(
                            offline_id=item.offline_id,
                            error="Código2 inválido: no coincide con el formato IP esperado",
                        )
                    )
                    continue

            # Idempotencia CIP1
            existente1 = db.query(MapeoCIP).filter(MapeoCIP.codigo_cip == item.codigo_cip1).first()
            if existente1:
                server_id1 = existente1.id
            else:
                nuevo1 = MapeoCIP(
                    lote_id=lote.id,
                    codigo_cip=item.codigo_cip1,
                    laboratorio=None,
                    tipo_muestra=item.tipo,
                    fecha_envio=None,
                )
                db.add(nuevo1)
                db.flush()
                server_id1 = nuevo1.id

            # Idempotencia CIP2
            existente2 = db.query(MapeoCIP).filter(MapeoCIP.codigo_cip == item.codigo_cip2).first()
            if existente2:
                server_id2 = existente2.id
            else:
                nuevo2 = MapeoCIP(
                    lote_id=lote.id,
                    codigo_cip=item.codigo_cip2,
                    laboratorio=None,
                    tipo_muestra=item.tipo,
                    fecha_envio=None,
                )
                db.add(nuevo2)
                db.flush()
                server_id2 = nuevo2.id

            # Asignar CIP1 a la prueba si aun no tiene
            prueba = (
                db.query(PruebaMetalurgica)
                .filter(
                    PruebaMetalurgica.lote_id == lote.id,
                    PruebaMetalurgica.cip.is_(None),
                )
                .order_by(PruebaMetalurgica.id.desc())
                .first()
            )
            if prueba:
                prueba.cip = item.codigo_cip1
                prueba.modificado_por = current_user.id

            db.commit()
            resultados.append(
                SyncCipPruebaResult(
                    offline_id=item.offline_id,
                    server_id_cip1=server_id1,
                    server_id_cip2=server_id2,
                )
            )

        except Exception as e:
            db.rollback()
            resultados.append(
                SyncCipPruebaResult(
                    offline_id=item.offline_id,
                    error=f"Error interno: {str(e)}",
                )
            )

    return SyncCipsPruebasResponse(resultados=resultados)


@router.get(
    "/recuperaciones",
    response_model=list[RecuperacionItem],
    summary="Leyes de cola y recuperación para Técnico de Pruebas",
)
def listar_recuperaciones(
    current_user=Depends(check_permiso("PRUEBAS_MET", "VIEW")),
    db: Session = Depends(get_db),
):
    """
    Retorna todos los análisis de recuperación vigentes con leyes de cola y
    % de recuperación. Visible para TecnicoMuestreo (no expone ley_cabeza).
    """
    return pruebas_service.obtener_recuperaciones(db)


# ── Rutas con path param ──────────────────────────────────────────────────────


@router.post(
    "/{ip_lote}/descartar",
    response_model=PruebaMetalurgicaOut,
    summary="Descartar una prueba (envase roto, etc.) — mantiene registro para trazabilidad",
)
def descartar_prueba(
    ip_lote: str,
    datos: DescartarPruebaRequest,
    current_user=Depends(check_permiso("PRUEBAS_MET", "UPDATE")),
    db: Session = Depends(get_db),
):
    try:
        prueba = pruebas_service.descartar_prueba(db, ip_lote, datos.motivo, current_user.id)
        db.commit()
        return PruebaMetalurgicaOut.model_validate(prueba)
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post(
    "/{ip_lote}/adicion",
    response_model=PruebaMetalurgicaOut,
    summary="Registrar adición parcial de NaCN/NaOH (acumulativa)",
)
def registrar_adicion(
    ip_lote: str,
    datos: AdicionRequest,
    current_user=Depends(check_permiso("PRUEBAS_MET", "UPDATE")),
    db: Session = Depends(get_db),
):
    try:
        prueba = pruebas_service.registrar_adicion(db, ip_lote, datos, current_user.id)
        db.commit()
        return PruebaMetalurgicaOut.model_validate(prueba)
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/{ip_lote}", response_model=PruebaMetalurgicaOut)
def obtener_detalle_prueba(
    ip_lote: str,
    current_user=Depends(check_permiso("PRUEBAS_MET", "VIEW")),
    db: Session = Depends(get_db),
):
    prueba = pruebas_service.obtener_prueba_por_ip(db, ip_lote)
    if not prueba:
        raise HTTPException(status_code=404, detail="No hay prueba metalúrgica para este lote")

    out = PruebaMetalurgicaOut.model_validate(prueba)
    # Poblar CIPs de recuperación desde mapeo_cip (el modelo ya no tiene columna cip)
    if prueba.fecha_ingreso:
        out.fecha_salida = prueba.fecha_ingreso + timedelta(hours=48)
    cips_rec = (
        db.query(MapeoCIP)
        .filter(
            MapeoCIP.lote_id == prueba.lote_id,
            MapeoCIP.tipo_muestra.in_(
                [
                    TipoMuestra.RECUPERACION_INTERNO,
                    TipoMuestra.RECUPERACION_EXTERNO,
                ]
            ),
        )
        .order_by(MapeoCIP.id)
        .all()
    )
    out.cips_recuperacion = [c.codigo_cip for c in cips_rec]
    return out


@router.post("/{ip_lote}", response_model=PruebaMetalurgicaOut, status_code=status.HTTP_201_CREATED)
def registrar_prueba(
    ip_lote: str,
    datos: PruebaMetalurgicaCreate,
    current_user=Depends(check_permiso("PRUEBAS_MET", "CREATE")),
    db: Session = Depends(get_db),
):
    try:
        prueba, warning = pruebas_service.registrar_prueba(db, ip_lote, datos, current_user.id)
        db.commit()
        response = PruebaMetalurgicaOut.model_validate(prueba)
        if prueba.fecha_ingreso:
            response.fecha_salida = prueba.fecha_ingreso + timedelta(hours=48)
        if warning:
            response.__pydantic_extra__ = {"warning": warning}
        return response
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post(
    "/{ip_lote}/adelantar-fecha",
    response_model=PruebaMetalurgicaOut,
    status_code=status.HTTP_200_OK,
    summary="Adelanta 24 horas a la fecha de ingreso de la prueba en proceso",
)
def adelantar_fecha(
    ip_lote: str,
    current_user=Depends(check_permiso("PRUEBAS_MET", "UPDATE")),
    db: Session = Depends(get_db),
):
    try:
        prueba = pruebas_service.adelantar_fecha_ingreso_24h(db, ip_lote, current_user.id)
        db.commit()
        response = PruebaMetalurgicaOut.model_validate(prueba)
        if prueba.fecha_ingreso:
            response.fecha_salida = prueba.fecha_ingreso + timedelta(hours=48)
        return response
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post(
    "/{ip_lote}/remuestreo",
    response_model=PruebaMetalurgicaOut,
    status_code=status.HTTP_201_CREATED,
    summary="Crea nuevo registro de prueba metalúrgica (remuestreo) sin modificar el anterior",
)
def solicitar_remuestreo(
    ip_lote: str,
    current_user=Depends(check_permiso("PRUEBAS_MET", "CREATE")),
    db: Session = Depends(get_db),
):
    """
    Siempre crea un INSERT nuevo para auditoría. El registro anterior queda intacto.
    El técnico deberá rellenar los parámetros en el formulario de pruebas.
    """
    try:
        prueba = pruebas_service.crear_prueba_remuestreo(db, ip_lote, current_user.id)
        db.commit()
        return PruebaMetalurgicaOut.model_validate(prueba)
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post(
    "/{ip_lote}/etiquetar",
    response_model=EtiquetadoPruebaOut,
    status_code=status.HTTP_201_CREATED,
    summary="Genera CIP de recuperación para una prueba completada",
)
def etiquetar_prueba(
    ip_lote: str,
    datos: EtiquetarPruebaRequest = EtiquetarPruebaRequest(),
    current_user=Depends(check_permiso("PRUEBAS_MET", "UPDATE")),
    db: Session = Depends(get_db),
):
    """
    Genera un CIP de recuperación. Puede llamarse múltiples veces
    para generar CIPs adicionales (ej: interno + externo).
    tipo: RecuperacionInterno (default) | RecuperacionExterno
    """
    try:
        resultado = pruebas_service.etiquetar_prueba(db, ip_lote, current_user.id, tipo=datos.tipo)
        db.commit()
        return resultado
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post(
    "/{ip_lote}/enviar-laboratorio",
    response_model=AnalisisRecuperacionOut,
    status_code=status.HTTP_201_CREATED,
    summary="Envía muestras de prueba COMPLETADO al laboratorio interno (Paititi)",
)
def enviar_a_laboratorio(
    ip_lote: str,
    datos: EnviarLaboratorioRequest,
    current_user=Depends(check_permiso("PRUEBAS_MET", "UPDATE")),
    db: Session = Depends(get_db),
):
    """
    Crea registros PENDIENTE de recuperación para el laboratorio interno Paititi.
    Accesible por TecnicoMet, Comercial, Admin.
    sub_tipos: ['SOLIDOS', 'SOLUCION'] para ambos análisis, o solo uno.
    Requiere que la prueba esté COMPLETADO y tenga CIP de RecuperacionInterno.
    La ley_cabeza se calcula automáticamente desde los análisis de ley vigentes del lote.
    """
    from app.models.models import Lote
    from app.schemas.laboratorio import EnviarRecuperacionInternaRequest
    from app.services.laboratorio import _rec_out, enviar_recuperacion_interna

    try:
        req = EnviarRecuperacionInternaRequest(
            sub_tipos=datos.sub_tipos,
            laboratorio="Paititi",
            cip=datos.cip,
        )
        nuevo = enviar_recuperacion_interna(db, ip_lote, req, current_user.id)
        db.commit()
        lote = db.query(Lote).filter(Lote.id == nuevo.lote_id).first()
        ip_lote_res = lote.ip if lote else None
        return _rec_out(nuevo, ip_lote_res)
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e)) from e
