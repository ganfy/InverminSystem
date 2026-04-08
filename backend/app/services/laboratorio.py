"""
Dos flujos diferenciados por rol:
  1. Laboratorista: registra análisis por CIP (nunca ve ni recibe IPs)
  2. Comercial/Gerencia/Admin: ve por IP, sube certificados, descarta análisis
"""

import os
import uuid
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from app.models.enums import TipoAnalisis
from app.models.models import (
    AnalisisLey,
    AnalisisRecuperacion,
    Lote,
    MapeoCIP,
    ProveedorAcopiador,
    SesionDescarga,
)
from app.schemas.laboratorio import (
    AnalisisLeyCreate,
    AnalisisLeyOut,
    AnalisisRecuperacionCreate,
    AnalisisRecuperacionOut,
    CIPAnalisisOut,
    LoteLabOut,
    SyncLaboratorioRequest,
    SyncLaboratorioResponse,
    SyncResultado,
)
from fastapi import UploadFile
from sqlalchemy.orm import Session, joinedload

FACTOR_OZ_TC = Decimal("34.2857")
STORAGE_PATH = Path(os.getenv("STORAGE_PATH", "storage"))
TIPOS_PERMITIDOS = {"pdf", "jpg", "jpeg", "png"}
MAX_FILE_SIZE = 10 * 1024 * 1024


# ── Helpers de cálculo ────────────────────────────────────────────────────────


def _calcular_ley_final(fino: Decimal, grueso: Decimal) -> Decimal:
    return (fino + grueso).quantize(Decimal("0.0001"))


def _calcular_ley_gr_tm(ley_final: Decimal) -> Decimal:
    return (ley_final * FACTOR_OZ_TC).quantize(Decimal("0.001"))


# ── Serializadores ────────────────────────────────────────────────────────────


def _ley_out(a: AnalisisLey, lote_ip: str | None = None) -> AnalisisLeyOut:
    return AnalisisLeyOut(
        id=a.id,
        lote_id=a.lote_id,
        lote_ip=lote_ip,
        cip=a.cip,
        laboratorio=a.laboratorio,
        tipo_analisis=a.tipo_analisis,
        material=a.material or "Au",
        ley_fino=a.ley_fino or Decimal("0"),
        ley_grueso=a.ley_grueso or Decimal("0"),
        ley_final=a.ley_final or Decimal("0"),
        ley_gr_tm=a.ley_gr_tm or Decimal("0"),
        vigente=a.vigente,
        fecha_analisis=a.fecha_analisis,
        certificado_url=a.certificado_url,
        descartado_por=a.descartado_por,
        fecha_descarte=a.fecha_descarte,
        justificacion_descarte=a.justificacion_descarte,
    )


def _rec_out(a: AnalisisRecuperacion, lote_ip: str | None = None) -> AnalisisRecuperacionOut:
    return AnalisisRecuperacionOut(
        id=a.id,
        lote_id=a.lote_id,
        lote_ip=lote_ip,
        cip=a.cip,
        laboratorio=a.laboratorio,
        ley_cabeza=a.ley_cabeza or Decimal("0"),
        ley_cola=a.ley_cola or Decimal("0"),
        ley_liquido=a.ley_liquido,
        recuperacion=a.recuperacion,
        vigente=a.vigente,
        fecha_analisis=a.fecha_analisis,
        certificado_url=a.certificado_url,
        descartado_por=a.descartado_por,
        fecha_descarte=a.fecha_descarte,
    )


# ── Vista Laboratorista: lista por CIP ────────────────────────────────────────


