"""
app/services/balanza_offline.py
================================
Lógica offline para el módulo Balanza (RF-BAL-005).

Dos responsabilidades:
  1. reservar_bloque_ip()  — reserva un rango de IPs para uso offline.
  2. sincronizar_batch()   — recibe sesiones+lotes creados offline y los persiste.

La tabla `configuracion` ya existe con claves:
  - proximo_ip          → siguiente número IP disponible (int como string)
  - tamano_bloque_ip    → cuántos IPs reservar por sync (default "50")
"""

from datetime import datetime
from decimal import Decimal

from app.models.enums import EstadoLote, EstadoSesion
from app.models.models import (
    Configuracion,
    Lote,
    Pesaje,
    ProveedorAcopiador,
    SesionDescarga,
)
from app.schemas.balanza_offline import (
    BloqueIPRespuesta,
    LoteOffline,
    ProvAcopCache,
    SesionOffline,
    SyncBatchRequest,
    SyncBatchRespuesta,
    SyncItemResultado,
)
from app.services.balanza import (
    _ahora,
)
from sqlalchemy.orm import Session, joinedload

# ── Helpers de configuración ───────────────────────────────


def _get_config(db: Session, clave: str, default: str) -> str:
    row = db.query(Configuracion).filter(Configuracion.clave == clave).first()
    return row.valor if row else default


def _set_config(db: Session, clave: str, valor: str) -> None:
    row = db.query(Configuracion).filter(Configuracion.clave == clave).first()
    if row:
        row.valor = valor
    else:
        db.add(Configuracion(clave=clave, valor=valor))


# ── 1. Reserva de bloque IP ────────────────────────────────


def reservar_bloque_ip(db: Session) -> BloqueIPRespuesta:
    """
    Reserva un bloque de IPs para operación offline (RF-BAL-005).

    Lee `proximo_ip` y `tamano_bloque_ip` de configuracion,
    calcula el rango [desde, hasta], actualiza el contador y retorna el bloque.

    El frontend usará IPs IP-{desde:04d} … IP-{hasta:04d} offline.
    Al sincronizar, los lotes llegan con esos IPs ya asignados y
    el backend los acepta directamente (UNIQUE constraint los protege).
    """
    desde = int(_get_config(db, "proximo_ip", "1"))
    tamano = int(_get_config(db, "tamano_bloque_ip", "50"))
    hasta = desde + tamano - 1

    # Actualizar contador global — siguiente bloque comenzará en hasta+1
    _set_config(db, "proximo_ip", str(hasta + 1))
    db.flush()

    return BloqueIPRespuesta(
        desde=desde,
        hasta=hasta,
        tamano=tamano,
        formato="IP-{n:04d}",
        anio=_ahora().year,
    )


def reservar_bloque_ticket(db: Session) -> dict:
    """
    Reserva un bloque de números de ticket para operación offline.
    Usa configuracion: proximo_ticket / tamano_bloque_ticket.
    El frontend asignará TK-{n:05d} sin llamar al servidor.
    """
    desde = int(_get_config(db, "proximo_ticket", "1"))
    tamano = int(_get_config(db, "tamano_bloque_ticket", "50"))
    hasta = desde + tamano - 1
    _set_config(db, "proximo_ticket", str(hasta + 1))
    db.flush()
    return {"desde": desde, "hasta": hasta, "tamano": tamano}


# ── 2. Caché de provacops ──────────────────────────────────


def obtener_cache_provacops(db: Session) -> list[ProvAcopCache]:
    """
    Devuelve la lista completa de relaciones proveedor-acopiador activas
    para que el frontend las almacene localmente y las use offline.
    """
    rows = (
        db.query(ProveedorAcopiador)
        .options(
            joinedload(ProveedorAcopiador.proveedor),
            joinedload(ProveedorAcopiador.acopiador),
        )
        # .filter(ProveedorAcopiador.activo == True)  # noqa: E712
        .all()
    )

    result = []
    for pa in rows:
        result.append(
            ProvAcopCache(
                provacop_id=pa.id,
                proveedor_id=pa.proveedor_id,
                proveedor_razon_social=pa.proveedor.razon_social,
                proveedor_ruc=pa.proveedor.ruc,
                acopiador_id=pa.acopiador_id,
                acopiador_razon_social=pa.acopiador.razon_social,
                acopiador_ruc=pa.acopiador.ruc,
                es_propio=pa.proveedor_id == pa.acopiador_id,
            )
        )
    return result


# ── 3. Sync batch ──────────────────────────────────────────


