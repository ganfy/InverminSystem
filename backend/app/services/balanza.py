"""
Service — Módulo Balanza
CRUD de sesiones de descarga, lotes y consulta de relaciones proveedor-acopiador.

Para la generación de tickets PDF ver: app/services/balanza_pdf.py
"""

import json
from datetime import UTC, datetime
from decimal import Decimal

from app.models.enums import EstadoLote, EstadoSesion
from app.models.models import (
    Entidad,
    Lote,
    LoteEliminado,
    Pesaje,
    ProveedorAcopiador,
    SesionDescarga,
)
from app.schemas.balanza import (
    EliminarLoteRequest,
    LoteCrear,
    LoteDetalle,
    LoteEditar,
    ProvAcopDropdown,
    SesionCrear,
    SesionDetalle,
    SesionEditar,
    SesionLista,
)
from sqlalchemy import extract, func
from sqlalchemy.orm import Session, joinedload

# =============================================================================
# CONSTANTES DE NEGOCIO
# =============================================================================

#: Estados en los que un lote puede ser eliminado (RF-BAL-004).
#: PAGADO queda excluido explícitamente.
ESTADOS_LOTE_ELIMINABLES = frozenset(
    {EstadoLote.RECEPCIONADO, EstadoLote.LIQUIDADO, EstadoLote.FACTURADO}
)

# =============================================================================
# HELPERS PRIVADOS
# =============================================================================


def _ahora() -> datetime:
    return datetime.now(UTC)


def _peso_neto(peso_inicial: Decimal, peso_final: Decimal) -> Decimal:
    """
    BRUTO (peso_inicial) - TARA (peso_final) = peso_neto.
    Solo se usa para serializar desde Python; la BD lo calcula igual.
    """
    return (peso_inicial - peso_final).quantize(Decimal("0.01"))


def _serializar_lote(lote: Lote) -> LoteDetalle:
    """Mapea un ORM Lote a su schema LoteDetalle."""
    pesaje = lote.pesajes[0] if lote.pesajes else None

    return LoteDetalle(
        id=lote.id,
        ip=lote.ip,
        numero_lote=lote.numero_lote,
        tipo_material=lote.tipo_material,
        estado=lote.estado,
        volado=lote.volado,
        peso_neto=_peso_neto(pesaje.peso_inicial, pesaje.peso_final) if pesaje else None,
        fecha_pesaje=pesaje.fecha_fin if pesaje else None,
        eliminado=lote.eliminado,
        habilitado_ruma=lote.habilitado_ruma,
        fecha_habilitacion=lote.fecha_habilitacion,
        pesaje=pesaje,
    )


def _serializar_sesion_lista(sesion: SesionDescarga) -> SesionLista:
    """Mapea un ORM SesionDescarga a su schema SesionLista (fila de grid)."""
    provacop = sesion.provacop
    lotes_activos = [lot for lot in sesion.lotes if not lot.eliminado]

    return SesionLista(
        id=sesion.id,
        fecha_ingreso=sesion.creado_en,
        proveedor_razon_social=provacop.proveedor.razon_social,
        acopiador_razon_social=provacop.acopiador.razon_social,
        es_propio=provacop.proveedor_id == provacop.acopiador_id,
        placa=sesion.placa,
        guia_remision=sesion.guia_remision,
        total_lotes=len(sesion.lotes),
        lotes_activos=len(lotes_activos),
        estado=sesion.estado,
    )


def _serializar_sesion_detalle(sesion: SesionDescarga) -> SesionDetalle:
    """Mapea un ORM SesionDescarga a su schema SesionDetalle (vista completa)."""
    provacop = sesion.provacop
    proveedor = provacop.proveedor
    acopiador = provacop.acopiador

    return SesionDetalle(
        id=sesion.id,
        provacop_id=sesion.provacop_id,
        proveedor_id=provacop.proveedor_id,
        proveedor_razon_social=proveedor.razon_social,
        proveedor_ruc=proveedor.ruc,
        acopiador_id=provacop.acopiador_id,
        acopiador_razon_social=acopiador.razon_social,
        acopiador_ruc=acopiador.ruc,
        es_propio=provacop.proveedor_id == provacop.acopiador_id,
        placa=sesion.placa,
        carreta=sesion.carreta,
        conductor=sesion.conductor,
        transportista=sesion.transportista,
        razon_social=sesion.razon_social,
        guia_remision=sesion.guia_remision,
        guia_transporte=sesion.guia_transporte,
        estado=sesion.estado,
        fecha_ingreso=datetime.fromisoformat(sesion.creado_en).astimezone(UTC)
        if isinstance(sesion.creado_en, str)
        else sesion.creado_en.astimezone(UTC),
        lotes=[_serializar_lote(lot) for lot in sesion.lotes],
    )


