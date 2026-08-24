import logging
from datetime import UTC, datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal

from app.models.enums import TipoMuestra
from app.models.models import (
    AnalisisLey,
    AnalisisRecuperacion,
    Lote,
    MapeoCIP,
    PruebaMetalurgica,
)
from app.schemas.pruebas import (
    AdicionRequest,
    EtiquetadoPruebaOut,
    LotePruebaList,
    PruebaMetalurgicaCreate,
    PruebaRecuperacionItem,
    RecuperacionItem,
    SyncPruebasResponse,
    SyncResult,
)
from app.services.config_calculo import get_pruebas_usa_cip
from app.services.muestreo import generar_base_cip
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


# ── Helpers internos ─────────────────────────────────────────────────────────


def _generar_codigo_recuperacion(
    ip: str,
    lote_id: int,
    correlativo: int,
    sufijo: str,
    usa_cip: bool,
) -> str:
    """
    Genera el código de identificación para una muestra de recuperación.

    - usa_cip=True  → "CIP-{base}-{sufijo}{correlativo}" (ej: CIP-058598D-R1)
    - usa_cip=False → "{ip}-{sufijo}{correlativo}"       (ej: IP-0042-R1)

    El formato IP garantiza unicidad en mapeo_cip.codigo_cip porque
    IP + correlativo siempre es único por lote.
    """
    if usa_cip:
        base = generar_base_cip(lote_id, salt=correlativo)
        return f"CIP-{base}-{sufijo}{correlativo}"
    else:
        return f"{ip}-{sufijo}{correlativo}"


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


def _get_sub_tipos_enviados(db: Session, cip: str | None) -> list[str]:
    """Retorna los sub_tipos que ya tienen análisis de recuperación vigente (PENDIENTE o COMPLETADO)
    para el CIP dado. Usado para saber qué sub-tipos NO hay que volver a enviar."""
    if not cip:
        return []
    registros = (
        db.query(AnalisisRecuperacion.sub_tipo)
        .filter(
            AnalisisRecuperacion.cip == cip,
            AnalisisRecuperacion.vigente == True,  # noqa: E712
            ~AnalisisRecuperacion.eliminado,
        )
        .all()
    )
    # Normalizar: None sub_tipo cuenta como 'SOLIDOS' (análisis legacy sin sub_tipo)
    enviados: list[str] = []
    for (sub_tipo,) in registros:
        if sub_tipo:
            enviados.append(sub_tipo)
        else:
            enviados.append("SOLIDOS")  # legacy
    return list(set(enviados))


def calcular_ley_planta(
    db: Session, lote_id: int, excluidos: list[int] | None = None
) -> Decimal | None:
    """
    Calcula ley planta = promedio de análisis de ley VIGENTES del lote.
    Excluye tipo 'minero'.
    Función compartida usada por pruebas y laboratorio.
    """
    query = db.query(AnalisisLey).filter(
        AnalisisLey.lote_id == lote_id,
        AnalisisLey.vigente == True,  # noqa: E712
        AnalisisLey.tipo_analisis.in_(["planta", "externo"]),
        AnalisisLey.material == "Au",
    )
    if excluidos:
        query = query.filter(AnalisisLey.id.notin_(excluidos))
    analisis = query.all()
    if not analisis:
        return None

    from app.services.config_calculo import get_constantes, get_quantize_decimal

    constantes = get_constantes(db)
    q_lab = get_quantize_decimal(constantes.decimales_ley_laboratorio)
    q_planta = get_quantize_decimal(constantes.decimales_ley_planta)

    leyes = [
        Decimal(str(a.ley_final)).quantize(q_lab, rounding=constantes.redondeo_ley_laboratorio)
        for a in analisis
        if a.ley_final is not None
    ]
    if not leyes:
        return None

    total = sum(leyes)
    return (total / len(leyes)).quantize(q_planta, rounding=constantes.redondeo_ley_planta)


# ── Lista principal ───────────────────────────────────────────────────────────


