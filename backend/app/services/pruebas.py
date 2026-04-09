import logging
from datetime import datetime, timedelta
from decimal import Decimal

from app.models.enums import TipoMuestra
from app.models.models import (
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


# ── Helper compartido ─────────────────────────────────────────────────────────


def _get_cips_recuperacion(db: Session, lote_id: int) -> list[MapeoCIP]:
    """Retorna todos los CIPs de recuperación (interno o externo) del lote."""
    return (
        db.query(MapeoCIP)
        .filter(
            MapeoCIP.lote_id == lote_id,
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


def calcular_ley_planta(db: Session, lote_id: int) -> Decimal | None:
    """
    Calcula ley planta = promedio de análisis de ley VIGENTES del lote.
    Excluye tipo 'minero'. Si hay dirimencia, usa solo ese.
    Función compartida usada por pruebas y laboratorio.
    """
    from app.models.models import AnalisisLey

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


# ── Lista principal ───────────────────────────────────────────────────────────


def obtener_lista_pruebas(db: Session) -> list[LotePruebaList]:
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

        fecha_recepcion = lote.pesajes[0].fecha_fin if lote.pesajes else None

        estado = "PENDIENTE"
        fecha_ingreso = None
        fecha_salida = None

        if prueba:
            fecha_ingreso = prueba.fecha_ingreso
            fecha_salida_calc = prueba.fecha_ingreso + timedelta(hours=48)
            fecha_salida = fecha_salida_calc
            estado = "COMPLETADO" if ahora >= fecha_salida_calc else "EN PROCESO"

        # CIPs de recuperación asignados a este lote
        cips_rec = _get_cips_recuperacion(db, lote.id)
        cip_asignado = cips_rec[0].codigo_cip if cips_rec else None

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


# ── Etiquetado ────────────────────────────────────────────────────────────────


def etiquetar_prueba(
    db: Session,
    ip_lote: str,
    usuario_id: int,
    tipo: TipoMuestra = TipoMuestra.RECUPERACION_INTERNO,
) -> EtiquetadoPruebaOut:
    """
    Genera un CIP de recuperación para la prueba metalúrgica de un lote.
    - Solo disponible cuando la prueba está COMPLETADO (48h pasadas).
    - Se puede llamar múltiples veces para generar CIPs adicionales
      (ej: uno interno y uno externo).
    - tipo: RecuperacionInterno (default) o RecuperacionExterno.
    """
    lote = db.query(Lote).filter(Lote.ip == ip_lote).first()
    if not lote:
        raise ValueError(f"Lote '{ip_lote}' no encontrado")

    prueba = db.query(PruebaMetalurgica).filter(PruebaMetalurgica.lote_id == lote.id).first()
    if not prueba:
        raise ValueError(f"No hay prueba metalúrgica registrada para el lote '{ip_lote}'")

    ahora = datetime.now()
    if ahora < prueba.fecha_ingreso + timedelta(hours=48):
        raise ValueError("La prueba aún no ha completado las 48 horas requeridas")

    # Contar todos los CIPs del lote (incluye Laboratorio + Recuperacion*)
    # para generar sufijo único global
    total_cips = db.query(MapeoCIP).filter(MapeoCIP.lote_id == lote.id).count()
    correlativo = total_cips + 1
    base = generar_base_cip(lote.id)

    # Sufijo diferenciado por tipo
    sufijo = "R" if tipo == TipoMuestra.RECUPERACION_INTERNO else "E"
    codigo_cip = f"CIP-{base}-{sufijo}{correlativo}"

    nuevo_cip = MapeoCIP(
        lote_id=lote.id,
        codigo_cip=codigo_cip,
        laboratorio=None,
        tipo_muestra=tipo,
        fecha_envio=ahora.date(),
    )
    db.add(nuevo_cip)
    db.flush()

    return EtiquetadoPruebaOut(
        ip=ip_lote,
        cip=codigo_cip,
        tipo=tipo,
        mensaje=f"CIP de recuperación ({tipo}) generado",
    )


# ── Pruebas listas para recuperación ─────────────────────────────────────────


def obtener_pruebas_para_recuperacion(db: Session) -> list[PruebaRecuperacionItem]:
    """
    Retorna pruebas COMPLETADO (48h) que:
    1. Tienen al menos 1 CIP de tipo RecuperacionInterno.
    2. El lote tiene ley planta calculable (al menos 1 análisis de ley vigente).
    Usado por Comercial para crear el registro pendiente de recuperación.
    """
    ahora = datetime.now()

    # Lote IDs con CIP de recuperación interno
    lote_ids_con_cip_rec = (
        db.query(MapeoCIP.lote_id)
        .filter(MapeoCIP.tipo_muestra == TipoMuestra.RECUPERACION_INTERNO)
        .distinct()
        .subquery()
    )

    pruebas = (
        db.query(PruebaMetalurgica)
        .filter(PruebaMetalurgica.lote_id.in_(lote_ids_con_cip_rec))
        .all()
    )

    resultado: list[PruebaRecuperacionItem] = []

    for prueba in pruebas:
        fecha_salida = prueba.fecha_ingreso + timedelta(hours=48)
        if ahora < fecha_salida:
            continue  # Aún no completó las 48h

        lote = db.query(Lote).filter(Lote.id == prueba.lote_id).first()
        if not lote:
            continue

        # Solo aparece si hay ley planta calculable
        ley_planta = calcular_ley_planta(db, lote.id)
        if ley_planta is None:
            continue

        try:
            proveedor = lote.sesion.provacop.proveedor.razon_social
        except AttributeError:
            proveedor = "-"

        # CIPs de recuperación del lote
        cips_rec = _get_cips_recuperacion(db, lote.id)
        # Solo los internos para este endpoint
        cips_internos = [c for c in cips_rec if c.tipo_muestra == TipoMuestra.RECUPERACION_INTERNO]

        # Estado de análisis de recuperación por CIP
        for cip_obj in cips_internos:
            tiene_rec = (
                db.query(AnalisisRecuperacion)
                .filter(
                    AnalisisRecuperacion.cip == cip_obj.codigo_cip,
                    AnalisisRecuperacion.vigente == True,  # noqa: E712
                )
                .first()
            ) is not None

            resultado.append(
                PruebaRecuperacionItem(
                    ip=lote.ip,
                    cip=cip_obj.codigo_cip,
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