def _cargar_sesion(db: Session, sesion_id: int) -> SesionDescarga:
    """Query de sesión con todas las relaciones necesarias para serializar."""
    sesion = (
        db.query(SesionDescarga)
        .options(
            joinedload(SesionDescarga.provacop).joinedload(ProveedorAcopiador.proveedor),
            joinedload(SesionDescarga.provacop).joinedload(ProveedorAcopiador.acopiador),
            joinedload(SesionDescarga.lotes).joinedload(Lote.pesajes),
        )
        .filter(SesionDescarga.id == sesion_id)
        .first()
    )
    if not sesion:
        raise ValueError(f"Sesión {sesion_id} no encontrada")
    return sesion


# =============================================================================
# IP SECUENCIAL  (RF-BAL-002)
# Formato: IP-XXXX — contador global, reinicia cada año calendario.
# =============================================================================


def generar_ip(db: Session) -> str:
    """
    Genera el siguiente IP secuencial del año en curso.

    Carga los IPs existentes del año y busca el máximo del sufijo numérico.
    La unicidad final la garantiza el UNIQUE constraint de lotes.ip.
    """
    anio_actual = _ahora().year

    ips_anio = (
        db.query(Lote.ip)
        .filter(
            Lote.ip.like("IP-%"),
            extract("year", Lote.creado_en) == anio_actual,
        )
        .all()
    )

    max_num = 0
    for (ip,) in ips_anio:
        try:
            num = int(ip.split("-")[1])
            if num > max_num:
                max_num = num
        except (IndexError, ValueError):
            pass

    return f"IP-{max_num + 1:04d}"


# =============================================================================
# SESIONES
# =============================================================================


def listar_sesiones(
    db: Session,
    estado: str | None = None,
    fecha_desde: datetime | None = None,
    fecha_hasta: datetime | None = None,
    busqueda: str | None = None,
) -> list[SesionLista]:
    """
    Lista sesiones con filtros opcionales (estado, rango de fecha, texto libre).
    busqueda: razón social del proveedor, placa o guía de remisión.
    """
    q = (
        db.query(SesionDescarga)
        .join(SesionDescarga.provacop)
        .join(ProveedorAcopiador.proveedor.of_type(Entidad))
        .options(
            joinedload(SesionDescarga.provacop).joinedload(ProveedorAcopiador.proveedor),
            joinedload(SesionDescarga.provacop).joinedload(ProveedorAcopiador.acopiador),
            joinedload(SesionDescarga.lotes),
        )
    )

    if estado:
        q = q.filter(SesionDescarga.estado == estado)
    if fecha_desde:
        q = q.filter(SesionDescarga.creado_en >= fecha_desde)
    if fecha_hasta:
        q = q.filter(SesionDescarga.creado_en <= fecha_hasta)
    if busqueda:
        patron = f"%{busqueda}%"
        q = q.filter(
            SesionDescarga.placa.ilike(patron)
            | SesionDescarga.guia_remision.ilike(patron)
            | Entidad.razon_social.ilike(patron)
        )

    return [_serializar_sesion_lista(s) for s in q.order_by(SesionDescarga.creado_en.desc())]


def crear_sesion(db: Session, datos: SesionCrear, usuario_id: int) -> SesionDetalle:
    """Crea una nueva sesión EN_PROCESO (RF-BAL-001)."""
    if not db.query(ProveedorAcopiador).filter(ProveedorAcopiador.id == datos.provacop_id).first():
        raise ValueError(f"La relación proveedor-acopiador {datos.provacop_id} no existe")

    sesion = SesionDescarga(
        provacop_id=datos.provacop_id,
        placa=datos.placa,
        carreta=datos.carreta,
        conductor=datos.conductor,
        transportista=datos.transportista,
        razon_social=datos.razon_social,
        guia_remision=datos.guia_remision,
        guia_transporte=datos.guia_transporte,
        estado=EstadoSesion.EN_PROCESO,
        creado_por=usuario_id,
        creado_en=_ahora(),
    )
    db.add(sesion)
    db.flush()
    return obtener_sesion(db, sesion.id)