def obtener_lista_pruebas(db: Session) -> list[LotePruebaList]:
    lotes_db = (
        db.query(Lote)
        .filter(
            Lote.eliminado == False,  # noqa: E712
            Lote.tipo_material.in_(["Mineral", "Llampo", "M.Llampo"]),
            Lote.ip.like("IP-%"),
        )
        .order_by(Lote.id.desc())
        .all()
    )

    lista: list[LotePruebaList] = []
    ahora = datetime.now(UTC).replace(tzinfo=None)

    for lote in lotes_db:
        pruebas = (
            db.query(PruebaMetalurgica)
            .filter(PruebaMetalurgica.lote_id == lote.id)
            .order_by(PruebaMetalurgica.id)
            .all()
        )

        fecha_recepcion = lote.pesajes[0].fecha_fin if lote.pesajes else None

        # CIPs de recuperación asignados a este lote
        cips_rec = _get_cips_recuperacion(db, lote.id)

        # Caso 1: NO hay pruebas → PENDIENTE
        if not pruebas:
            lista.append(
                LotePruebaList(
                    lote_id=lote.id,
                    ip=lote.ip,
                    fecha_recepcion=fecha_recepcion,
                    fecha_ingreso=None,
                    fecha_salida=None,
                    malla_porcentaje=None,
                    gasto_agno3=None,
                    estado="PENDIENTE",
                    cip_asignado=None,
                    etiquetado=False,
                )
            )
            continue

        # Caso 2: SÍ hay pruebas → agregar TODAS
        for n, prueba in enumerate(pruebas):
            fecha_ingreso = prueba.fecha_ingreso
            fecha_salida = fecha_ingreso + timedelta(hours=48) if fecha_ingreso else None

            estado = "PENDIENTE"
            if fecha_ingreso:
                estado = "COMPLETADO" if ahora >= fecha_salida else "EN PROCESO"

            # Mapeo robusto de CIPs (1 o 2 CIPs dependiendo de cuándo se generó)
            cip_asignado = prueba.cip
            cips_asignados = []

            if cip_asignado:
                # Encontrar el índice de este CIP principal en la lista cips_rec
                idx = next((i for i, c in enumerate(cips_rec) if c.codigo_cip == cip_asignado), -1)
                if idx != -1:
                    cips_asignados.append(cips_rec[idx].codigo_cip)
                    # Revisar si el siguiente CIP también es de esta prueba
                    if idx + 1 < len(cips_rec):
                        next_cip = cips_rec[idx + 1].codigo_cip
                        # Si hay una siguiente prueba, verificamos que next_cip no sea SU cip principal
                        next_test_cip = pruebas[n + 1].cip if n + 1 < len(pruebas) else None
                        if next_test_cip != next_cip:
                            cips_asignados.append(next_cip)

            sub_tipos_enviados = []
            if cip_asignado:
                sub_tipos_enviados = _get_sub_tipos_enviados(db, cip_asignado)

            sub_tipos_enviados_por_cip = {}
            for c in cips_asignados:
                sub_tipos_enviados_por_cip[c] = _get_sub_tipos_enviados(db, c)

            lista.append(
                LotePruebaList(
                    lote_id=lote.id,
                    ip=lote.ip,
                    fecha_recepcion=fecha_recepcion,
                    fecha_ingreso=fecha_ingreso,
                    fecha_salida=fecha_salida,
                    malla_porcentaje=float(prueba.malla_porcentaje)
                    if prueba.malla_porcentaje is not None
                    else None,
                    gasto_agno3=float(prueba.gasto_agno3)
                    if prueba.gasto_agno3 is not None
                    else None,
                    estado=estado,
                    cip_asignado=cip_asignado,
                    cips_asignados=cips_asignados,
                    etiquetado=bool(cips_asignados),
                    adicion_nacn=float(prueba.adicion_nacn)
                    if prueba.adicion_nacn is not None
                    else None,
                    adicion_naoh=float(prueba.adicion_naoh)
                    if prueba.adicion_naoh is not None
                    else None,
                    descartado=bool(prueba.descartado),
                    motivo_descarte=prueba.motivo_descarte,
                    sub_tipos_enviados=sub_tipos_enviados,
                    sub_tipos_enviados_por_cip=sub_tipos_enviados_por_cip,
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
                f"Malla {datos.malla_porcentaje:.1f}% fuera del rango aceptable (88% - 94%)"
            )

    datos.fecha_ingreso = datetime.now(UTC).replace(tzinfo=None)

    prueba_existente = (
        db.query(PruebaMetalurgica)
        .filter(PruebaMetalurgica.lote_id == lote.id)
        .order_by(PruebaMetalurgica.id.desc())
        .first()
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
    return (
        db.query(PruebaMetalurgica)
        .filter(PruebaMetalurgica.lote_id == lote.id)
        .order_by(PruebaMetalurgica.id.desc())
        .first()
    )


# ── Etiquetado ────────────────────────────────────────────────────────────────


def crear_prueba_remuestreo(
    db: Session,
    ip_lote: str,
    usuario_id: int,
) -> PruebaMetalurgica:
    """
    Crea SIEMPRE un nuevo registro de PruebaMetalurgica para el lote (auditoría).
    No modifica registros existentes. El técnico completará los campos en el formulario.
    """
    lote = db.query(Lote).filter(Lote.ip == ip_lote).first()
    if not lote:
        raise ValueError(f"Lote '{ip_lote}' no encontrado")

    prueba = PruebaMetalurgica(
        lote_id=lote.id,
        fecha_ingreso=None,  # se completará al ingresar a pruebas
        creado_por=usuario_id,
    )
    db.add(prueba)
    db.flush()
    db.refresh(prueba)
    return prueba


def etiquetar_prueba(
    db: Session,
    ip_lote: str,
    usuario_id: int,
    tipo: TipoMuestra = TipoMuestra.RECUPERACION_INTERNO,
) -> EtiquetadoPruebaOut:
    """
    Genera un CIP de recuperación para la prueba metalúrgica de un lote.
    - Solo disponible cuando la prueba está COMPLETADO (48h pasadas).
    - tipo: RecuperacionInterno (default) o RecuperacionExterno.
    """
    lote = db.query(Lote).filter(Lote.ip == ip_lote).first()
    if not lote:
        raise ValueError(f"Lote '{ip_lote}' no encontrado")

    prueba = (
        db.query(PruebaMetalurgica)
        .filter(
            PruebaMetalurgica.lote_id == lote.id,
            PruebaMetalurgica.cip.is_(None),
        )
        .order_by(PruebaMetalurgica.id.desc())
        .first()
    )
    if not prueba:
        raise ValueError(
            f"No hay prueba metalúrgica pendiente de etiquetar para '{ip_lote}'. "
            "Todas las pruebas ya tienen CIP asignado."
        )

    if prueba.descartado:
        raise ValueError("No se puede etiquetar una prueba descartada")

    ahora = datetime.now(UTC).replace(tzinfo=None)
    # Se permite etiquetar hasta 5 horas antes de que se cumplan las 48h (es decir, a las 43h)
    if not prueba.fecha_ingreso or ahora < prueba.fecha_ingreso + timedelta(hours=43):
        raise ValueError(
            "La prueba aún no ha completado las horas requeridas (se permite etiquetar 5h antes de las 48h)"
        )

    # Contador independiente: solo CIPs de recuperación (no incluye los de muestreo/laboratorio)
    total_cips = (
        db.query(MapeoCIP)
        .filter(
            MapeoCIP.lote_id == lote.id,
            MapeoCIP.tipo_muestra.in_(
                [
                    TipoMuestra.RECUPERACION_INTERNO,
                    TipoMuestra.RECUPERACION_EXTERNO,
                ]
            ),
        )
        .count()
    )

    # Sufijo diferenciado por tipo
    sufijo = "R" if tipo == TipoMuestra.RECUPERACION_INTERNO else "E"

    # Leer configuración de modo de identificación
    usa_cip = get_pruebas_usa_cip(db)

    # Generamos 2 códigos por si necesitan volver a analizar (contramuestra)
    correlativo1 = total_cips + 1
    correlativo2 = total_cips + 2
    codigo_cip1 = _generar_codigo_recuperacion(lote.ip, lote.id, correlativo1, sufijo, usa_cip)
    codigo_cip2 = _generar_codigo_recuperacion(lote.ip, lote.id, correlativo2, sufijo, usa_cip)

    nuevo_cip1 = MapeoCIP(
        lote_id=lote.id,
        codigo_cip=codigo_cip1,
        laboratorio=None,
        tipo_muestra=tipo,
        fecha_envio=None,
    )
    nuevo_cip2 = MapeoCIP(
        lote_id=lote.id,
        codigo_cip=codigo_cip2,
        laboratorio=None,
        tipo_muestra=tipo,
        fecha_envio=None,
    )
    db.add_all([nuevo_cip1, nuevo_cip2])

    prueba.cip = codigo_cip1
    prueba.modificado_por = usuario_id

    db.flush()

    modo_label = "CIPs" if usa_cip else "identificadores"
    return EtiquetadoPruebaOut(
        ip=ip_lote,
        cip=codigo_cip1,
        tipo=tipo,
        mensaje=f"{modo_label} de recuperación ({tipo}) generados: {codigo_cip1} y {codigo_cip2}",
    )


# ── Descartar prueba ─────────────────────────────────────────────────────────────


def descartar_prueba(
    db: Session,
    ip_lote: str,
    motivo: str,
    usuario_id: int,
) -> PruebaMetalurgica:
    """Marca la prueba más reciente como descartada.
    Mantiene el registro para trazabilidad de insumos gastados
    pero no se toma para etiquetado ni análisis."""
    lote = db.query(Lote).filter(Lote.ip == ip_lote).first()
    if not lote:
        raise ValueError(f"Lote '{ip_lote}' no encontrado")

    prueba = (
        db.query(PruebaMetalurgica)
        .filter(
            PruebaMetalurgica.lote_id == lote.id,
            PruebaMetalurgica.descartado == False,  # noqa: E712
        )
        .order_by(PruebaMetalurgica.id.desc())
        .first()
    )
    if not prueba:
        raise ValueError(f"No hay prueba activa para descartar en '{ip_lote}'")

    prueba.descartado = True
    prueba.descartado_por = usuario_id
    prueba.fecha_descarte = datetime.now(UTC).replace(tzinfo=None)
    prueba.motivo_descarte = motivo
    prueba.modificado_por = usuario_id

    db.flush()
    db.refresh(prueba)
    return prueba


# ── Adición acumulativa ────────────────────────────────────────────────────────


def registrar_adicion(
    db: Session,
    ip_lote: str,
    datos: AdicionRequest,
    usuario_id: int,
) -> PruebaMetalurgica:
    """Suma la adición parcial de NaCN/NaOH al acumulado de la prueba en proceso."""
    lote = db.query(Lote).filter(Lote.ip == ip_lote).first()
    if not lote:
        raise ValueError(f"Lote '{ip_lote}' no encontrado")

    prueba = (
        db.query(PruebaMetalurgica)
        .filter(
            PruebaMetalurgica.lote_id == lote.id,
            PruebaMetalurgica.descartado == False,  # noqa: E712
        )
        .order_by(PruebaMetalurgica.id.desc())
        .first()
    )
    if not prueba:
        raise ValueError(f"No hay prueba activa para '{ip_lote}'")
    if not prueba.fecha_ingreso:
        raise ValueError("La prueba aún no ha iniciado (sin fecha de ingreso)")

    from decimal import Decimal

    if datos.adicion_nacn is not None and datos.adicion_nacn > 0:
        actual = prueba.adicion_nacn or Decimal("0")
        prueba.adicion_nacn = actual + Decimal(str(datos.adicion_nacn))
    if datos.adicion_naoh is not None and datos.adicion_naoh > 0:
        actual = prueba.adicion_naoh or Decimal("0")
        prueba.adicion_naoh = actual + Decimal(str(datos.adicion_naoh))
    if datos.porcentaje_nacn is not None:
        prueba.porcentaje_nacn = Decimal(str(datos.porcentaje_nacn))

    prueba.modificado_por = usuario_id

    db.flush()
    db.refresh(prueba)
    return prueba


# ── Pruebas listas para recuperación ─────────────────────────────────────────


def obtener_pruebas_para_recuperacion(db: Session) -> list[PruebaRecuperacionItem]:
    """
    Retorna pruebas COMPLETADO (48h) que:
    1. Tienen al menos 1 CIP de tipo RecuperacionInterno.
    2. El lote tiene ley planta calculable (al menos 1 análisis de ley vigente).
    Usado por Comercial para crear el registro pendiente de recuperación.
    """
    ahora = datetime.now(UTC).replace(tzinfo=None)

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


# ── Recuperaciones ────────────────────────────────────────────────────────────

_OZ_TC_TO_GR_TM = Decimal("34.2857")


def obtener_recuperaciones(db: Session) -> list[RecuperacionItem]:
    """Retorna todos los análisis de recuperación vigentes con leyes de cola y
    % recuperación. Usado por TecnicoMuestreo en su vista de resultados.
    """
    registros = (
        db.query(AnalisisRecuperacion)
        .filter(
            AnalisisRecuperacion.vigente == True,  # noqa: E712
            AnalisisRecuperacion.ley_cola != None,  # noqa: E711
        )
        .order_by(AnalisisRecuperacion.fecha_analisis.desc())
        .all()
    )

    resultado: list[RecuperacionItem] = []
    for rec in registros:
        # Obtener IP y proveedor a través del CIP → lote
        ip = None
        proveedor = "-"
        if rec.cip:
            mapeo = db.query(MapeoCIP).filter(MapeoCIP.codigo_cip == rec.cip).first()
            if mapeo:
                lote = db.query(Lote).filter(Lote.id == mapeo.lote_id).first()
                if lote:
                    ip = lote.ip
                    try:
                        proveedor = lote.sesion.provacop.proveedor.razon_social
                    except AttributeError:
                        proveedor = "-"

        # Conversiones de unidades
        cola_oz_tc: Decimal | None = rec.ley_cola
        cola_gr_tm = (
            (cola_oz_tc * _OZ_TC_TO_GR_TM).quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)
            if cola_oz_tc is not None
            else None
        )
        # ley_liquido en DB está en oz/TC → convertir a g/m³
        solucion_au = (
            (rec.ley_liquido * _OZ_TC_TO_GR_TM).quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)
            if rec.ley_liquido is not None
            else None
        )

        # Obtener ley Ag de la tabla analisis_ley para el lote
        ley_ag_record = None
        if rec.cip:
            mapeo = db.query(MapeoCIP).filter(MapeoCIP.codigo_cip == rec.cip).first()
            if mapeo:
                ley_ag_record = (
                    db.query(AnalisisLey)
                    .filter(
                        AnalisisLey.lote_id == mapeo.lote_id,
                        AnalisisLey.material == "Ag",
                        AnalisisLey.vigente == True,  # noqa: E712
                    )
                    .order_by(AnalisisLey.id.desc())
                    .first()
                )
        ley_cola_ag_gr_tm = (
            Decimal(str(ley_ag_record.ley_gr_tm))
            if ley_ag_record and ley_ag_record.ley_gr_tm
            else None
        )

        resultado.append(
            RecuperacionItem(
                ip=ip or "-",
                cip=rec.cip,
                proveedor=proveedor,
                fecha_analisis=rec.fecha_analisis,
                ley_cola_au_oz_tc=cola_oz_tc,
                ley_cola_au_gr_tm=cola_gr_tm,
                ley_cola_ag_gr_tm=ley_cola_ag_gr_tm,
                solucion_au_g_m3=solucion_au,
                solucion_ag_g_m3=rec.solucion_ag_g_m3,
                recuperacion=rec.recuperacion,
                vigente=rec.vigente,
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