def obtener_cips_laboratorio(
    db: Session,
    incluir_ip: bool = False,
) -> list[CIPAnalisisOut]:
    """
    Lista todos los CIPs generados con su estado de análisis.
    incluir_ip=True → para roles Comercial/Gerencia/Admin que pueden ver el IP.
    incluir_ip=False → Laboratorista nunca ve el IP.
    """
    cips = (
        db.query(MapeoCIP)
        .join(Lote, Lote.id == MapeoCIP.lote_id)
        .filter(Lote.eliminado == False)  # noqa: E712
        .order_by(MapeoCIP.id.desc())
        .all()
    )

    resultados: list[CIPAnalisisOut] = []
    for cip in cips:
        lote = db.query(Lote).filter(Lote.id == cip.lote_id).first()
        if not lote:
            continue

        # Buscar análisis vigentes para este CIP específico
        analisis_ley = (
            db.query(AnalisisLey)
            .filter(AnalisisLey.cip == cip.codigo_cip)
            .order_by(AnalisisLey.id)
            .all()
        )
        analisis_rec = (
            db.query(AnalisisRecuperacion)
            .filter(AnalisisRecuperacion.cip == cip.codigo_cip)
            .order_by(AnalisisRecuperacion.id)
            .all()
        )

        vigentes_ley = [a for a in analisis_ley if a.vigente]
        vigentes_rec = [a for a in analisis_rec if a.vigente]

        estado_ley = "COMPLETADO" if vigentes_ley else "PENDIENTE"
        estado_rec = "COMPLETADO" if vigentes_rec else "PENDIENTE"

        ip = lote.ip if incluir_ip else None

        resultados.append(
            CIPAnalisisOut(
                cip=cip.codigo_cip,
                lote_id=cip.lote_id,
                lote_ip=ip,
                fecha_envio=cip.fecha_envio,
                tipo_muestra=cip.tipo_muestra,
                laboratorio_destino=cip.laboratorio,
                estado_ley=estado_ley,
                estado_recuperacion=estado_rec,
                analisis_ley=[_ley_out(a, ip) for a in analisis_ley],
                analisis_recuperacion=[_rec_out(a, ip) for a in analisis_rec],
            )
        )

    return resultados


# ── Vista Comercial: lista por Lote/IP ────────────────────────────────────────


def obtener_lotes_laboratorio(db: Session) -> list[LoteLabOut]:
    """Lista los lotes que tienen al menos un CIP generado. Para Comercial."""
    # Subconsulta: lote_ids con CIPs
    lote_ids_con_cip = db.query(MapeoCIP.lote_id).distinct().subquery()

    lotes = (
        db.query(Lote)
        .filter(
            Lote.id.in_(lote_ids_con_cip),
            Lote.eliminado == False,  # noqa: E712
        )
        .options(
            joinedload(Lote.sesion)
            .joinedload(SesionDescarga.provacop)
            .joinedload(ProveedorAcopiador.proveedor),
            joinedload(Lote.mapeo_cip),
        )
        .order_by(Lote.id.desc())
        .all()
    )

    resultados: list[LoteLabOut] = []
    for lote in lotes:
        try:
            proveedor = lote.sesion.provacop.proveedor.razon_social
        except AttributeError:
            proveedor = "-"

        cips = [m.codigo_cip for m in (lote.mapeo_cip or [])]

        analisis_ley = (
            db.query(AnalisisLey)
            .filter(AnalisisLey.lote_id == lote.id)
            .order_by(AnalisisLey.id)
            .all()
        )
        analisis_rec = (
            db.query(AnalisisRecuperacion)
            .filter(AnalisisRecuperacion.lote_id == lote.id)
            .order_by(AnalisisRecuperacion.id)
            .all()
        )

        resultados.append(
            LoteLabOut(
                ip=lote.ip,
                lote_id=lote.id,
                proveedor=proveedor,
                material=lote.tipo_material,
                fecha_recepcion=lote.creado_en,
                cips=cips,
                analisis_ley=[_ley_out(a, lote.ip) for a in analisis_ley],
                analisis_recuperacion=[_rec_out(a, lote.ip) for a in analisis_rec],
                tiene_dirimencia=bool(lote.dirimencia),
            )
        )

    return resultados


