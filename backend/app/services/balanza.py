"""
Service — Módulo Balanza
Lógica de negocio: IP secuencial, crear sesión/lote, eliminar, ticket PDF.
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
    ProvAcopDropdown,
    SesionCrear,
    SesionDetalle,
    SesionLista,
)
from sqlalchemy import extract, func
from sqlalchemy.orm import Session, joinedload

# =============================================================================
# CONSTANTES
# =============================================================================

ESTADOS_LOTE_ELIMINABLES = ("RECEPCIONADO", "LIQUIDADO", "FACTURADO")

# =============================================================================
# HELPERS INTERNOS
# =============================================================================


def _ahora() -> datetime:
    return datetime.now(UTC)


def _peso_neto_pesaje(p: Pesaje) -> Decimal:
    """
    peso_final (BRUTO) - peso_inicial (TARA) = peso_neto.
    Alineado con RF-BAL-002 y check constraint ck_pesajes_peso_final_mayor_inicial.
    """
    return (p.peso_final - p.peso_inicial).quantize(Decimal("0.01"))


def _lote_a_detalle(lote: Lote) -> LoteDetalle:
    """Serializa un Lote ORM a LoteDetalle schema."""
    pesaje_vigente = lote.pesajes[0] if lote.pesajes else None
    peso_neto = _peso_neto_pesaje(pesaje_vigente) if pesaje_vigente else None

    return LoteDetalle(
        id=lote.id,
        ip=lote.ip,
        numero_lote=lote.numero_lote,
        tipo_material=lote.tipo_material,
        estado=lote.estado,
        volado=lote.volado,
        peso_neto=peso_neto,
        fecha_pesaje=pesaje_vigente.fecha_fin if pesaje_vigente else None,
        eliminado=lote.eliminado,
        habilitado_ruma=lote.habilitado_ruma,
        fecha_habilitacion=lote.fecha_habilitacion,
        pesaje=pesaje_vigente,
    )


def _sesion_a_lista(sesion: SesionDescarga) -> SesionLista:
    """Serializa SesionDescarga a SesionLista para el grid."""
    provacop = sesion.provacop
    proveedor: Entidad = provacop.proveedor
    acopiador: Entidad = provacop.acopiador
    es_propio = provacop.proveedor_id == provacop.acopiador_id
    lotes_activos = [lot for lot in sesion.lotes if not lot.eliminado]

    return SesionLista(
        id=sesion.id,
        fecha_ingreso=sesion.creado_en,
        proveedor_razon_social=proveedor.razon_social,
        acopiador_razon_social=acopiador.razon_social,
        es_propio=es_propio,
        placa=sesion.placa,
        guia_remision=sesion.guia_remision,
        total_lotes=len(sesion.lotes),
        lotes_activos=len(lotes_activos),
        estado=sesion.estado,
    )


def _sesion_a_detalle(sesion: SesionDescarga) -> SesionDetalle:
    """Serializa SesionDescarga a SesionDetalle schema."""
    provacop = sesion.provacop
    proveedor: Entidad = provacop.proveedor
    acopiador: Entidad = provacop.acopiador
    es_propio = provacop.proveedor_id == provacop.acopiador_id

    return SesionDetalle(
        id=sesion.id,
        provacop_id=sesion.provacop_id,
        proveedor_id=provacop.proveedor_id,
        proveedor_razon_social=proveedor.razon_social,
        proveedor_ruc=proveedor.ruc,
        acopiador_id=provacop.acopiador_id,
        acopiador_razon_social=acopiador.razon_social,
        acopiador_ruc=acopiador.ruc,
        es_propio=es_propio,
        placa=sesion.placa,
        carreta=sesion.carreta,
        conductor=sesion.conductor,
        transportista=sesion.transportista,
        razon_social=sesion.razon_social,
        guia_remision=sesion.guia_remision,
        guia_transporte=sesion.guia_transporte,
        estado=sesion.estado,
        fecha_ingreso=sesion.creado_en,
        lotes=[_lote_a_detalle(lot) for lot in sesion.lotes],
    )


# =============================================================================
# IP SECUENCIAL  (RF-BAL-002)
# Formato: IP-XXXX — contador global, reinicia cada año calendario.
# Ejemplo: el primer lote de 2026: IP-0001; el 99: IP-0099.
# =============================================================================


def generar_ip(db: Session) -> str:
    """
    Genera el siguiente IP secuencial del año en curso.
    Formato: IP-XXXX (4 digitos, cero-relleno).

    Carga los IPs del año en Python y busca el MAX del sufijo numerico.
    La unicidad final la garantiza el UNIQUE constraint de lotes.ip,
    que rechaza la insercion si hay colision por concurrencia.
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
    Lista sesiones con filtros opcionales.
    busqueda: razon social del proveedor, placa o guia remision.
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

    sesiones = q.order_by(SesionDescarga.creado_en.desc()).all()
    return [_sesion_a_lista(s) for s in sesiones]