def sincronizar_batch(
    db: Session,
    payload: SyncBatchRequest,
    usuario_id: int,
) -> SyncBatchRespuesta:
    """
    Recibe un batch de sesiones+lotes creados offline y los persiste.

    Orden de procesamiento: sesiones → lotes → pesajes.
    Si un item ya existe (IP duplicado, sesión ya synced), se marca como
    `ya_existia=True` y se continúa — nunca se aborta el batch completo.

    Retorna mapping temp_id → resultado para que el frontend actualice su
    IndexedDB local.
    """
    resultados: list[SyncItemResultado] = []
    ahora = _ahora()

    for sesion_data in payload.sesiones:
        resultado = _sync_sesion(db, sesion_data, usuario_id, ahora)
        resultados.append(resultado)
        db.flush()

    db.commit()

    return SyncBatchRespuesta(
        procesados=len(resultados),
        resultados=resultados,
        ts_servidor=ahora.isoformat(),
    )


def _sync_sesion(
    db: Session,
    data: SesionOffline,
    usuario_id: int,
    ahora: datetime,
) -> SyncItemResultado:
    """Persiste una sesión offline con todos sus lotes."""

    # Verificar si ya fue sincronizada antes (idempotencia por offline_id)
    existente = (
        db.query(SesionDescarga).filter(SesionDescarga.offline_id == data.offline_id).first()
    )
    if existente:
        return SyncItemResultado(
            offline_id=data.offline_id,
            server_id=existente.id,
            ya_existia=True,
            error=None,
            lotes=[],
        )

    try:
        sesion = SesionDescarga(
            provacop_id=data.provacop_id,
            placa=data.placa,
            carreta=data.carreta,
            conductor=data.conductor,
            transportista=data.transportista,
            razon_social=data.razon_social,
            guia_remision=data.guia_remision,
            guia_transporte=data.guia_transporte,
            estado=EstadoSesion.COMPLETO if data.estado == "COMPLETO" else EstadoSesion.EN_PROCESO,
            creado_por=usuario_id,
            creado_en=data.creado_en or ahora,
            offline_id=data.offline_id,
        )
        db.add(sesion)
        db.flush()

        lotes_resultado = []
        for lote_data in data.lotes:
            lote_res = _sync_lote(db, lote_data, sesion.id, usuario_id, ahora)
            lotes_resultado.append(lote_res)

        return SyncItemResultado(
            offline_id=data.offline_id,
            server_id=sesion.id,
            ya_existia=False,
            error=None,
            lotes=lotes_resultado,
        )

    except Exception as e:
        db.rollback()
        return SyncItemResultado(
            offline_id=data.offline_id,
            server_id=None,
            ya_existia=False,
            error=str(e),
            lotes=[],
        )


def _sync_lote(
    db: Session,
    data: LoteOffline,
    sesion_id: int,
    usuario_id: int,
    ahora: datetime,
) -> dict:
    """Persiste un lote offline. El IP ya viene asignado desde el bloque reservado."""

    # Idempotencia: si el IP ya existe, no duplicar
    existente = db.query(Lote).filter(Lote.ip == data.ip).first()
    if existente:
        return {"offline_id": data.offline_id, "ip": data.ip, "ya_existia": True, "error": None}

    try:
        lote = Lote(
            sesion_id=sesion_id,
            ip=data.ip,
            numero_lote=data.numero_lote,
            tipo_material=data.tipo_material,
            estado=EstadoLote.RECEPCIONADO,
            volado=False,
            habilitado_ruma=False,
            creado_por=usuario_id,
            creado_en=data.creado_en or ahora,
        )
        db.add(lote)
        db.flush()

        p = data.pesaje
        pesaje = Pesaje(
            lote_id=lote.id,
            peso_inicial=Decimal(str(p.peso_inicial)),
            peso_final=Decimal(str(p.peso_final)),
            sacos=p.sacos,
            granel=p.granel,
            numero_ticket=None,
            fecha_inicio=p.fecha_inicio or data.creado_en or ahora,
            fecha_fin=p.fecha_fin or ahora,
        )
        db.add(pesaje)
        db.flush()
        db.refresh(pesaje)

        pesaje.numero_ticket = data.numero_ticket or pesaje.id
        db.flush()

        return {"offline_id": data.offline_id, "ip": data.ip, "ya_existia": False, "error": None}

    except Exception as e:
        return {"offline_id": data.offline_id, "ip": data.ip, "ya_existia": False, "error": str(e)}
