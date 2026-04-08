import logging
from datetime import datetime, timedelta
from decimal import Decimal

from app.models.models import (
    AnalisisLey,
    AnalisisRecuperacion,
    Lote,
    MapeoCIP,
    PruebaMetalurgica,
)
from app.schemas.pruebas import (
    EtiquetadoPruebaOut,
    LotePruebaList,
    PruebaMetalurgicaCreate,
    PruebaRecuperacionItem,
    SyncPruebasResponse,
    SyncResult,
)
from app.services.muestreo import generar_base_cip
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


# ── Lista principal ───────────────────────────────────────────────────────────


def obtener_lista_pruebas(db: Session) -> list[LotePruebaList]:
    """Lista todos los lotes y su estado en pruebas metalúrgicas."""
    lotes_db = (
        db.query(Lote)
        .filter(Lote.eliminado == False)  # noqa: E712
        .order_by(Lote.id.desc())
        .all()
    )

    lista: list[LotePruebaList] = []
    ahora = datetime.now()

    for lote in lotes_db:
        prueba = db.query(PruebaMetalurgica).filter(PruebaMetalurgica.lote_id == lote.id).first()

        fecha_recepcion = None
        if lote.pesajes:
            fecha_recepcion = lote.pesajes[0].fecha_fin

        estado = "PENDIENTE"
        fecha_ingreso = None
        fecha_salida = None

        if prueba:
            fecha_ingreso = prueba.fecha_ingreso
            fecha_salida_calc = prueba.fecha_ingreso + timedelta(hours=48)
            fecha_salida = fecha_salida_calc

            if ahora >= fecha_salida_calc:
                estado = "COMPLETADO"
            else:
                estado = "EN PROCESO"

        # CIP asignado para recuperación (si fue etiquetado)
        cip_asignado = prueba.cip if prueba and prueba.cip else None

        lista.append(
            LotePruebaList(
                ip=lote.ip,
                fecha_recepcion=fecha_recepcion,
                fecha_ingreso=fecha_ingreso,
                fecha_salida=fecha_salida,
                malla_porcentaje=float(prueba.malla_porcentaje)
                if prueba and prueba.malla_porcentaje
                else None,
                gasto_agno3=float(prueba.gasto_agno3) if prueba and prueba.gasto_agno3 else None,
                estado=estado,
                cip_asignado=cip_asignado,
                etiquetado=cip_asignado is not None,
            )
        )

    return lista


def registrar_prueba(
    db: Session,
    ip_lote: str,
    datos: PruebaMetalurgicaCreate,
    usuario_id: int,
) -> tuple[PruebaMetalurgica, str | None]:
    lote = db.query(Lote).filter(Lote.ip == ip_lote).first()
    if not lote:
        raise ValueError(f"Lote '{ip_lote}' no encontrado")

    warning_msg = None
    if datos.malla_porcentaje is not None:
        if not (88 <= datos.malla_porcentaje <= 94):
            warning_msg = (
                f"⚠️ Malla {datos.malla_porcentaje:.1f}% fuera del rango aceptable (88% - 94%)"
            )

    prueba_existente = (
        db.query(PruebaMetalurgica).filter(PruebaMetalurgica.lote_id == lote.id).first()
    )

    if prueba_existente:
        for campo, valor in datos.model_dump().items():
            setattr(prueba_existente, campo, valor)
        prueba_existente.modificado_por = usuario_id
        prueba = prueba_existente
    else:
        prueba = PruebaMetalurgica(
            lote_id=lote.id,
            **datos.model_dump(),
            creado_por=usuario_id,
        )
        db.add(prueba)

    db.flush()
    db.refresh(prueba)
    return prueba, warning_msg


def obtener_prueba_por_ip(db: Session, ip_lote: str) -> PruebaMetalurgica | None:
    lote = db.query(Lote).filter(Lote.ip == ip_lote).first()
    if not lote:
        return None
    return db.query(PruebaMetalurgica).filter(PruebaMetalurgica.lote_id == lote.id).first()


# ── Etiquetado (nuevo) ────────────────────────────────────────────────────────