def crear_sesion(db: Session, datos: SesionCrear, usuario_id: int) -> SesionDetalle:
    """Crea una nueva sesion EN_PROCESO (RF-BAL-001)."""
    provacop = (
        db.query(ProveedorAcopiador).filter(ProveedorAcopiador.id == datos.provacop_id).first()
    )
    if not provacop:
        raise ValueError(f"La relacion proveedor-acopiador {datos.provacop_id} no existe")

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
    """Detalle de sesion con todos sus lotes."""
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
        raise ValueError(f"Sesion {sesion_id} no encontrada")
    return _sesion_a_detalle(sesion)


def finalizar_sesion(db: Session, sesion_id: int, usuario_id: int) -> SesionDetalle:
    """Marca la sesion como COMPLETO. Requiere al menos 1 lote activo."""
    sesion = db.query(SesionDescarga).filter(SesionDescarga.id == sesion_id).first()
    if not sesion:
        raise ValueError(f"Sesion {sesion_id} no encontrada")
    if sesion.estado == EstadoSesion.COMPLETO:
        raise ValueError("La sesion ya esta completada")
    lotes_activos = [lot for lot in sesion.lotes if not lot.eliminado]
    if not lotes_activos:
        raise ValueError("No se puede finalizar una sesion sin lotes activos")

    sesion.estado = EstadoSesion.COMPLETO
    sesion.modificado_por = usuario_id
    sesion.modificado_en = _ahora()
    db.flush()

    return obtener_sesion(db, sesion_id)


def pausar_sesion(db: Session, sesion_id: int, usuario_id: int) -> SesionDetalle:
    """Pausa una sesion EN_PROCESO."""
    sesion = db.query(SesionDescarga).filter(SesionDescarga.id == sesion_id).first()
    if not sesion:
        raise ValueError(f"Sesion {sesion_id} no encontrada")
    if sesion.estado != EstadoSesion.EN_PROCESO:
        raise ValueError("Solo se pueden pausar sesiones EN_PROCESO")

    sesion.estado = EstadoSesion.PAUSADO
    sesion.modificado_por = usuario_id
    sesion.modificado_en = _ahora()
    db.flush()

    return obtener_sesion(db, sesion_id)