def obtener_sesion(db: Session, sesion_id: int) -> SesionDetalle:
    """Retorna el detalle completo de una sesión con todos sus lotes."""
    return _serializar_sesion_detalle(_cargar_sesion(db, sesion_id))


def finalizar_sesion(db: Session, sesion_id: int, usuario_id: int) -> SesionDetalle:
    """Marca la sesión como COMPLETO. Requiere al menos 1 lote activo."""
    sesion = _cargar_sesion(db, sesion_id)
    if sesion.estado == EstadoSesion.COMPLETO:
        raise ValueError("La sesión ya está completada")
    if not any(lot for lot in sesion.lotes if not lot.eliminado):
        raise ValueError("No se puede finalizar una sesión sin lotes activos")

    sesion.estado = EstadoSesion.COMPLETO
    sesion.modificado_por = usuario_id
    sesion.modificado_en = _ahora()
    db.flush()
    return _serializar_sesion_detalle(_cargar_sesion(db, sesion_id))


def pausar_sesion(db: Session, sesion_id: int, usuario_id: int) -> SesionDetalle:
    """Pausa una sesión EN_PROCESO."""
    sesion = _cargar_sesion(db, sesion_id)
    if sesion.estado != EstadoSesion.EN_PROCESO:
        raise ValueError("Solo se pueden pausar sesiones EN_PROCESO")

    sesion.estado = EstadoSesion.PAUSADO
    sesion.modificado_por = usuario_id
    sesion.modificado_en = _ahora()
    db.flush()
    return _serializar_sesion_detalle(_cargar_sesion(db, sesion_id))


def reanudar_sesion(db: Session, sesion_id: int, usuario_id: int) -> SesionDetalle:
    """Reanuda una sesión PAUSADA → EN_PROCESO."""
    sesion = _cargar_sesion(db, sesion_id)
    if sesion.estado != EstadoSesion.PAUSADO:
        raise ValueError("Solo se pueden reanudar sesiones PAUSADAS")

    sesion.estado = EstadoSesion.EN_PROCESO
    sesion.modificado_por = usuario_id
    sesion.modificado_en = _ahora()
    db.flush()
    return _serializar_sesion_detalle(_cargar_sesion(db, sesion_id))


# =============================================================================
# LOTES
# =============================================================================


def agregar_lote(
    db: Session,
    sesion_id: int,
    datos: LoteCrear,
    usuario_id: int,
) -> LoteDetalle:
    """
    Agrega un lote con pesaje a una sesión activa (RF-BAL-002).
    Genera IP secuencial y calcula peso_neto automáticamente.
    """
    sesion = db.query(SesionDescarga).filter(SesionDescarga.id == sesion_id).first()
    if not sesion:
        raise ValueError(f"Sesión {sesion_id} no encontrada")
    if sesion.estado == EstadoSesion.COMPLETO:
        raise ValueError("No se pueden agregar lotes a una sesión COMPLETO")

    numero_lote = (
        db.query(func.count(Lote.id)).filter(Lote.sesion_id == sesion_id).scalar() or 0
    ) + 1

    ahora = _ahora()
    ip = generar_ip(db)
    p = datos.pesaje

    lote = Lote(
        sesion_id=sesion_id,
        ip=ip,
        numero_lote=numero_lote,
        tipo_material=datos.tipo_material,
        estado=EstadoLote.RECEPCIONADO,
        volado=False,
        habilitado_ruma=False,
        creado_por=usuario_id,
        creado_en=ahora,
    )
    db.add(lote)
    db.flush()

    pesaje = Pesaje(
        lote_id=lote.id,
        peso_inicial=p.peso_inicial,
        peso_final=p.peso_final,
        # peso_neto es GENERATED ALWAYS → no enviar
        sacos=p.sacos,
        granel=p.granel,
        numero_ticket=None,
        fecha_inicio=p.fecha_inicio or ahora,
        fecha_fin=ahora,
    )
    db.add(pesaje)
    db.flush()  # obtiene pesaje.id de la secuencia
    db.refresh(pesaje)  # carga peso_neto calculado por la BD

    # Número de ticket: "TK-XXXXX" con padding 5 dígitos, basado en el PK
    pesaje.numero_ticket = f"TK-{pesaje.id:03d}"
    db.flush()

    lote_cargado = db.query(Lote).options(joinedload(Lote.pesajes)).filter(Lote.id == lote.id).one()
    return _serializar_lote(lote_cargado)


