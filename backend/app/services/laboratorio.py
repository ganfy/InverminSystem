"""
Dos flujos diferenciados por rol:
  1. Laboratorista: registra análisis por CIP (nunca ve ni recibe IPs)
  2. Comercial/Gerencia/Admin: ve por IP, sube certificados, descarta análisis
"""

import os
import re
import shutil
import tempfile
import uuid
from datetime import date, datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

from app.models.enums import EstadoRecuperacion, OrigenDatos, TipoAnalisis, TipoMuestra
from app.models.models import (
    AnalisisDetalle,
    AnalisisLey,
    AnalisisRecuperacion,
    Lote,
    MapeoCIP,
    ProveedorAcopiador,
    PruebaMetalurgica,
    SesionDescarga,
)
from app.schemas.laboratorio import (
    AnalisisAgCreate,
    AnalisisAgOut,
    AnalisisLeyCreate,
    AnalisisLeyOut,
    AnalisisRecuperacionCreate,
    AnalisisRecuperacionOut,
    CIPAnalisisOut,
    CIPResumen,
    CompletarRecuperacionRequest,
    EnviarRecuperacionInternaRequest,
    LoteLabOut,
    SyncLaboratorioRequest,
    SyncLaboratorioResponse,
    SyncResultado,
)
from app.services.config_calculo import get_constantes
from app.services.pruebas import calcular_ley_planta
from fastapi import UploadFile
from sqlalchemy.orm import Session, joinedload

STORAGE_PATH = Path(os.getenv("STORAGE_PATH", "storage"))
TIPOS_PERMITIDOS = {"pdf", "jpg", "jpeg", "png"}
MAX_FILE_SIZE = 10 * 1024 * 1024

# ── Helpers de cálculo ────────────────────────────────────────────────────────


def _calcular_ley_final(fino: Decimal, grueso: Decimal) -> Decimal:
    return (Decimal(str(fino)) + Decimal(str(grueso))).quantize(Decimal("0.0001"))


def _calcular_ley_gr_tm(ley_final: Decimal, factor_oz_tc: Decimal) -> Decimal:
    return (Decimal(str(ley_final)) * factor_oz_tc).quantize(Decimal("0.001"))


def _ley_minero(db: Session, lote_id: int) -> Decimal | None:
    """Retorna la ley del análisis tipo minero vigente del lote, si existe."""
    a = (
        db.query(AnalisisLey)
        .filter(
            AnalisisLey.lote_id == lote_id,
            AnalisisLey.tipo_analisis == TipoAnalisis.MINERO,
            AnalisisLey.material == "Au",
            AnalisisLey.vigente == True,  # noqa: E712
        )
        .first()
    )
    return a.ley_final if a else None


def _ley_solo_planta(db: Session, lote_id: int) -> Decimal | None:
    """Solo análisis tipo 'planta' (lab propio). Para display."""
    analisis = (
        db.query(AnalisisLey)
        .filter(
            AnalisisLey.lote_id == lote_id,
            AnalisisLey.vigente == True,  # noqa: E712
            AnalisisLey.tipo_analisis == TipoAnalisis.PLANTA,
            AnalisisLey.material == "Au",
        )
        .all()
    )
    if not analisis:
        return None
    total = sum(a.ley_final for a in analisis if a.ley_final is not None)
    return (total / len(analisis)).quantize(Decimal("0.0001"))


def _ley_solo_externo(db: Session, lote_id: int) -> Decimal | None:
    """Solo análisis tipo 'externo'. Para display."""
    analisis = (
        db.query(AnalisisLey)
        .filter(
            AnalisisLey.lote_id == lote_id,
            AnalisisLey.vigente == True,  # noqa: E712
            AnalisisLey.tipo_analisis == TipoAnalisis.EXTERNO,
            AnalisisLey.material == "Au",
        )
        .all()
    )
    if not analisis:
        return None
    total = sum(a.ley_final for a in analisis if a.ley_final is not None)
    return (total / len(analisis)).quantize(Decimal("0.0001"))


def _ley_dirimencia(db: Session, lote_id: int) -> Decimal | None:
    """Ley del análisis de dirimencia vigente, si existe."""
    a = (
        db.query(AnalisisLey)
        .filter(
            AnalisisLey.lote_id == lote_id,
            AnalisisLey.tipo_analisis == TipoAnalisis.DIRIMENCIA,
            AnalisisLey.vigente == True,  # noqa: E712
            AnalisisLey.material == "Au",
        )
        .first()
    )
    return Decimal(str(a.ley_final)) if a and a.ley_final else None


def _nombres_usuarios(db: Session, ids: set[int]) -> dict[int, str]:
    """Batch lookup: {user_id: nombre_completo}"""
    if not ids:
        return {}
    from app.models.models import Usuario

    rows = db.query(Usuario.id, Usuario.nombre_completo).filter(Usuario.id.in_(ids)).all()
    return {r.id: r.nombre_completo for r in rows}


def _ag_fields_for_lote(db: Session, lote_id: int) -> dict:
    resultado = obtener_ley_ag_vigente(db, lote_id)
    if resultado is None:
        return {"ley_ag_gr_tm": None, "ley_ag_oz_tc": None}
    gr_tm, oz_tc = resultado
    return {"ley_ag_gr_tm": float(gr_tm), "ley_ag_oz_tc": float(oz_tc)}


# ── Serializadores ────────────────────────────────────────────────────────────


def _ley_out(
    a: AnalisisLey, lote_ip: str | None = None, creado_por_nombre: str | None = None
) -> AnalisisLeyOut:
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
        creado_por_nombre=creado_por_nombre,
    )


def _rec_out(
    a: AnalisisRecuperacion, lote_ip: str | None = None, creado_por_nombre: str | None = None
) -> AnalisisRecuperacionOut:
    return AnalisisRecuperacionOut(
        id=a.id,
        lote_id=a.lote_id,
        lote_ip=lote_ip,
        cip=a.cip,
        laboratorio=a.laboratorio,
        ley_cabeza=a.ley_cabeza if a.ley_cabeza is not None else Decimal("0"),
        ley_cola=a.ley_cola,
        ley_liquido=a.ley_liquido,
        ley_cola_ag_gr_tm=a.ley_cola_ag_gr_tm,
        solucion_ag_g_m3=a.solucion_ag_g_m3,
        recuperacion=a.recuperacion,
        estado=a.estado,
        vigente=a.vigente,
        fecha_analisis=a.fecha_analisis,
        certificado_url=a.certificado_url,
        descartado_por=a.descartado_por,
        fecha_descarte=a.fecha_descarte,
        creado_por_nombre=creado_por_nombre,
    )


# ── Vista Laboratorista: lista por CIP ────────────────────────────────────────