def reanudar_sesion(db: Session, sesion_id: int, usuario_id: int) -> SesionDetalle:
    """Reanuda una sesion PAUSADA a EN_PROCESO."""
    sesion = db.query(SesionDescarga).filter(SesionDescarga.id == sesion_id).first()
    if not sesion:
        raise ValueError(f"Sesion {sesion_id} no encontrada")
    if sesion.estado != EstadoSesion.PAUSADO:
        raise ValueError("Solo se pueden reanudar sesiones PAUSADAS")

    sesion.estado = EstadoSesion.EN_PROCESO
    sesion.modificado_por = usuario_id
    sesion.modificado_en = _ahora()
    db.flush()

    return obtener_sesion(db, sesion_id)


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
    Agrega un lote con su pesaje a una sesion activa (RF-BAL-002).
    Genera IP secuencial automaticamente y calcula peso_neto.
    """
    sesion = db.query(SesionDescarga).filter(SesionDescarga.id == sesion_id).first()
    if not sesion:
        raise ValueError(f"Sesion {sesion_id} no encontrada")
    if sesion.estado == EstadoSesion.COMPLETO:
        raise ValueError("No se pueden agregar lotes a una sesion COMPLETO")

    numero_lote = (
        db.query(func.count(Lote.id)).filter(Lote.sesion_id == sesion_id).scalar() or 0
    ) + 1

    ip = generar_ip(db)
    numero_ticket = f"TK-{ip}"
    ahora = _ahora()
    p = datos.pesaje
    peso_neto = (p.peso_final - p.peso_inicial).quantize(Decimal("0.01"))

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

    db.add(
        Pesaje(
            lote_id=lote.id,
            peso_inicial=p.peso_inicial,
            peso_final=p.peso_final,
            peso_neto=peso_neto,
            sacos=p.sacos,
            granel=p.granel,
            numero_ticket=numero_ticket,
            fecha_inicio=p.fecha_inicio or ahora,
            fecha_fin=ahora,
        )
    )
    db.flush()

    # Recarga con joinedload para que _lote_a_detalle tenga pesajes disponibles
    lote_cargado = db.query(Lote).options(joinedload(Lote.pesajes)).filter(Lote.id == lote.id).one()
    return _lote_a_detalle(lote_cargado)


def eliminar_lote(
    db: Session,
    sesion_id: int,
    lote_id: int,
    datos: EliminarLoteRequest,
    usuario_id: int,
) -> None:
    """
    Soft delete de lote con snapshot de auditoria (RF-BAL-004).
    No se puede eliminar si estado == PAGADO.
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
        raise ValueError(f"Lote {lote_id} no encontrado en sesion {sesion_id}")
    if lote.eliminado:
        raise ValueError("El lote ya fue eliminado")
    if lote.estado == EstadoLote.PAGADO:
        raise ValueError("No se puede eliminar un lote con estado PAGADO")
    if lote.estado not in ESTADOS_LOTE_ELIMINABLES:
        raise ValueError(f"Solo se pueden eliminar lotes en estado: {ESTADOS_LOTE_ELIMINABLES}")

    provacop = lote.sesion.provacop
    proveedor = provacop.proveedor
    acopiador = provacop.acopiador
    pesaje_vigente = lote.pesajes[0] if lote.pesajes else None

    snapshot = {
        "ip": lote.ip,
        "proveedor_ruc": proveedor.ruc,
        "proveedor_razon_social": proveedor.razon_social,
        "acopiador_ruc": acopiador.ruc,
        "acopiador_razon_social": acopiador.razon_social,
        "tipo_material": lote.tipo_material,
        "peso_neto_tm": str(pesaje_vigente.peso_neto) if pesaje_vigente else None,
        "estado_al_eliminar": lote.estado,
        "sesion_id": sesion_id,
        "numero_lote": lote.numero_lote,
    }

    db.add(
        LoteEliminado(
            ip=lote.ip,
            eliminado_por=usuario_id,
            fecha_eliminacion=_ahora(),
            motivo=datos.motivo,
            datos_originales=json.dumps(snapshot, ensure_ascii=False),
        )
    )

    lote.eliminado = True
    lote.eliminado_por = usuario_id
    lote.eliminado_en = _ahora()
    db.flush()


# =============================================================================
# PROVEEDORES-ACOPIADORES  (dropdown en formulario de nueva sesion)
# =============================================================================