def obtener_detalle_lote(db: Session, ip: str) -> LoteLabOut | None:
    """Detalle completo de un lote con TODOS sus análisis (incluyendo descartados)."""
    lote = (
        db.query(Lote)
        .options(
            joinedload(Lote.sesion)
            .joinedload(SesionDescarga.provacop)
            .joinedload(ProveedorAcopiador.proveedor),
            joinedload(Lote.mapeo_cip),
        )
        .filter(Lote.ip == ip, Lote.eliminado == False)  # noqa: E712
        .first()
    )
    if not lote:
        return None

    try:
        proveedor = lote.sesion.provacop.proveedor.razon_social
    except AttributeError:
        proveedor = "-"

    cips = [m.codigo_cip for m in (lote.mapeo_cip or [])]

    analisis_ley = (
        db.query(AnalisisLey).filter(AnalisisLey.lote_id == lote.id).order_by(AnalisisLey.id).all()
    )
    analisis_rec = (
        db.query(AnalisisRecuperacion)
        .filter(AnalisisRecuperacion.lote_id == lote.id)
        .order_by(AnalisisRecuperacion.id)
        .all()
    )

    return LoteLabOut(
        ip=lote.ip,
        lote_id=lote.id,
        proveedor=proveedor,
        material=lote.tipo_material,
        fecha_recepcion=lote.creado_en,
        cips=cips,
        analisis_ley=[_ley_out(a, lote.ip) for a in analisis_ley],
        analisis_recuperacion=[_rec_out(a, lote.ip) for a in analisis_rec],
        tiene_dirimencia=bool(lote.dirimencia),
    )


# ── Registro de análisis ──────────────────────────────────────────────────────


def registrar_analisis_ley(db: Session, datos: AnalisisLeyCreate, usuario_id: int) -> AnalisisLey:
    mapeo = db.query(MapeoCIP).filter(MapeoCIP.codigo_cip == datos.cip).first()
    if not mapeo:
        raise ValueError(f"Código CIP '{datos.cip}' no encontrado en el sistema")

    # Dirimencia: invalidar análisis previos vigentes del mismo lote
    if datos.tipo_analisis == TipoAnalisis.DIRIMENCIA:
        previos = (
            db.query(AnalisisLey)
            .filter(
                AnalisisLey.lote_id == mapeo.lote_id,
                AnalisisLey.vigente == True,  # noqa: E712
            )
            .all()
        )
        for p in previos:
            p.vigente = False

    ley_final = _calcular_ley_final(datos.ley_fino, datos.ley_grueso)
    ley_gr_tm = _calcular_ley_gr_tm(ley_final)

    nuevo = AnalisisLey(
        lote_id=mapeo.lote_id,
        cip=datos.cip,
        laboratorio=datos.laboratorio,
        tipo_analisis=datos.tipo_analisis,
        material=datos.material,
        ley_fino=datos.ley_fino,
        ley_grueso=datos.ley_grueso,
        ley_final=ley_final,
        ley_gr_tm=ley_gr_tm,
        origen_datos=datos.origen_datos,
        fecha_analisis=datos.fecha_analisis,
        vigente=True,
        creado_por=usuario_id,
    )
    db.add(nuevo)
    db.flush()
    db.refresh(nuevo)
    return nuevo


def registrar_analisis_recuperacion(
    db: Session, datos: AnalisisRecuperacionCreate, usuario_id: int
) -> AnalisisRecuperacion:
    mapeo = db.query(MapeoCIP).filter(MapeoCIP.codigo_cip == datos.cip).first()
    if not mapeo:
        raise ValueError(f"Código CIP '{datos.cip}' no encontrado en el sistema")

    if datos.ley_cola >= datos.ley_cabeza:
        raise ValueError("La ley cola debe ser estrictamente menor a la ley cabeza")

    nuevo = AnalisisRecuperacion(
        lote_id=mapeo.lote_id,
        cip=datos.cip,
        laboratorio=datos.laboratorio,
        ley_cabeza=datos.ley_cabeza,
        ley_cola=datos.ley_cola,
        ley_liquido=datos.ley_liquido,
        origen_datos=datos.origen_datos,
        fecha_analisis=datos.fecha_analisis,
        vigente=True,
        creado_por=usuario_id,
    )
    db.add(nuevo)
    db.flush()
    db.refresh(nuevo)
    return nuevo