def etiquetar_prueba(db: Session, ip_lote: str, usuario_id: int) -> EtiquetadoPruebaOut:
    """
    Genera un CIP de recuperación para la prueba metalúrgica de un lote.
    Solo disponible cuando la prueba está COMPLETADO (48h pasadas).
    """
    lote = db.query(Lote).filter(Lote.ip == ip_lote).first()
    if not lote:
        raise ValueError(f"Lote '{ip_lote}' no encontrado")

    prueba = db.query(PruebaMetalurgica).filter(PruebaMetalurgica.lote_id == lote.id).first()
    if not prueba:
        raise ValueError(f"No hay prueba metalúrgica registrada para el lote '{ip_lote}'")

    # Verificar que hayan pasado las 48h
    ahora = datetime.now()
    if ahora < prueba.fecha_ingreso + timedelta(hours=48):
        raise ValueError("La prueba aún no ha completado las 48 horas requeridas")

    # Si ya tiene CIP, devolver el existente
    if prueba.cip:
        return EtiquetadoPruebaOut(
            ip=ip_lote,
            cip=prueba.cip,
            mensaje="La prueba ya tenía un CIP de recuperación asignado",
        )

    # Generar CIP único para recuperación
    # Se usa la misma base que muestreo pero con sufijo R1, R2...
    base = generar_base_cip(lote.id)

    # Contar CIPs existentes del lote para el sufijo
    cips_existentes = db.query(MapeoCIP).filter(MapeoCIP.lote_id == lote.id).count()
    correlativo = cips_existentes + 1
    codigo_cip = f"CIP-{base}-R{correlativo}"

    # Registrar en mapeo_cip
    nuevo_cip = MapeoCIP(
        lote_id=lote.id,
        codigo_cip=codigo_cip,
        laboratorio=None,
        tipo_muestra="RECUPERACION",
        fecha_envio=ahora.date(),
    )
    db.add(nuevo_cip)
    db.flush()

    # Asociar a la prueba
    prueba.cip = codigo_cip
    db.flush()

    return EtiquetadoPruebaOut(ip=ip_lote, cip=codigo_cip)


# ── Pruebas listas para recuperación (nuevo) ─────────────────────────────────


def _calcular_ley_planta(db: Session, lote_id: int) -> Decimal | None:
    """
    Calcula la ley planta = promedio de análisis de ley VIGENTES del lote.
    Excluye tipo 'minero'. Si hay dirimencia, usa solo ese.
    """
    # Buscar dirimencia primero
    dirimencia = (
        db.query(AnalisisLey)
        .filter(
            AnalisisLey.lote_id == lote_id,
            AnalisisLey.tipo_analisis == "dirimencia",
            AnalisisLey.vigente == True,  # noqa: E712
        )
        .first()
    )
    if dirimencia:
        return dirimencia.ley_final

    # Promediar análisis vigentes (planta + externo)
    analisis = (
        db.query(AnalisisLey)
        .filter(
            AnalisisLey.lote_id == lote_id,
            AnalisisLey.vigente == True,  # noqa: E712
            AnalisisLey.tipo_analisis.in_(["planta", "externo"]),
        )
        .all()
    )
    if not analisis:
        return None

    total = sum(a.ley_final for a in analisis if a.ley_final is not None)
    return (total / len(analisis)).quantize(Decimal("0.0001"))


def obtener_pruebas_para_recuperacion(db: Session) -> list[PruebaRecuperacionItem]:
    """
    Retorna pruebas COMPLETADO (48h) + CIP asignado + ley planta disponible.
    Solo estas pueden pasar a análisis de recuperación en laboratorio.
    """
    ahora = datetime.now()
    pruebas = (
        db.query(PruebaMetalurgica)
        .filter(PruebaMetalurgica.cip.isnot(None))  # ya fue etiquetada
        .all()
    )

    resultado: list[PruebaRecuperacionItem] = []

    for prueba in pruebas:
        # Verificar 48h completadas
        fecha_salida = prueba.fecha_ingreso + timedelta(hours=48)
        if ahora < fecha_salida:
            continue

        lote = db.query(Lote).filter(Lote.id == prueba.lote_id).first()
        if not lote:
            continue

        # Calcular ley planta
        ley_planta = _calcular_ley_planta(db, lote.id)
        if ley_planta is None:
            continue  # No hay ley planta → no puede hacer recuperación aún

        # Obtener nombre proveedor
        try:
            proveedor = lote.sesion.provacop.proveedor.razon_social
        except AttributeError:
            proveedor = "-"

        # ¿Ya tiene análisis de recuperación con este CIP?
        tiene_rec = (
            db.query(AnalisisRecuperacion)
            .filter(
                AnalisisRecuperacion.cip == prueba.cip,
                AnalisisRecuperacion.vigente == True,  # noqa: E712
            )
            .first()
        ) is not None

        resultado.append(
            PruebaRecuperacionItem(
                ip=lote.ip,
                cip=prueba.cip,
                lote_id=lote.id,
                proveedor=proveedor,
                fecha_salida=fecha_salida,
                ley_cabeza=ley_planta,
                tiene_analisis_recuperacion=tiene_rec,
            )
        )

    return resultado


# ── Sync Offline ──────────────────────────────────────────────────────────────


def sync_batch(
    db: Session,
    pruebas_offline: list,
    usuario_id: int,
) -> SyncPruebasResponse:
    resultados: list[SyncResult] = []

    for item in pruebas_offline:
        try:
            prueba, _ = registrar_prueba(db, item.ip, item.datos, usuario_id)
            db.flush()
            resultados.append(SyncResult(offline_id=item.offline_id, server_id=prueba.id))
        except Exception as e:
            db.rollback()
            resultados.append(SyncResult(offline_id=item.offline_id, error=str(e)))

    db.commit()
    return SyncPruebasResponse(resultados=resultados)