def obtener_cips_laboratorio(
    db: Session,
    incluir_ip: bool = False,
) -> list[CIPAnalisisOut]:
    """
    Lista todos los CIPs con su estado de análisis.
    - CIPs tipo Laboratorio: estado_ley indica si hay análisis de ley.
    - CIPs tipo Recuperacion*: estado_recuperacion indica si hay análisis pendiente/completo.
    incluir_ip=False para Laboratorista (confidencialidad).
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
        if not incluir_ip and cip.laboratorio not in [
            "Paititi",
            "Laboratorio Interno",
            "El Dorado - Invermin Paititi",
        ]:
            continue
        lote = db.query(Lote).filter(Lote.id == cip.lote_id).first()
        if not lote:
            continue

        analisis_ley = (
            db.query(AnalisisLey)
            .filter(AnalisisLey.cip == cip.codigo_cip)
            .order_by(AnalisisLey.id)
            .all()
        )
        analisis_rec = (
            db.query(AnalisisRecuperacion)
            .filter(
                AnalisisRecuperacion.cip == cip.codigo_cip,
            )
            .order_by(AnalisisRecuperacion.id)
            .all()
        )

        no_eliminados_ley = [a for a in analisis_ley if not a.eliminado]
        # vigentes_ley = [a for a in no_eliminados_ley if a.vigente]
        estado_ley = "COMPLETADO" if no_eliminados_ley else "PENDIENTE"

        # Estado recuperacion: idem, filtrar eliminados primero
        no_eliminados_rec = [a for a in analisis_rec if not a.eliminado]
        pendiente_rec = any(
            a.estado == EstadoRecuperacion.PENDIENTE and a.vigente for a in no_eliminados_rec
        )
        completado_rec = any(
            a.estado == EstadoRecuperacion.COMPLETADO and a.vigente for a in no_eliminados_rec
        )

        if completado_rec:
            estado_rec = "COMPLETADO"
        elif pendiente_rec:
            estado_rec = "PENDIENTE"
        else:
            estado_rec = "SIN_DATOS"

        ip = lote.ip if incluir_ip else None

        ids = {a.creado_por for a in analisis_ley + analisis_rec if a.creado_por}
        nombres = _nombres_usuarios(db, ids)

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
                analisis_ley=[
                    _ley_out(a, ip, nombres.get(a.creado_por)) for a in no_eliminados_ley
                ],
                analisis_recuperacion=[
                    _rec_out(a, ip, nombres.get(a.creado_por)) for a in no_eliminados_rec
                ],
            )
        )

    return resultados


# ── Vista Comercial: lista por Lote/IP ────────────────────────────────────────


def _build_lote_lab_out(db: Session, lote: Lote) -> LoteLabOut:
    try:
        proveedor = lote.sesion.provacop.proveedor.razon_social
    except AttributeError:
        proveedor = "-"

    todos_cips = db.query(MapeoCIP).filter(MapeoCIP.lote_id == lote.id).all()
    cips = [c.codigo_cip for c in todos_cips]
    cips_detalle = [
        CIPResumen(
            codigo_cip=c.codigo_cip,
            tipo_muestra=c.tipo_muestra,
            laboratorio=c.laboratorio,
        )
        for c in todos_cips
    ]

    todos_analisis_ley = (
        db.query(AnalisisLey)
        .filter(AnalisisLey.lote_id == lote.id)
        .filter(~AnalisisLey.eliminado)
        .order_by(AnalisisLey.id)
        .all()
    )
    # Separar: registros de cert interno vs análisis reales
    analisis_ley = [
        a for a in todos_analisis_ley if a.tipo_analisis not in (TipoAnalisis.COMERCIAL,)
    ]
    cert_ley_rec = next(
        (a for a in todos_analisis_ley if a.tipo_analisis == TipoAnalisis.COMERCIAL and a.vigente),
        None,
    )
    todos_analisis_rec = (
        db.query(AnalisisRecuperacion)
        .filter(AnalisisRecuperacion.lote_id == lote.id)
        .filter(~AnalisisRecuperacion.eliminado)
        .order_by(AnalisisRecuperacion.id)
        .all()
    )
    # Separar cert comercial de análisis reales de laboratorio
    analisis_rec = [a for a in todos_analisis_rec if a.estado != EstadoRecuperacion.CERT_COMERCIAL]
    cert_rec_record = next(
        (
            a
            for a in todos_analisis_rec
            if a.estado == EstadoRecuperacion.CERT_COMERCIAL and a.vigente
        ),
        None,
    )

    ids = {a.creado_por for a in analisis_ley + analisis_rec if a.creado_por}
    nombres = _nombres_usuarios(db, ids)

    pruebas_lote = db.query(PruebaMetalurgica).filter(PruebaMetalurgica.lote_id == lote.id).all()
    _ahora = datetime.now()
    tiene_prueba_pendiente = any(
        p.fecha_ingreso is None or _ahora < p.fecha_ingreso + timedelta(hours=48)
        for p in pruebas_lote
    )

    # CIP de recuperación con prueba COMPLETADA pero sin análisis de recuperación vigente
    cips_con_rec_vigente = {a.cip for a in analisis_rec if a.vigente and not a.eliminado}
    cips_recuperacion = [
        c
        for c in todos_cips
        if c.tipo_muestra in (TipoMuestra.RECUPERACION_INTERNO, TipoMuestra.RECUPERACION_EXTERNO)
    ]
    tiene_cip_listo_sin_enviar = any(
        c.codigo_cip not in cips_con_rec_vigente for c in cips_recuperacion
    )

    # Debug
    import logging

    logger = logging.getLogger(__name__)
    logger.info(
        "cert_ley_url=%s | cert_rec_url=%s | lote=%s",
        cert_ley_rec.certificado_url if cert_ley_rec else None,
        cert_rec_record.certificado_url if cert_rec_record else None,
        lote.ip,
    )

    return LoteLabOut(
        ip=lote.ip,
        lote_id=lote.id,
        proveedor=proveedor,
        material=lote.tipo_material,
        fecha_recepcion=lote.creado_en,
        cips=cips,
        cips_detalle=cips_detalle,
        ley_planta=calcular_ley_planta(db, lote.id),
        ley_minero=_ley_minero(db, lote.id),
        analisis_ley=[_ley_out(a, lote.ip, nombres.get(a.creado_por)) for a in analisis_ley],
        analisis_recuperacion=[
            _rec_out(a, lote.ip, nombres.get(a.creado_por)) for a in analisis_rec
        ],
        tiene_dirimencia=bool(lote.dirimencia),
        **_ag_fields_for_lote(db, lote.id),
        tiene_prueba_pendiente=tiene_prueba_pendiente,
        tiene_cip_listo_sin_enviar=tiene_cip_listo_sin_enviar,
        cert_ley_url=cert_ley_rec.certificado_url if cert_ley_rec else None,
        cert_rec_url=cert_rec_record.certificado_url if cert_rec_record else None,
    )


def obtener_lotes_laboratorio(db: Session) -> list[LoteLabOut]:
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

    return [_build_lote_lab_out(db, lote) for lote in lotes]


def obtener_detalle_lote(db: Session, ip: str) -> LoteLabOut | None:
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
    return _build_lote_lab_out(db, lote)


# ── Registro de análisis ──────────────────────────────────────────────────────


def registrar_analisis_ley(db: Session, datos: AnalisisLeyCreate, usuario_id: int) -> AnalisisLey:
    mapeo = db.query(MapeoCIP).filter(MapeoCIP.codigo_cip == datos.cip).first()
    if not mapeo:
        raise ValueError(f"Código CIP '{datos.cip}' no encontrado en el sistema")

    if mapeo.tipo_muestra not in (None, TipoMuestra.LABORATORIO):
        raise ValueError(
            f"El CIP '{datos.cip}' es de tipo '{mapeo.tipo_muestra}' y no se usa para análisis de ley"
        )

    # Actualizar laboratorio destino en el mapeo
    if datos.laboratorio:
        mapeo.laboratorio = datos.laboratorio or "Paititi"

    # Dirimencia: invalidar análisis previos vigentes del mismo lote
    # if datos.tipo_analisis == TipoAnalisis.DIRIMENCIA:
    #     previos = (
    #         db.query(AnalisisLey)
    #         .filter(
    #             AnalisisLey.lote_id == mapeo.lote_id,
    #             AnalisisLey.vigente == True,  # noqa: E712
    #         )
    #         .all()
    #     )
    #     for p in previos:
    #         p.vigente = False

    # Para Ag: garantizar ley_grueso=0, desactivar Ag anterior vigente
    if datos.material == "Ag":
        datos.ley_grueso = 0.0
        db.query(AnalisisLey).filter(
            AnalisisLey.lote_id == mapeo.lote_id,
            AnalisisLey.material == "Ag",
            AnalisisLey.vigente == True,  # noqa: E712
        ).update({"vigente": False}, synchronize_session="fetch")

    ley_final = _calcular_ley_final(datos.ley_fino, datos.ley_grueso)
    constantes = get_constantes(db)
    ley_gr_tm = _calcular_ley_gr_tm(ley_final, constantes.factor_oz_tc)

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
    if datos.material == "Ag":
        _crear_detalle_ag(db, nuevo.id, datos)
    else:
        _crear_detalles_newmont(db, nuevo.id, datos)
    return nuevo


def registrar_ley_por_ip(
    db: Session,
    ip_lote: str,
    datos,  # AnalisisLeyPorIPCreate
    usuario_id: int,
) -> AnalisisLey:
    """
    Registra ley minero o dirimencia directamente por IP.
    No requiere CIP: la ley minero la presenta el proveedor, no pasa por
    el laboratorio de planta. La dirimencia se registra cuando ya se tiene
    el CIP pero se invoca desde la vista por IP para simplificar el flujo.
    """

    if datos.tipo_analisis not in (TipoAnalisis.MINERO, TipoAnalisis.DIRIMENCIA):
        raise ValueError("Este endpoint solo acepta tipo_analisis 'minero' o 'dirimencia'")

    lote = db.query(Lote).filter(Lote.ip == ip_lote, Lote.eliminado == False).first()  # noqa: E712
    if not lote:
        raise ValueError(f"Lote '{ip_lote}' no encontrado")

    # Dirimencia: invalidar todos los analisis previos vigentes del lote
    # if datos.tipo_analisis == TipoAnalisis.DIRIMENCIA:
    #     previos = (
    #         db.query(AnalisisLey)
    #         .filter(
    #             AnalisisLey.lote_id == lote.id,
    #             AnalisisLey.vigente == True,  # noqa: E712
    #         )
    #         .all()
    #     )
    #     for p in previos:
    #         p.vigente = False

    if datos.material == "Ag":
        datos.ley_grueso = 0.0
        db.query(AnalisisLey).filter(
            AnalisisLey.lote_id == lote.id,
            AnalisisLey.material == "Ag",
            AnalisisLey.vigente == True,  # noqa: E712
        ).update({"vigente": False}, synchronize_session="fetch")

    ley_final = _calcular_ley_final(Decimal(str(datos.ley_fino)), Decimal(str(datos.ley_grueso)))
    constantes = get_constantes(db)
    ley_gr_tm = _calcular_ley_gr_tm(ley_final, constantes.factor_oz_tc)

    nuevo = AnalisisLey(
        lote_id=lote.id,
        cip=None,  # ley minero y dirimencia pueden no tener CIP de planta
        laboratorio=datos.laboratorio,
        tipo_analisis=datos.tipo_analisis,
        material=datos.material,
        ley_fino=Decimal(str(datos.ley_fino)),
        ley_grueso=Decimal(str(datos.ley_grueso)),
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
    if datos.material == "Ag":
        _crear_detalle_ag(db, nuevo.id, datos)

    return nuevo


def registrar_analisis_recuperacion(
    db: Session, datos: AnalisisRecuperacionCreate, usuario_id: int
) -> AnalisisRecuperacion:
    """
    Registro directo (COMPLETADO) de recuperación.
    Usado para: laboratorio externo via certificado, o flujos sin pending previo.
    """
    mapeo = db.query(MapeoCIP).filter(MapeoCIP.codigo_cip == datos.cip).first()
    if not mapeo:
        raise ValueError(f"Código CIP '{datos.cip}' no encontrado en el sistema")

    if datos.ley_cola >= datos.ley_cabeza:
        raise ValueError("La ley cola debe ser estrictamente menor a la ley cabeza")

    # Actualizar laboratorio destino en el mapeo
    if datos.laboratorio:
        mapeo.laboratorio = datos.laboratorio or "Paititi"

    nuevo = AnalisisRecuperacion(
        lote_id=mapeo.lote_id,
        cip=datos.cip,
        laboratorio=datos.laboratorio,
        ley_cabeza=datos.ley_cabeza,
        ley_cola=datos.ley_cola,
        ley_liquido=datos.ley_liquido,
        estado=EstadoRecuperacion.COMPLETADO,
        origen_datos=datos.origen_datos,
        fecha_analisis=datos.fecha_analisis,
        vigente=True,
        creado_por=usuario_id,
    )
    db.add(nuevo)
    db.flush()
    db.refresh(nuevo)
    return nuevo


# ── Flujo de recuperación interna (pendiente → completado) ────────────────────


def enviar_recuperacion_interna(
    db: Session,
    ip_lote: str,
    datos: EnviarRecuperacionInternaRequest,
    usuario_id: int,
) -> AnalisisRecuperacion:
    """
    Comercial crea un registro PENDIENTE de recuperación para el laboratorio interno.
    - Calcula snapshot de ley_cabeza (ley comercial actual).
    - Selecciona el CIP: si datos.cip es None, usa el único RecuperacionInterno del lote.
    - Falla si ya existe un pending vigente para ese CIP.
    """
    lote = db.query(Lote).filter(Lote.ip == ip_lote, Lote.eliminado == False).first()  # noqa: E712
    if not lote:
        raise ValueError(f"Lote '{ip_lote}' no encontrado")

    # Calcular ley comercial (snapshot)
    ley_comercial = datos.ley_cabeza
    if ley_comercial is None:
        raise ValueError(
            "El lote no tiene análisis de ley vigentes. "
            "No es posible determinar la ley cabeza para recuperación."
        )

    # Resolver CIP
    cips_internos = (
        db.query(MapeoCIP)
        .filter(
            MapeoCIP.lote_id == lote.id,
            MapeoCIP.tipo_muestra == TipoMuestra.RECUPERACION_INTERNO,
        )
        .order_by(MapeoCIP.id)
        .all()
    )

    if not cips_internos:
        raise ValueError(
            "El lote no tiene CIPs de recuperación generados. "
            "El técnico debe completar las pruebas metalúrgicas y etiquetar primero."
        )

    if datos.cip:
        cip_obj = next((c for c in cips_internos if c.codigo_cip == datos.cip), None)
        if not cip_obj:
            raise ValueError(f"CIP '{datos.cip}' no es un CIP de RecuperacionInterno de este lote")
    else:
        if len(cips_internos) > 1:
            raise ValueError(
                f"El lote tiene {len(cips_internos)} CIPs de recuperación internos. "
                "Especifique cuál usar con el campo 'cip'."
            )
        cip_obj = cips_internos[0]

    # Actualizar laboratorio destino en el mapeo
    if datos.laboratorio:
        cip_obj.laboratorio = datos.laboratorio or "Paititi"

    cip_obj.fecha_envio = date.today()

    # Verificar que no haya pending vigente para ese CIP
    pending_existente = (
        db.query(AnalisisRecuperacion)
        .filter(
            AnalisisRecuperacion.cip == cip_obj.codigo_cip,
            AnalisisRecuperacion.estado == EstadoRecuperacion.PENDIENTE,
            AnalisisRecuperacion.vigente == True,  # noqa: E712
        )
        .first()
    )
    if pending_existente:
        raise ValueError(
            f"Ya existe un análisis de recuperación PENDIENTE para el CIP '{cip_obj.codigo_cip}'. "
            "El laboratorista aún no lo ha completado."
        )

    nuevo = AnalisisRecuperacion(
        lote_id=lote.id,
        cip=cip_obj.codigo_cip,
        laboratorio=datos.laboratorio,
        ley_cabeza=ley_comercial,  # snapshot: se congela aquí
        ley_cola=None,
        ley_liquido=None,
        estado=EstadoRecuperacion.PENDIENTE,
        origen_datos=OrigenDatos.MANUAL,
        vigente=True,
        creado_por=usuario_id,
    )
    db.add(nuevo)
    db.flush()
    db.refresh(nuevo)
    return nuevo


def _calcular_ley_reco_gr_tm(mineral_mg: Decimal, peso_g: Decimal) -> Decimal:
    """ley (Gr/TM) = mineral_mg / peso_g * 1000"""
    if peso_g == 0:
        raise ValueError("El peso de la muestra no puede ser 0")
    return (Decimal(str(mineral_mg)) / Decimal(str(peso_g)) * 1000).quantize(
        Decimal("0.0001"), rounding=ROUND_HALF_UP
    )


def _promedio_decimal(*values) -> Decimal | None:
    vals = [Decimal(str(v)) for v in values if v is not None]
    if not vals:
        return None
    return (sum(vals) / len(vals)).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)


def _procesar_muestras_reconocimiento(
    db: "Session",
    recuperacion_id: int,
    muestras,  # list[MuestraReconocimientoIn]
    usuario_id: int,
) -> "tuple[Decimal | None, Decimal | None]":
    """
    Crea 3 filas en analisis_detalle por cada muestra física:
      AU1  : mineral_mg=au1_mg, ley=ley_au1 (Gr/TM)
      AU2  : mineral_mg=au2_mg, ley=ley_au2 (Gr/TM)
      AU_AG: mineral_mg=au_ag_mg, ley=ley_ag (Gr/TM)
    Retorna (ley_cola_oz_tc, ley_cola_ag_gr_tm).
    ley_cola_oz_tc = promedio de avg(Au1,Au2) por muestra / 34.2857
    """
    constantes = get_constantes(db)
    leyes_au_gr_tm: list[Decimal] = []
    leyes_ag_gr_tm: list[Decimal] = []

    for m in muestras:
        peso = Decimal(str(m.peso_g))

        ley_au1 = _calcular_ley_reco_gr_tm(m.au1_mg, peso)
        ley_au2 = _calcular_ley_reco_gr_tm(m.au2_mg, peso)
        ley_au_avg = _promedio_decimal(ley_au1, ley_au2)

        # Ag = señal neta: (Au+Ag_mg - avg(Au1,Au2)_mg) / peso * 1000
        au_avg_mg = (Decimal(str(m.au1_mg)) + Decimal(str(m.au2_mg))) / 2
        ag_mg = max(
            Decimal("0"), Decimal(str(m.au_ag_mg)) - au_avg_mg - constantes.blank_correction_ag
        )
        ley_ag = _calcular_ley_reco_gr_tm(ag_mg, peso) if ag_mg > 0 else Decimal("0")

        leyes_au_gr_tm.append(ley_au_avg)
        leyes_ag_gr_tm.append(ley_ag)

        db.add(
            AnalisisDetalle(
                recuperacion_id=recuperacion_id,
                origen="AU1",
                peso=peso,
                mineral_mg=Decimal(str(m.au1_mg)),
                ley=ley_au1,
                numero_ensayo=m.numero_ensayo,
            )
        )
        db.add(
            AnalisisDetalle(
                recuperacion_id=recuperacion_id,
                origen="AU2",
                peso=peso,
                mineral_mg=Decimal(str(m.au2_mg)),
                ley=ley_au2,
                numero_ensayo=m.numero_ensayo,
            )
        )
        db.add(
            AnalisisDetalle(
                recuperacion_id=recuperacion_id,
                origen="AU_AG",
                peso=peso,
                mineral_mg=Decimal(str(m.au_ag_mg)),
                ley=None,
                numero_ensayo=m.numero_ensayo,
            )
        )

    db.flush()

    ley_cola_gr_tm = _promedio_decimal(*leyes_au_gr_tm)
    ley_cola_oz_tc = (
        (ley_cola_gr_tm / constantes.factor_oz_tc).quantize(
            Decimal("0.0001"), rounding=ROUND_HALF_UP
        )
        if ley_cola_gr_tm
        else None
    )
    ley_cola_ag = _promedio_decimal(*leyes_ag_gr_tm)
    return ley_cola_oz_tc, ley_cola_ag


def _crear_detalles_newmont(
    db: "Session",
    analisis_id: int,
    datos,  # AnalisisLeyCreate — necesita campo opcional muestras_detalle
) -> None:
    """
    Crea hasta 3 filas en analisis_detalle con los datos crudos del triple sampling.
    Solo si el payload incluye muestras_detalle (campo opcional, no breaking change).
    Orden esperado: [FINO1, GRUESO, FINO2]
    """
    muestras = getattr(datos, "muestras_detalle", None)
    if not muestras:
        return

    mapa_origen = {0: "FINO1", 1: "GRUESO", 2: "FINO2"}
    for i, m in enumerate(muestras):
        db.add(
            AnalisisDetalle(
                analisis_id=analisis_id,
                origen=mapa_origen.get(i, f"MUESTRA_{i+1}"),
                peso=Decimal(str(m.peso_g)),
                mineral_mg=Decimal(str(m.au_mg)),
                ley=Decimal(str(m.ley_oz_tc)),
                numero_ensayo=1,
            )
        )
    db.flush()


def _crear_detalle_ag(
    db: "Session",
    analisis_id: int,
    datos,  # AnalisisLeyCreate | AnalisisLeyPorIPCreate
) -> None:
    """
    Crea 1 fila en analisis_detalle para análisis de Ag.
    origen = datos.punto (CABEZA | COLA | LIQUIDO).
    ley almacenada en oz/TC (ley_fino del payload).
    """
    if getattr(datos, "material", "Au") != "Ag":
        return
    punto = getattr(datos, "punto", None)
    if not punto:
        return
    db.add(
        AnalisisDetalle(
            analisis_id=analisis_id,
            origen=punto,  # CABEZA | COLA | LIQUIDO
            ley=Decimal(str(datos.ley_fino)),
            numero_ensayo=1,
        )
    )
    db.flush()


def completar_recuperacion(
    db: "Session",
    analisis_id: int,
    datos: "CompletarRecuperacionRequest",
    usuario_id: int,
) -> "AnalisisRecuperacion":
    """
    Laboratorista completa un análisis de recuperación PENDIENTE.

    Flujo A — con muestras crudas (reconocimiento de planta):
      Requiere datos.muestras (list[MuestraReconocimientoIn]).
      Crea filas en analisis_detalle (AU1, AU2, AU_AG) y calcula:
        ley_cola        = promedio leyes Au (convertido a Oz/TC)
        ley_cola_ag_gr_tm = promedio leyes Ag (Gr/TM)

    Flujo B — fallback (certificado externo / sin muestras):
      Requiere datos.ley_cola directo.
      No crea filas de detalle.
    """
    a = (
        db.query(AnalisisRecuperacion)
        .filter(AnalisisRecuperacion.id == analisis_id)
        .filter(~AnalisisRecuperacion.eliminado)
        .first()
    )
    if not a:
        raise ValueError("Análisis de recuperación no encontrado")
    if a.estado != EstadoRecuperacion.PENDIENTE:
        raise ValueError("Solo se pueden completar análisis en estado PENDIENTE")
    if not a.vigente:
        raise ValueError("No se puede completar un análisis descartado")

    # ── Determinar ley_cola ───────────────────────────────────────────────────
    muestras = getattr(datos, "muestras", None)
    if muestras:
        ley_cola, ley_cola_ag = _procesar_muestras_reconocimiento(db, a.id, muestras, usuario_id)
    else:
        if datos.ley_cola is None:
            raise ValueError("Debe ingresar muestras o ley_cola directamente")
        ley_cola = Decimal(str(datos.ley_cola))
        ley_cola_ag = None

    if ley_cola >= a.ley_cabeza:
        raise ValueError("La ley cola debe ser estrictamente menor a la ley cabeza")

    a.ley_cola = ley_cola
    a.ley_liquido = datos.ley_liquido
    a.ley_cola_ag_gr_tm = ley_cola_ag
    a.solucion_ag_g_m3 = getattr(datos, "solucion_ag_g_m3", None)
    a.estado = EstadoRecuperacion.COMPLETADO
    a.fecha_analisis = datos.fecha_analisis
    a.modificado_por = usuario_id
    db.flush()

    # ── Generar Análisis de Ley de Plata (Ag) Automáticamente ──────────
    if ley_cola_ag is not None:
        # Obtenemos el análisis Au padre para heredar el tipo de análisis
        analisis_au = (
            db.query(AnalisisLey)
            .filter(
                AnalisisLey.lote_id == a.lote_id,
                AnalisisLey.material == "Au",
                AnalisisLey.vigente,
            )
            .first()
        )

        tipo_an = analisis_au.tipo_analisis if analisis_au else TipoAnalisis.PLANTA

        # Inactivamos cualquier análisis de Ag previo del lote
        db.query(AnalisisLey).filter(
            AnalisisLey.lote_id == a.lote_id,
            AnalisisLey.material == "Ag",
            AnalisisLey.vigente == True,  # noqa: E712
        ).update({"vigente": False}, synchronize_session="fetch")

        # Calculamos Ag Oz/TC (ley_fino) a partir de Gr/TM
        constantes = get_constantes(db)
        ley_oz_tc = (ley_cola_ag / constantes.factor_oz_tc).quantize(
            Decimal("0.0001"), rounding=ROUND_HALF_UP
        )

        nuevo_ag = AnalisisLey(
            lote_id=a.lote_id,
            cip=a.cip,
            laboratorio=a.laboratorio,
            tipo_analisis=tipo_an,
            material="Ag",
            ley_fino=float(ley_oz_tc),
            ley_grueso=0.0,
            ley_final=float(ley_oz_tc),
            ley_gr_tm=float(ley_cola_ag),
            origen_datos=OrigenDatos.MANUAL,
            fecha_analisis=datos.fecha_analisis,
            vigente=True,
            creado_por=usuario_id,
        )
        db.add(nuevo_ag)
        db.flush()

        # Guardamos el detalle que justifica la ley de Ag creada
        db.add(
            AnalisisDetalle(
                analisis_id=nuevo_ag.id,
                origen="COLA",
                ley=ley_oz_tc,
                numero_ensayo=1,
            )
        )
        db.flush()

    db.refresh(a)
    return a


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


def eliminar_analisis_ley(db: Session, analisis_id: int, usuario_id: int) -> AnalisisLey:
    from datetime import datetime

    a = db.query(AnalisisLey).filter(AnalisisLey.id == analisis_id).first()
    if not a:
        raise ValueError("Analisis de ley no encontrado")
    if a.eliminado:
        raise ValueError("El analisis ya esta eliminado")
    a.eliminado = True
    a.eliminado_en = datetime.now()
    a.eliminado_por = usuario_id
    # Si estaba vigente, marcarlo no vigente tambien para que no afecte calculos
    if a.vigente:
        a.vigente = False
        a.descartado_por = usuario_id
        a.fecha_descarte = a.eliminado_en
        a.justificacion_descarte = "Eliminado por usuario"
    db.flush()
    return a


def eliminar_analisis_recuperacion(
    db: Session, analisis_id: int, usuario_id: int
) -> AnalisisRecuperacion:
    from datetime import datetime

    a = db.query(AnalisisRecuperacion).filter(AnalisisRecuperacion.id == analisis_id).first()
    if not a:
        raise ValueError("Analisis de recuperacion no encontrado")
    if a.eliminado:
        raise ValueError("El analisis ya esta eliminado")
    a.eliminado = True
    a.eliminado_en = datetime.now()
    a.eliminado_por = usuario_id
    if a.vigente:
        a.vigente = False
        a.descartado_por = usuario_id
        a.fecha_descarte = a.eliminado_en
        a.justificacion_descarte = "Eliminado por usuario"
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

    ahora = datetime.now()
    cip_str = (a.cip or "cert").replace("/", "_")
    carpeta = STORAGE_PATH / "certificados" / str(ahora.year) / f"{ahora.month:02d}"
    carpeta.mkdir(parents=True, exist_ok=True)
    nombre = f"{cip_str}_{uuid.uuid4().hex[:8]}.{ext}"
    (carpeta / nombre).write_bytes(contenido)

    ruta = f"certificados/{ahora.year}/{ahora.month:02d}/{nombre}"
    a.certificado_url = ruta
    db.flush()
    return ruta


def extraer_certificado_ley(
    archivo_bytes: bytes, filename: str, laboratorio_hint: str = ""
) -> dict:
    """
    Extrae campos de un certificado PDF/imagen de análisis de ley.
    Detección flexible: no depende del laboratorio específico.
    laboratorio_hint: nombre ingresado por el operador (no se usa para extracción,
                      solo se devuelve como sugerencia de pre-fill).
    """
    texto = _pdf_to_text(archivo_bytes, filename)
    t = texto  # alias para legibilidad

    def _first_float(*patterns):
        for p in patterns:
            m = re.search(p, t, re.IGNORECASE)
            if m:
                try:
                    return float(m.group(1).replace(",", "."))
                except (ValueError, IndexError):
                    pass
        return None

    def _first_str(*patterns):
        for p in patterns:
            m = re.search(p, t, re.IGNORECASE)
            if m:
                try:
                    return m.group(1).strip()
                except IndexError:
                    return m.group(0).strip()
        return None

    # ── N° de informe / certificado ───────────────────────────────────────────
    # Cubre: "Certificado N°: MSSC 001-34764-RLV", "N° LQ IP202601-0046",
    #        "INFORME N° AAS-ELDORADO-0226-084", "REPORT N° ...", "Nro. ..."
    n_informe = _first_str(
        r"CERTIFICADO\s+(?:DE\s+ENSAYO\s+)?N[°oO\u00ba\.]*\s*:?\s*([\w\s\-\/]+?)(?:\n|$)",
        r"INFORME\s+(?:DE\s+ENSAYO\s+)?N[°oO\u00ba\.]*\s*:?\s*([\w\s\-\/]+?)(?:\n|$)",
        r"N[°oO\u00ba\.]+\s+(?:INFORME|LQ|CERT|REPORT|INF)\s*([\w\-\/]+)",
        r"N[°oO\u00ba\.]+\s*([\w]{2,}[-\/][\w\-\/]+)",  # genérico "N° ABC-123"
    )
    if n_informe:
        n_informe = n_informe.strip().rstrip(".")

    # ── CIP / código muestra ──────────────────────────────────────────────────
    # Cubre: "Código Cliente: IP-2793" (Minares), "CODIGO: IP-2620-RM" (Paititi),
    #        valores en tabla "RLV-83 | IP-2793", "CIP-123456X-A2"
    # Estrategia: buscar patrón IP-\d+ o CIP-... cerca de palabras clave
    cip = _first_str(
        # Explícito con etiqueta
        r"C[OÓ]DIGO\s+CLIENTE\s*:?\s*([\w\-]+)",
        r"C[OÓ]DIGO\s+MUESTRA\s*:?\s*([\w\-]+)",
        r"MUESTRA\s*:?\s*(CIP[-\w]+)",
        r"C[OÓ]DIGO\s*:?\s*(IP[-\s]?[\d]+(?:\s*[-\s]\s*\w+)?)",
        # Patrón CIP explícito
        r"(CIP[-\s]*[\w\-]+)",
        # Patrón IP en tabla (valor aislado)
        r"(?:^|\||\s)(IP[-\s]?[\d]{2,5}(?:[-\s]\w{1,4})?)\s*(?:\||$)",
    )
    if cip:
        # Normalizar espacios: "IP 2793" → "IP-2793"
        cip = re.sub(r"^IP\s+", "IP-", cip.strip())

    ley_grueso = _first_float(
        r"MALLA\s*\+\s*1[45]0[\s\S]{0,30}?([\d]+[.,][\d]+)",
        r"MESH\s*\+\s*1[45]0[\s\S]{0,30}?([\d]+[.,][\d]+)",
        r"\+\s*1[45]0[\s\S]{0,30}?([\d]+[.,][\d]+)",
    )
    ley_fino = _first_float(
        r"MALLA\s*-\s*1[45]0[\s\S]{0,30}?([\d]+[.,][\d]+)",
        r"MESH\s*-\s*1[45]0[\s\S]{0,30}?([\d]+[.,][\d]+)",
        r"-\s*1[45]0[\s\S]{0,30}?([\d]+[.,][\d]+)",
    )
    ley_final = _first_float(
        r"LE[YV]\s*FINAL[\s\S]{0,30}?([\d]+[.,][\d]+)",
        r"LE[YV]\s+AU[\s\S]{0,30}?([\d]+[.,][\d]+)",
        r"AU\s*(?:OZ/TC|OZ\.TC|0Z/TC|ozitc|oz/te|o2z/tc)[\s\S]{0,30}?([\d]+[.,][\d]+)",
    )

    # Si las etiquetas están muy separadas de los valores, leemos fila por fila.
    if ley_final is None or ley_fino is None or ley_grueso is None:
        for linea in texto.split("\n"):
            # Encontrar todos los decimales en la línea actual
            floats = re.findall(r"\b\d+\.\d{2,4}\b", linea)

            # Caso 1: La fila tiene al menos 3 números (Grueso, Fino, Final, opcional g/TM)
            # Ej: RLV-83 IP - 2793 0.040 0.519 0.559 19.162
            if len(floats) >= 3:
                # El orden minero estándar de izquierda a derecha suele ser: Malla Gruesa (+), Malla Fina (-), Final
                ley_grueso = float(floats[0])
                ley_fino = float(floats[1])
                ley_final = float(floats[2])
                break

            # Caso 2: La fila tiene exactamente 2 números (Ley Final oz/TC y g/TM)
            elif len(floats) == 2 and ley_final is None:
                f1, f2 = float(floats[0]), float(floats[1])
                # Sabemos que g/TM es ~34.28 veces mayor que oz/TC, así que la Final es el valor menor.
                ley_final = min(f1, f2)

    # ley_gr_tm (referencia, no se guarda en BD - backend lo recalcula)
    ley_gr_tm = _first_float(
        r"G/TM\s*:?\s*([\d]+[.,][\d]+)",
        r"GR/TM\s*:?\s*([\d]+[.,][\d]+)",
        r"G/T\.M\.\s*:?\s*([\d]+[.,][\d]+)",
    )

    # ── Fecha ─────────────────────────────────────────────────────────────────
    # Preferir "Fecha Entrega" o "Fecha Análisis"; fallback "Fecha Recepción"
    fecha_raw = _first_str(
        r"FECHA\s+(?:DE\s+)?ENTREGA\s*:?\s*(\d{1,2}[-\/]\d{1,2}[-\/]\d{2,4})",
        r"FECHA\s+AN[AÁ]LISIS\s*:?\s*(\d{1,2}[-\/]\d{1,2}[-\/]\d{2,4})",
        r"FECHA\s*:?\s*(\d{1,2}[-\/]\d{1,2}[-\/]\d{2,4})",
        r"DATE\s*:?\s*(\d{1,2}[-\/]\d{1,2}[-\/]\d{2,4})",
    )
    fecha_norm = _normalizar_fecha(fecha_raw)

    return {
        "cip": cip,
        "n_informe": n_informe,
        "laboratorio": laboratorio_hint or None,  # operador lo ingresa
        "fecha_analisis": fecha_norm,
        "ley_fino": ley_fino,  # malla -140/-150
        "ley_grueso": ley_grueso,  # malla +140/+150
        "ley_final": ley_final,  # fino + grueso (calculado o extraído)
        "ley_gr_tm": ley_gr_tm,  # referencia
        "texto_raw": texto[:800],
    }


def extraer_certificado_recuperacion(
    archivo_bytes: bytes, filename: str, laboratorio_hint: str = ""
) -> dict:
    """
    Extrae campos de un certificado de análisis de recuperación (AAS, leyes líquido).
    Flexible: funciona para El Dorado AAS y otros formatos.
    El operador provee el laboratorio; aquí solo extraemos valores numéricos.
    """
    texto = _pdf_to_text(archivo_bytes, filename)
    t = texto

    def _first_float(*patterns):
        for p in patterns:
            m = re.search(p, t, re.IGNORECASE)
            if m:
                try:
                    return float(m.group(1).replace(",", "."))
                except (ValueError, IndexError):
                    pass
        return None

    def _first_str(*patterns):
        for p in patterns:
            m = re.search(p, t, re.IGNORECASE)
            if m:
                try:
                    return m.group(1).strip()
                except IndexError:
                    return m.group(0).strip()
        return None

    # N° informe
    n_informe = _first_str(
        r"CERTIFICADO\s+(?:DE\s+ENSAYO\s+)?N[°oO\u00ba\.]*\s*:?\s*([\w\s\-\/]+?)(?:\n|$)",
        r"N[°oO\u00ba\.]+\s*([\w]{2,}[-\/][\w\-\/]+)",
    )

    # CIP para recuperación: patrones REE, IP con sufijos
    cip = _first_str(
        r"C[OÓ]DIGO\s+CLIENTE\s*:?\s*([\w\-]+)",
        r"C[OÓ]DIGO\s*:?\s*(IP[-\s]?[\d]+(?:\s*[-\s]\s*\w+)?)",
        r"(CIP[-\s]*[\w\-]+)",
        r"(?:^|\||\s)(IP[-\s]?[\d]{2,5}(?:[-\s]\w{1,6})?)\s*(?:\||$)",
    )

    # Fecha
    fecha_raw = _first_str(
        r"FECHA\s+(?:DE\s+)?ENTREGA\s*:?\s*(\d{1,2}[-\/]\d{1,2}[-\/]\d{2,4})",
        r"FECHA\s+AN[AÁ]LISIS\s*:?\s*(\d{1,2}[-\/]\d{1,2}[-\/]\d{2,4})",
        r"FECHA\s*:?\s*(\d{1,2}[-\/]\d{1,2}[-\/]\d{2,4})",
    )
    fecha_norm = _normalizar_fecha(fecha_raw)

    # Para AAS El Dorado: "Ley Au g/m3" = g/m3 del líquido
    # Nota: la ley_cabeza viene del sistema (ley planta), no del certificado externo
    ley_liquido_gm3 = _first_float(
        r"LEY\s+AU\s+G/M3\s*:?\s*([\d]+[.,][\d]+)",
        r"G/M3\s*:?\s*([\d]+[.,][\d]+)",
        r"LEY\s+L[IÍ]QUIDO\s*:?\s*([\d]+[.,][\d]+)",
    )

    ley_cola = _first_float(
        r"LEY\s+COLA\s*:?\s*([\d]+[.,][\d]+)",
        r"COLA\s*:?\s*([\d]+[.,][\d]+)",
        r"TAIL\s*:?\s*([\d]+[.,][\d]+)",
    )

    recuperacion = _first_float(
        r"RECUPERACI[OÓ]N\s*:?\s*([\d]+[.,][\d]+)\s*%",
        r"RECOVERY\s*:?\s*([\d]+[.,][\d]+)",
        r"%\s+RECUP\s*:?\s*([\d]+[.,][\d]+)",
    )

    return {
        "cip": cip,
        "n_informe": n_informe if n_informe else None,
        "laboratorio": laboratorio_hint or None,
        "fecha_analisis": fecha_norm,
        "ley_liquido_gm3": ley_liquido_gm3,  # unidad g/m3 (AAS) - diferente a oz/tc
        "ley_cola": ley_cola,
        "recuperacion": recuperacion,
        "texto_raw": texto[:800],
        # ley_cabeza viene del sistema (snapshot al crear pending), no del certificado
    }


def _normalizar_fecha(raw: str | None) -> str | None:
    """dd/mm/yy o dd-mm-yyyy → YYYY-MM-DD."""
    if not raw:
        return None
    for sep in ["/", "-"]:
        parts = raw.split(sep)
        if len(parts) == 3:
            d, mo, y = parts
            if len(y) == 2:
                y = "20" + y
            try:
                return f"{y}-{int(mo):02d}-{int(d):02d}"
            except ValueError:
                pass
    return raw


def _pdf_to_text(archivo_bytes: bytes, filename: str) -> str:
    """Extract text from PDF bytes using pymupdf, fallback to tesseract OCR."""
    tmp = Path(tempfile.mkdtemp())
    try:
        ruta = tmp / filename
        ruta.write_bytes(archivo_bytes)

        def preprocesar_imagen(img_path):
            from PIL import Image

            # Volvemos a lo simple y efectivo: Solo escala de grises y zoom 2x.
            # Sin filtros destructivos (autocontrast, binarize, etc.) que borren los números.
            img = Image.open(str(img_path)).convert("L")
            img = img.resize((img.width * 2, img.height * 2), Image.Resampling.LANCZOS)
            return img

        # Volvemos a psm 4: Ideal para tablas y asume una columna de texto de tamaños variables
        config_ocr = r"--oem 3 --psm 4"

        ext = ruta.suffix.lower()
        if ext in [".jpg", ".jpeg", ".png"]:
            try:
                import pytesseract

                img = preprocesar_imagen(ruta)
                texto = pytesseract.image_to_string(img, lang="spa+eng", config=config_ocr)
                print(f"[OCR TEXTO EXTRAÍDO]\n{texto}\n[FIN OCR]")
                return texto
            except Exception as e:
                print(f"Error OCR Imagen: {e}")
                return ""

        # psm 6 asume un bloque de texto uniforme, ideal para cuando limpiamos todo el fondo
        config_ocr = r"--oem 3 --psm 6"

        ext = ruta.suffix.lower()
        if ext in [".jpg", ".jpeg", ".png"]:
            try:
                import pytesseract

                img = preprocesar_imagen(ruta)
                texto = pytesseract.image_to_string(img, lang="spa+eng", config=config_ocr)
                print(f"[OCR TEXTO EXTRAÍDO]\n{texto}\n[FIN OCR]")
                return texto
            except Exception as e:
                print(f"Error OCR Imagen: {e}")
                return ""

        try:
            import fitz

            doc = fitz.open(str(ruta))
            textos = []
            for page in doc:
                t = page.get_text()
                if t.strip():
                    textos.append(t)
                else:
                    # scanned page → render and OCR
                    try:
                        import pytesseract
                        from PIL import Image

                        mat = fitz.Matrix(2.0, 2.0)
                        pix = page.get_pixmap(matrix=mat)
                        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                        textos.append(pytesseract.image_to_string(img, lang="spa+eng"))
                    except Exception:
                        pass
            doc.close()
            return "\n".join(textos)
        except Exception:
            return ""
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def generar_y_guardar_certificado_interno(db: Session, analisis_id: int, tipo: str) -> str:
    from app.services import certificado_ley_pdf as cert_svc

    if tipo == "ley":
        a = db.query(AnalisisLey).filter(AnalisisLey.id == analisis_id).first()
        if not a:
            raise ValueError("Análisis no encontrado")
        pdf_bytes = cert_svc.generar_certificado_ensayo_cip_pdf(db, a.cip)
    else:
        a = db.query(AnalisisRecuperacion).filter(AnalisisRecuperacion.id == analisis_id).first()
        if not a:
            raise ValueError("Análisis no encontrado")
        pdf_bytes = cert_svc.generar_certificado_recuperacion_cip_pdf(db, a.cip)

    ahora = datetime.now()
    cip_str = (a.cip or "cert").replace("/", "_")
    carpeta = STORAGE_PATH / "certificados" / str(ahora.year) / f"{ahora.month:02d}"
    carpeta.mkdir(parents=True, exist_ok=True)
    nombre = f"{cip_str}_{tipo}_interno_{uuid.uuid4().hex[:8]}.pdf"

    (carpeta / nombre).write_bytes(pdf_bytes)
    ruta = f"certificados/{ahora.year}/{ahora.month:02d}/{nombre}"

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


# ═══════════════════════════════════════════════════════════════════════════════
# Cálculo de ley comercial según parametros_comerciales
# ═══════════════════════════════════════════════════════════════════════════════


def calcular_ley_comercial(
    ley_planta: Decimal, params, umbral_volado: Decimal | None = None
) -> dict:
    """
    Aplica las reglas de parametros_comerciales sobre ley_planta.
    params: instancia de ParametrosComerciales (puede ser None → sin reglas).

    Reglas (en orden):
    1. Si ley_planta < lim_ley_comercial → restar dscto_ley_comercial
    2. Multiplicar por porcentaje_ley_comercial (factor, ej. 0.940)

    NOTA: lim_ley_inferior y lim_ley_superior NO se usan aquí para
    clamping de ley. Esos campos determinan el % de recuperación
    en liquidaciones (ver liquidaciones.py → _determinar_rec_liq).
    """
    if params is None:
        return {
            "ley_planta": float(ley_planta),
            "ley_comercial": float(ley_planta),
            "descuento_aplicado": 0.0,
            "factor_aplicado": 1.0,
            "ajuste_rango": False,
            "sin_parametros": True,
            "detalle": "Sin parametros comerciales configurados para este proveedor-acopiador",
        }

    q = Decimal("0.001")
    ley = ley_planta
    descuento = Decimal("0")
    factor = Decimal("1")
    detalle_pasos = []

    # Regla 1: descuento si ley < límite comercial
    if params.lim_ley_comercial and params.dscto_ley_comercial:
        lim = Decimal(str(params.lim_ley_comercial))
        dscto = Decimal(str(params.dscto_ley_comercial))
        if ley < lim:
            descuento = dscto
            ley = ley - dscto
            detalle_pasos.append(
                f"Ley {float(ley_planta):.4f} < limite {float(lim):.3f}: "
                f"descuento {float(dscto):.4f} → {float(ley):.4f}"
            )

    # Regla 2: factor porcentual aplicado a ley_planta (sin clamping de rango)
    elif params.porcentaje_ley_comercial:
        factor = Decimal(str(params.porcentaje_ley_comercial))
        ley_antes = ley
        ley = (ley * factor).quantize(q, rounding=ROUND_HALF_UP)
        detalle_pasos.append(
            f"Factor {float(factor):.3f}: {float(ley_antes):.3f} x {float(factor):.3f} = {float(ley):.3f}"
        )

    # Check volado:
    _umbral = umbral_volado if umbral_volado is not None else Decimal("0.100")
    if ley < _umbral:
        detalle_pasos.append(
            f"Resultado {float(ley):.3f} < umbral volado {float(_umbral):.4f}: se marca como volado"
        )
        ley = Decimal("0")

    return {
        "ley_planta": float(ley_planta),
        "ley_comercial": float(ley),
        "descuento_aplicado": float(descuento),
        "factor_aplicado": float(factor),
        "ajuste_rango": False,
        "sin_parametros": False,
        "detalle": " | ".join(detalle_pasos) if detalle_pasos else "Sin ajustes aplicados",
    }


# ── Análisis de Plata (Ag) ────────────────────────────────────────────────────


def _calcular_ley_ag(
    au_ag_mg: float,
    au_mg: float,
    peso_muestra: float,
    factor_oz_tc: Decimal,
    blank_correction: Decimal,
) -> tuple[Decimal, Decimal]:
    """
    Retorna (ley_ag_gr_tm, ley_ag_oz_tc).
    Fórmula: ley_ag_gr_tm = ((au_ag_mg - au_mg - blank_correction) * 1000) / peso_muestra
    """
    neto = Decimal(str(au_ag_mg)) - Decimal(str(au_mg)) - blank_correction
    if neto < 0:
        neto = Decimal("0")
    ley_gr_tm = (neto * 1000 / Decimal(str(peso_muestra))).quantize(
        Decimal("0.001"), rounding=ROUND_HALF_UP
    )
    ley_oz_tc = (ley_gr_tm / factor_oz_tc).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
    return ley_gr_tm, ley_oz_tc


def registrar_analisis_ag(
    db: Session,
    analisis_au_id: int,
    datos: "AnalisisAgCreate",
    usuario_id: int,
) -> "AnalisisAgOut":
    """
    Crea un AnalisisLey con material='Ag' vinculado al mismo lote que analisis_au_id.
    Si ya existe un Ag vigente para ese lote, lo marca como no vigente primero.
    """
    from app.models.models import AnalisisLey
    from app.schemas.laboratorio import AnalisisAgOut

    analisis_au = db.query(AnalisisLey).filter(AnalisisLey.id == analisis_au_id).first()
    if not analisis_au:
        raise ValueError(f"Análisis Au {analisis_au_id} no encontrado")
    if analisis_au.material != "Au":
        raise ValueError("Solo se puede agregar Ag a análisis de material Au")

    lote_id = analisis_au.lote_id

    # Marcar Ag anterior como no vigente
    db.query(AnalisisLey).filter(
        AnalisisLey.lote_id == lote_id,
        AnalisisLey.material == "Ag",
        AnalisisLey.vigente == True,  # noqa: E712
    ).update({"vigente": False}, synchronize_session="fetch")

    constantes = get_constantes(db)
    ley_gr_tm, ley_oz_tc = _calcular_ley_ag(
        datos.au_ag_mg,
        datos.au_mg,
        datos.peso_muestra,
        constantes.factor_oz_tc,
        constantes.blank_correction_ag,
    )

    nuevo = AnalisisLey(
        lote_id=lote_id,
        cip=analisis_au.cip,
        laboratorio=datos.laboratorio,
        tipo_analisis=analisis_au.tipo_analisis,  # hereda tipo del Au padre
        material="Ag",
        ley_fino=float(ley_oz_tc),  # reutilizamos ley_fino para Oz/TC de Ag
        ley_grueso=0.0,
        ley_gr_tm=float(ley_gr_tm),
        origen_datos="manual",
        fecha_analisis=datos.fecha_analisis,
        vigente=True,
        creado_por=usuario_id,
    )
    db.add(nuevo)
    db.flush()

    lote = db.query(Lote).filter(Lote.id == lote_id).first()
    return AnalisisAgOut(
        id=nuevo.id,
        lote_id=lote_id,
        lote_ip=lote.ip if lote else None,
        laboratorio=nuevo.laboratorio,
        ley_ag_gr_tm=ley_gr_tm,
        ley_ag_oz_tc=ley_oz_tc,
        fecha_analisis=nuevo.fecha_analisis,
        vigente=nuevo.vigente,
        creado_por=nuevo.creado_por,
        creado_en=nuevo.creado_en,
    )


def obtener_ley_ag_vigente(db: Session, lote_id: int) -> tuple[Decimal, Decimal] | None:
    """
    Retorna (ley_ag_gr_tm, ley_ag_oz_tc) del análisis Ag vigente para el lote,
    o None si no existe.
    Usada por el servicio de liquidaciones.
    """
    from app.models.models import AnalisisLey

    a = (
        db.query(AnalisisLey)
        .filter(
            AnalisisLey.lote_id == lote_id,
            AnalisisLey.material == "Ag",
            AnalisisLey.vigente == True,  # noqa: E712
        )
        .order_by(AnalisisLey.id.desc())
        .first()
    )
    if not a:
        return None
    gr_tm = Decimal(str(a.ley_gr_tm)) if a.ley_gr_tm else Decimal("0")
    oz_tc = Decimal(str(a.ley_fino)) if a.ley_fino else Decimal("0")
    return gr_tm, oz_tc