# ── Acciones de Comercial ─────────────────────────────────────────────────────


def descartar_analisis_ley(
    db: Session, analisis_id: int, justificacion: str, usuario_id: int
) -> AnalisisLey:
    a = db.query(AnalisisLey).filter(AnalisisLey.id == analisis_id).first()
    if not a:
        raise ValueError("Análisis de ley no encontrado")
    a.vigente = False
    a.descartado_por = usuario_id
    a.fecha_descarte = datetime.utcnow()
    a.justificacion_descarte = justificacion
    db.flush()
    return a


def descartar_analisis_recuperacion(
    db: Session, analisis_id: int, justificacion: str, usuario_id: int
) -> AnalisisRecuperacion:
    a = db.query(AnalisisRecuperacion).filter(AnalisisRecuperacion.id == analisis_id).first()
    if not a:
        raise ValueError("Análisis de recuperación no encontrado")
    a.vigente = False
    a.descartado_por = usuario_id
    a.fecha_descarte = datetime.utcnow()
    a.justificacion_descarte = justificacion
    db.flush()
    return a


def subir_certificado(db: Session, analisis_id: int, archivo: UploadFile, tipo: str) -> str:
    contenido = archivo.file.read()
    if len(contenido) > MAX_FILE_SIZE:
        raise ValueError("El archivo supera los 10 MB permitidos")

    ext = Path(archivo.filename or "").suffix.lstrip(".").lower()
    if ext not in TIPOS_PERMITIDOS:
        raise ValueError(f"Tipo de archivo no permitido: .{ext}")

    if tipo == "ley":
        a = db.query(AnalisisLey).filter(AnalisisLey.id == analisis_id).first()
    else:
        a = db.query(AnalisisRecuperacion).filter(AnalisisRecuperacion.id == analisis_id).first()

    if not a:
        raise ValueError("Análisis no encontrado")

    ahora = datetime.utcnow()
    cip_str = (a.cip or "cert").replace("/", "_")
    carpeta = STORAGE_PATH / "certificados" / str(ahora.year) / f"{ahora.month:02d}"
    carpeta.mkdir(parents=True, exist_ok=True)
    nombre = f"{cip_str}_{uuid.uuid4().hex[:8]}.{ext}"
    (carpeta / nombre).write_bytes(contenido)

    ruta = f"/certificados/{ahora.year}/{ahora.month:02d}/{nombre}"
    a.certificado_url = ruta
    db.flush()
    return ruta


# ── Sync Offline ──────────────────────────────────────────────────────────────


def sincronizar_batch(
    db: Session, payload: SyncLaboratorioRequest, usuario_id: int
) -> SyncLaboratorioResponse:
    ley_res: list[SyncResultado] = []
    rec_res: list[SyncResultado] = []

    for item in payload.analisis_ley:
        try:
            nuevo = registrar_analisis_ley(db, item.datos, usuario_id)
            db.flush()
            ley_res.append(
                SyncResultado(offline_id=item.offline_id, server_id=nuevo.id, error=None)
            )
        except Exception as e:
            db.rollback()
            ley_res.append(SyncResultado(offline_id=item.offline_id, server_id=None, error=str(e)))

    for item in payload.analisis_recuperacion:
        try:
            nuevo = registrar_analisis_recuperacion(db, item.datos, usuario_id)
            db.flush()
            rec_res.append(
                SyncResultado(offline_id=item.offline_id, server_id=nuevo.id, error=None)
            )
        except Exception as e:
            db.rollback()
            rec_res.append(SyncResultado(offline_id=item.offline_id, server_id=None, error=str(e)))

    db.commit()
    return SyncLaboratorioResponse(
        resultados_ley=ley_res,
        resultados_recuperacion=rec_res,
    )