def eliminar_lote(
    db: Session,
    sesion_id: int,
    lote_id: int,
    datos: EliminarLoteRequest,
    usuario_id: int,
) -> None:
    """
    Soft delete de lote con snapshot de auditoría (RF-BAL-004).
    Bloquea si estado == PAGADO. Requiere motivo obligatorio.
    """
    lote = (
        db.query(Lote)
        .options(
            joinedload(Lote.sesion)
            .joinedload(SesionDescarga.provacop)
            .joinedload(ProveedorAcopiador.proveedor),
            joinedload(Lote.sesion)
            .joinedload(SesionDescarga.provacop)
            .joinedload(ProveedorAcopiador.acopiador),
            joinedload(Lote.pesajes),
        )
        .filter(Lote.id == lote_id, Lote.sesion_id == sesion_id)
        .first()
    )
    if not lote:
        raise ValueError(f"Lote {lote_id} no encontrado en sesión {sesion_id}")
    if lote.eliminado:
        raise ValueError("El lote ya fue eliminado")
    if lote.estado == EstadoLote.PAGADO:
        raise ValueError("No se puede eliminar un lote con estado PAGADO")
    if lote.estado not in ESTADOS_LOTE_ELIMINABLES:
        raise ValueError(
            f"Solo se pueden eliminar lotes en estado: "
            f"{', '.join(e.value for e in ESTADOS_LOTE_ELIMINABLES)}"
        )

    provacop = lote.sesion.provacop
    pesaje = lote.pesajes[0] if lote.pesajes else None

    db.add(
        LoteEliminado(
            ip=lote.ip,
            eliminado_por=usuario_id,
            fecha_eliminacion=_ahora(),
            motivo=datos.motivo,
            datos_originales=json.dumps(
                {
                    "ip": lote.ip,
                    "proveedor_ruc": provacop.proveedor.ruc,
                    "proveedor_razon_social": provacop.proveedor.razon_social,
                    "acopiador_ruc": provacop.acopiador.ruc,
                    "acopiador_razon_social": provacop.acopiador.razon_social,
                    "tipo_material": lote.tipo_material,
                    "peso_neto_tm": str(pesaje.peso_neto) if pesaje else None,
                    "estado_al_eliminar": lote.estado,
                    "sesion_id": sesion_id,
                    "numero_lote": lote.numero_lote,
                },
                ensure_ascii=False,
            ),
        )
    )

    lote.eliminado = True
    lote.eliminado_por = usuario_id
    lote.eliminado_en = _ahora()
    db.flush()


def editar_sesion(
    db: Session,
    sesion_id: int,
    datos: SesionEditar,
    usuario_id: int,
) -> SesionDetalle:
    """
    Edita la cabecera de una sesión (corrección de errores de registro).

    BD: UPDATE directo sobre sesiones_descarga.
    Si provacop_id cambia, se valida que el par exista y esté activo.
    Los lotes heredan el proveedor a través de la FK sesion→provacop,
    NO almacenan provacop_id directamente → no requiere cascada.
    """
    sesion = _cargar_sesion(db, sesion_id)

    if datos.provacop_id is not None:
        pa = db.query(ProveedorAcopiador).filter(ProveedorAcopiador.id == datos.provacop_id).first()
        if not pa:
            raise ValueError(f"Relación proveedor-acopiador {datos.provacop_id} no existe")
        sesion.provacop_id = datos.provacop_id

    if datos.placa is not None:
        sesion.placa = datos.placa
    if datos.carreta is not None:
        sesion.carreta = datos.carreta
    if datos.conductor is not None:
        sesion.conductor = datos.conductor
    if datos.transportista is not None:
        sesion.transportista = datos.transportista
    if datos.razon_social is not None:
        sesion.razon_social = datos.razon_social
    if datos.guia_remision is not None:
        sesion.guia_remision = datos.guia_remision
    if datos.guia_transporte is not None:
        sesion.guia_transporte = datos.guia_transporte

    sesion.modificado_por = usuario_id
    sesion.modificado_en = _ahora()
    db.flush()
    return _serializar_sesion_detalle(_cargar_sesion(db, sesion_id))