def listar_provacop_activos(
    db: Session,
    busqueda: str | None = None,
) -> list[ProvAcopDropdown]:
    """
    Lista relaciones proveedor-acopiador para el autocomplete.
    Filtra por razon social del proveedor si se envia busqueda.
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
        patron = f"%{busqueda}%"
        q = q.filter(proveedor_alias.razon_social.ilike(patron))

    resultados = q.order_by(proveedor_alias.razon_social).limit(20).all()

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
        for pa, prov, acop in resultados
    ]


# =============================================================================
# TICKET PDF  (RF-BAL-003)
# Genera un PDF por lote usando WeasyPrint (ya en pyproject.toml).
# Retorna bytes para enviar como StreamingResponse.
# =============================================================================

_TICKET_CSS = """
@page { size: A5 landscape; margin: 1.5cm; }
body { font-family: 'Courier New', monospace; font-size: 11pt; color: #1a1a1a; }
.header {
    text-align: center; border-bottom: 2px solid #8B6914;
    padding-bottom: 8px; margin-bottom: 12px;
}
.logo { font-size: 16pt; font-weight: bold; color: #5a3e0a; }
.subtitulo { font-size: 9pt; color: #666; }
.ticket-id {
    font-size: 22pt; font-weight: bold; color: #8B6914;
    text-align: center; margin: 12px 0; letter-spacing: 2px;
}
table { width: 100%; border-collapse: collapse; margin-top: 10px; }
td { padding: 4px 8px; }
.label { color: #555; font-size: 9pt; text-transform: uppercase; }
.value { font-weight: bold; font-size: 11pt; }
.pesos { background: #f5f0e8; border-radius: 4px; margin-top: 12px; padding: 8px; }
.peso-row { display: flex; justify-content: space-between; margin: 4px 0; }
.footer {
    margin-top: 16px; border-top: 1px dashed #ccc;
    padding-top: 8px; font-size: 8pt; color: #888; text-align: center;
}
"""


def generar_ticket_pdf(db: Session, sesion_id: int, lote_id: int) -> bytes:
    """
    Genera el ticket PDF para un lote especifico (RF-BAL-003).
    Retorna bytes listos para StreamingResponse.
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
        raise ValueError(f"Lote {lote_id} no encontrado")

    sesion = lote.sesion
    provacop = sesion.provacop
    proveedor = provacop.proveedor
    acopiador = provacop.acopiador
    pesaje = lote.pesajes[0] if lote.pesajes else None
    es_propio = provacop.proveedor_id == provacop.acopiador_id

    peso_bruto = pesaje.peso_final if pesaje else Decimal("0")  # cargado
    peso_tara = pesaje.peso_inicial if pesaje else Decimal("0")  # vacio
    peso_neto = pesaje.peso_neto if pesaje else Decimal("0")
    fecha_str = sesion.creado_en.strftime("%d/%m/%Y %H:%M") if sesion.creado_en else "-"

    acopiador_html = (
        ""
        if es_propio
        else (
            f'<tr><td class="label">Acopiador</td>'
            f'<td class="value">{acopiador.razon_social}</td></tr>'
        )
    )

    ticket_num = pesaje.numero_ticket if pesaje else "-"
    sacos_val = pesaje.sacos if pesaje and pesaje.sacos else "-"
    granel_val = "Si" if pesaje and pesaje.granel else "No"

    html = (
        f"<!DOCTYPE html><html lang='es'><head><meta charset='UTF-8'>"
        f"<style>{_TICKET_CSS}</style></head><body>"
        f"<div class='header'>"
        f"<div class='logo'>INVERMIN PAITITI S.A.C.</div>"
        f"<div class='subtitulo'>TICKET DE RECEPCION DE MINERAL</div>"
        f"</div>"
        f"<div class='ticket-id'>{lote.ip}</div>"
        f"<table>"
        f"<tr><td class='label'>Proveedor</td><td class='value'>{proveedor.razon_social}</td>"
        f"<td class='label'>RUC</td><td class='value'>{proveedor.ruc or '-'}</td></tr>"
        f"{acopiador_html}"
        f"<tr><td class='label'>Placa</td><td class='value'>{sesion.placa}</td>"
        f"<td class='label'>Conductor</td><td class='value'>{sesion.conductor or '-'}</td></tr>"
        f"<tr><td class='label'>Tipo Material</td><td class='value'>{lote.tipo_material or '-'}</td>"
        f"<td class='label'>Fecha Ingreso</td><td class='value'>{fecha_str}</td></tr>"
        f"<tr><td class='label'>Guia Remision</td><td class='value'>{sesion.guia_remision or '-'}</td>"
        f"<td class='label'>Guia Transporte</td><td class='value'>{sesion.guia_transporte or '-'}</td></tr>"
        f"<tr><td class='label'>Sacos</td><td class='value'>{sacos_val}</td>"
        f"<td class='label'>Granel</td><td class='value'>{granel_val}</td></tr>"
        f"</table>"
        f"<div class='pesos'>"
        f"<div class='peso-row'><span class='label'>PESO BRUTO (TMH)</span>"
        f"<span class='value'>{peso_bruto:.3f} TM</span></div>"
        f"<div class='peso-row'><span class='label'>PESO TARA (TMH)</span>"
        f"<span class='value'>{peso_tara:.3f} TM</span></div>"
        f"<div class='peso-row'><span class='label'>PESO NETO (TMH)</span>"
        f"<span class='value' style='color:#2d6a2d;font-size:15pt;'>{peso_neto:.3f} TM</span></div>"
        f"</div>"
        f"<div class='footer'>N Ticket: {ticket_num} | "
        f"Lote #{lote.numero_lote} | Estado: {lote.estado}</div>"
        f"</body></html>"
    )

    try:
        from weasyprint import HTML

        return HTML(string=html).write_pdf()
    except ImportError as exc:
        raise RuntimeError(
            "WeasyPrint no esta instalado. Instalar con: pip install weasyprint"
        ) from exc