def editar_lote(
    db: Session,
    sesion_id: int,
    lote_id: int,
    datos: LoteEditar,
    usuario_id: int,
) -> LoteDetalle:
    """
    Admin: edita tipo_material y/o datos de pesaje de un lote existente.

    El campo peso_neto es GENERATED ALWAYS en PostgreSQL;
    al actualizar peso_inicial y/o peso_final el motor lo recalcula
    automáticamente (fórmula: peso_inicial - peso_final).
    """
    lote = (
        db.query(Lote)
        .options(joinedload(Lote.pesajes))
        .filter(Lote.id == lote_id, Lote.sesion_id == sesion_id)
        .first()
    )
    if not lote:
        raise ValueError(f"Lote {lote_id} no encontrado en sesión {sesion_id}")
    if lote.eliminado:
        raise ValueError("No se puede editar un lote eliminado")

    if datos.tipo_material is not None:
        lote.tipo_material = datos.tipo_material

    # Editar pesaje si existe
    pesaje = lote.pesajes[0] if lote.pesajes else None
    if pesaje and (
        datos.peso_inicial is not None
        or datos.peso_final is not None
        or datos.sacos is not None
        or datos.granel is not None
    ):
        nuevo_bruto = datos.peso_inicial if datos.peso_inicial is not None else pesaje.peso_inicial
        nuevo_tara = datos.peso_final if datos.peso_final is not None else pesaje.peso_final

        if nuevo_bruto <= nuevo_tara:
            raise ValueError("peso_inicial (bruto) debe ser mayor que peso_final (tara)")

        pesaje.peso_inicial = nuevo_bruto
        pesaje.peso_final = nuevo_tara
        # peso_neto es columna GENERATED → PostgreSQL lo recalcula en flush

        if datos.sacos is not None:
            pesaje.sacos = datos.sacos
        if datos.granel is not None:
            pesaje.granel = datos.granel

    lote.modificado_por = usuario_id
    lote.modificado_en = _ahora()
    db.flush()

    lote_recargado = (
        db.query(Lote).options(joinedload(Lote.pesajes)).filter(Lote.id == lote_id).one()
    )
    return _serializar_lote(lote_recargado)


# =============================================================================
# PROVEEDOR-ACOPIADOR  (autocomplete en formulario nueva sesión)
# =============================================================================


def listar_provacop_activos(
    db: Session,
    busqueda: str | None = None,
) -> list[ProvAcopDropdown]:
    """
    Lista relaciones proveedor-acopiador activas para el autocomplete.
    Filtra por razón social del proveedor si se envía busqueda (max 20 resultados).
    """
    from sqlalchemy.orm import aliased

    proveedor_alias = aliased(Entidad, name="proveedor")
    acopiador_alias = aliased(Entidad, name="acopiador")

    q = (
        db.query(ProveedorAcopiador, proveedor_alias, acopiador_alias)
        .join(proveedor_alias, ProveedorAcopiador.proveedor_id == proveedor_alias.id)
        .join(acopiador_alias, ProveedorAcopiador.acopiador_id == acopiador_alias.id)
        .filter(proveedor_alias.activo.is_(True))
    )

    if busqueda:
        q = q.filter(proveedor_alias.razon_social.ilike(f"%{busqueda}%"))

    return [
        ProvAcopDropdown(
            provacop_id=pa.id,
            proveedor_id=pa.proveedor_id,
            proveedor_razon_social=prov.razon_social,
            proveedor_ruc=prov.ruc,
            acopiador_id=pa.acopiador_id,
            acopiador_razon_social=acop.razon_social,
            acopiador_ruc=acop.ruc,
            es_propio=pa.proveedor_id == pa.acopiador_id,
        )
        for pa, prov, acop in q.order_by(proveedor_alias.razon_social).limit(20)
    ]
