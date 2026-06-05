"""
Service: Módulo Rumas y Campañas.

Lógica de negocio separada del router.
"""

from datetime import date, datetime
from decimal import Decimal

from app.models.enums import EstadoCampana, EstadoRuma, TipoAnalisis
from app.models.models import (
    AnalisisLey,
    AnalisisRecuperacion,
    Campana,
    Lote,
    Muestreo,
    Pesaje,
    Ruma,
    RumaCampana,
    Usuario,
)
from app.schemas.rumas import (
    AsignarLotesRequest,
    CampanaCerrarRequest,
    CampanaCreate,
    CampanaEditarMeta,
    CampanaOut,
    LoteDisponibleOut,
    LoteRumaItem,
    RumaLista,
    RumaOut,
)
from fastapi import HTTPException
from sqlalchemy.orm import Session

# ──────────────────────────────────────────────────────────────────────────────
# Helpers internos
# ──────────────────────────────────────────────────────────────────────────────


def _get_campana_activa(db: Session) -> Campana:
    camp = db.query(Campana).filter(Campana.estado == EstadoCampana.ACTIVA).first()
    if not camp:
        raise HTTPException(status_code=404, detail="No hay campaña activa")
    return camp


def _siguiente_codigo_campana(db: Session) -> str:
    """Genera CAMP{año}-{secuencial:02d}."""
    anio = date.today().year
    prefijo = f"CAMP{anio}-"
    ultima = (
        db.query(Campana)
        .filter(Campana.codigo.like(f"{prefijo}%"))
        .order_by(Campana.id.desc())
        .first()
    )
    if ultima:
        try:
            num = int(ultima.codigo.split("-")[-1]) + 1
        except (ValueError, IndexError):
            num = 1
    else:
        num = 1
    return f"{prefijo}{num:02d}"


def _siguiente_numero_ruma_independiente(db: Session) -> int:
    """Obtiene el siguiente número de ruma para el año actual (global, no por campaña)"""
    anio = date.today().year
    ultima = (
        db.query(Ruma).filter(Ruma.codigo.like(f"RMA{anio}-%")).order_by(Ruma.id.desc()).first()
    )
    if ultima:
        try:
            return int(ultima.codigo.split("-")[-1]) + 1
        except (ValueError, IndexError):
            return 1
    return 1


def _codigo_ruma(campana: Campana, numero: int) -> str:
    return f"{campana.codigo}-{numero:03d}"


def _get_ruma_o_404(db: Session, ruma_id: int) -> Ruma:
    ruma = db.query(Ruma).filter(Ruma.id == ruma_id).first()
    if not ruma:
        raise HTTPException(status_code=404, detail="Ruma no encontrada")
    return ruma


def _calcular_tms_lote(lote: Lote, db: Session) -> float | None:
    """
    TMS = TMH * (1 - %H2O/100).
    Usa el último muestreo vigente.
    """
    pesaje = db.query(Pesaje).filter(Pesaje.lote_id == lote.id).first()
    if not pesaje or pesaje.peso_inicial is None or pesaje.peso_final is None:
        return 0.0
    tmh = float(abs(pesaje.peso_final - pesaje.peso_inicial))
    muestreo = (
        db.query(Muestreo)
        .filter(Muestreo.lote_id == lote.id)
        .order_by(Muestreo.creado_en.desc())
        .first()
    )
    if not muestreo or not muestreo.peso_humedo or not muestreo.peso_seco:
        return None
    ph = float(muestreo.peso_humedo)
    if ph <= 0:
        return None
    h2o = ((ph - float(muestreo.peso_seco)) / ph) * 100
    return round(tmh * (1 - h2o / 100), 3)


def _calcular_tmh_lote(lote: Lote, db: Session) -> float:
    pesaje = db.query(Pesaje).filter(Pesaje.lote_id == lote.id).first()
    if not pesaje or not pesaje.peso_inicial or not pesaje.peso_final:
        return 0.0
    return float(abs(pesaje.peso_final - pesaje.peso_inicial))


def _ley_vigente(lote: Lote, db: Session) -> float | None:
    leyes = (
        db.query(AnalisisLey.tipo_analisis, AnalisisLey.ley_final)
        .filter(
            AnalisisLey.lote_id == lote.id,
            AnalisisLey.vigente == True,  # noqa: E712
            AnalisisLey.tipo_analisis != TipoAnalisis.MINERO,
            AnalisisLey.material == "Au",
        )
        .all()
    )
    if not leyes:
        return None
    # Preferir ley comercial
    for tipo, valor in leyes:
        if tipo in (TipoAnalisis.COMERCIAL, "ley_comercial") and valor is not None:
            return float(valor)
    valores = [float(v) for _, v in leyes if v is not None]
    return round(sum(valores) / len(valores), 3) if valores else None


def _rec_vigente(lote: Lote, db: Session) -> float | None:
    recs = (
        db.query(AnalisisRecuperacion.estado, AnalisisRecuperacion.recuperacion)
        .filter(AnalisisRecuperacion.lote_id == lote.id, AnalisisRecuperacion.vigente == True)  # noqa: E712
        .all()
    )
    if not recs:
        return None
    for estado, val in recs:
        if estado == "CERT_COMERCIAL" and val is not None:
            return float(val)
    valores = [float(v) for e, v in recs if e == "COMPLETADO" and v is not None]
    return round(sum(valores) / len(valores), 2) if valores else None


def _proveedor_acopiador_lote(lote: Lote) -> tuple[str, str | None]:
    sesion = lote.sesion
    proveedor = "—"
    acopiador = None
    if sesion and getattr(sesion, "provacop", None):
        if getattr(sesion.provacop, "proveedor", None):
            proveedor = sesion.provacop.proveedor.razon_social
        if getattr(sesion.provacop, "acopiador", None):
            acopiador = sesion.provacop.acopiador.razon_social
    return proveedor, acopiador


def _calcular_totales_ruma(lotes: list[Lote], db: Session) -> dict:
    """
    Totales ponderados de la ruma.
    Ley promedio ponderada = Σ(tms_i * ley_i) / Σ(tms_i)
    """
    total_tms = 0.0
    suma_tms_ley = 0.0
    suma_rec_ponderada = 0.0
    tms_con_ley = 0.0
    tms_con_rec = 0.0
    llampo_tms = 0.0

    for lote in lotes:
        tms = _calcular_tms_lote(lote, db)
        if tms is None:
            tms = 0.0
        total_tms += tms

        ley = _ley_vigente(lote, db)
        if ley is not None and tms > 0:
            suma_tms_ley += tms * ley
            tms_con_ley += tms

        rec = _rec_vigente(lote, db)
        if rec is not None and tms > 0:
            suma_rec_ponderada += tms * rec
            tms_con_rec += tms

        if lote.tipo_material and "llampo" in lote.tipo_material.lower():
            llampo_tms += tms

    ley_pond = round(suma_tms_ley / tms_con_ley, 4) if tms_con_ley > 0 else None
    rec_prom = round(suma_rec_ponderada / tms_con_rec, 2) if tms_con_rec > 0 else None
    pct_llampo = round((llampo_tms / total_tms) * 100, 1) if total_tms > 0 else None

    return {
        "total_lotes": len(lotes),
        "total_tms": round(total_tms, 3),
        "ley_ponderada": ley_pond,
        "rec_promedio": rec_prom,
        "pct_llampo": pct_llampo,
    }


def _build_campana_out(campana: Campana) -> CampanaOut:
    hoy = date.today()
    dias = (hoy - campana.fecha_inicio).days if campana.fecha_inicio else None
    meta = float(campana.meta_oro_fino) if campana.meta_oro_fino else 1.0
    acum = float(campana.oro_fino_acumulado or 0)
    progreso = round((acum / meta) * 100, 1) if meta > 0 else 0.0
    return CampanaOut(
        id=campana.id,
        codigo=campana.codigo,
        meta_oro_fino=campana.meta_oro_fino,
        fecha_inicio=campana.fecha_inicio,
        fecha_cierre=campana.fecha_cierre,
        estado=campana.estado,
        oro_fino_acumulado=campana.oro_fino_acumulado or Decimal("0"),
        total_lotes=campana.total_lotes or 0,
        total_toneladas=campana.total_toneladas or Decimal("0"),
        total_rumas=campana.total_rumas or 0,
        progreso_pct=progreso,
        dias_transcurridos=dias,
    )


def _build_ruma_out(ruma: Ruma, db: Session, incluir_lotes: bool = True) -> RumaOut:
    lotes = ruma.lotes if incluir_lotes else []
    totales = _calcular_totales_ruma(lotes, db)

    lotes_out = []
    for lote in lotes:
        proveedor, _ = _proveedor_acopiador_lote(lote)
        lotes_out.append(
            LoteRumaItem(
                ip=lote.ip,
                proveedor=proveedor,
                tmh=_calcular_tmh_lote(lote, db),
                tms=_calcular_tms_lote(lote, db),
                ley_avg=_ley_vigente(lote, db),
                rec_porc=_rec_vigente(lote, db),
                tipo_material=lote.tipo_material,
                habilitado_ruma=bool(lote.habilitado_ruma),
                volado=bool(lote.volado),
            )
        )

    return RumaOut(
        id=ruma.id,
        codigo=ruma.codigo,
        numero_ruma=ruma.numero_ruma,
        fecha_creacion=ruma.fecha_creacion or date.today(),
        estado=ruma.estado,
        lotes=lotes_out,
        **totales,
    )


def _actualizar_totales_campana(db: Session, campana_id: int):
    """
    Recalcula dinámicamente el progreso de la campaña.
    - Rumas creadas: Cronológico (desde fecha inicio hasta fecha cierre).
    - Lotes, TMS y Oro: Solo de las rumas ASIGNADAS.
    """
    campana = db.query(Campana).filter(Campana.id == campana_id).first()
    if not campana:
        return

    # 1. Total de Rumas Creadas en el periodo de la campaña
    query_rumas = db.query(Ruma).filter(Ruma.fecha_creacion >= campana.fecha_inicio)
    if campana.fecha_cierre:
        query_rumas = query_rumas.filter(Ruma.fecha_creacion <= campana.fecha_cierre)

    campana.total_rumas = query_rumas.count()

    # 2. Totales de procesamiento (Solo de las rumas asignadas)
    ids_ruma = [rc.id_ruma for rc in campana.rumas_campana]
    if not ids_ruma:
        campana.total_lotes = 0
        campana.total_toneladas = Decimal("0")
        campana.oro_fino_acumulado = Decimal("0")
        db.flush()
        return

    lotes = db.query(Lote).filter(Lote.ruma_id.in_(ids_ruma), ~Lote.eliminado).all()

    total_lotes = len(lotes)
    total_tms = 0.0
    oro_acumulado = 0.0

    for lote in lotes:
        tms = _calcular_tms_lote(lote, db) or 0.0
        total_tms += tms

        ley_oz = _ley_vigente(lote, db)
        rec_pct = _rec_vigente(lote, db)

        if tms > 0 and ley_oz is not None and rec_pct is not None:
            oro_lote = tms * (ley_oz * 34.2857) * (rec_pct / 100.0)
            oro_acumulado += oro_lote

    campana.total_lotes = total_lotes
    campana.total_toneladas = Decimal(str(round(total_tms, 3)))
    campana.oro_fino_acumulado = Decimal(str(round(oro_acumulado, 2)))

    db.flush()


# ──────────────────────────────────────────────────────────────────────────────
# CAMPAÑAS
# ──────────────────────────────────────────────────────────────────────────────


# ── CAMPAÑAS ──────────────────────────────────────────────────────────────────


def obtener_campana_activa(db: Session) -> CampanaOut:
    """Retorna la campaña activa recalculando sus métricas en tiempo real."""
    campana = db.query(Campana).filter(Campana.estado == EstadoCampana.ACTIVA).first()
    if not campana:
        raise HTTPException(status_code=404, detail="No hay campaña activa")

    # 1. Forzamos el recálculo para que lea directamente de la BD los datos frescos
    _actualizar_totales_campana(db, campana.id)

    # 2. Re-refrescamos el objeto por si hubo cambios persistidos en el helper
    db.refresh(campana)

    return _build_campana_out(campana)


def listar_campanas(db: Session) -> list[CampanaOut]:
    """Lista todas las campañas asegurando que la activa esté actualizada."""
    camps = db.query(Campana).order_by(Campana.id.desc()).all()

    for c in camps:
        if c.estado == EstadoCampana.ACTIVA:
            _actualizar_totales_campana(db, c.id)
            db.refresh(c)

    return [_build_campana_out(c) for c in camps]


def crear_campana(db: Session, datos: CampanaCreate, usuario: Usuario) -> CampanaOut:
    # Solo si no hay campaña activa
    activa = db.query(Campana).filter(Campana.estado == EstadoCampana.ACTIVA).first()
    if activa:
        raise HTTPException(
            status_code=400,
            detail=f"Ya existe una campaña activa: {activa.codigo}. Ciérrala antes de crear una nueva.",
        )
    codigo = _siguiente_codigo_campana(db)
    nueva = Campana(
        codigo=codigo,
        meta_oro_fino=datos.meta_oro_fino,
        fecha_inicio=date.today(),
        estado=EstadoCampana.ACTIVA,
        oro_fino_acumulado=Decimal("0"),
        total_lotes=0,
        total_toneladas=Decimal("0"),
        total_rumas=0,
        gerencia_id=usuario.id,
    )
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return _build_campana_out(nueva)


def asignar_ruma_a_campana(
    db: Session, campana_id: int, ruma_id: int, usuario: Usuario
) -> CampanaOut:
    campana = db.query(Campana).filter(Campana.id == campana_id).first()
    if not campana:
        raise HTTPException(status_code=404, detail="Campaña no encontrada")
    if campana.estado != EstadoCampana.ACTIVA:
        raise HTTPException(
            status_code=400, detail="Solo se pueden asignar rumas a campañas activas"
        )

    ruma = _get_ruma_o_404(db, ruma_id)

    # Validar que no esté ya asignada
    asignacion_existente = db.query(RumaCampana).filter(RumaCampana.id_ruma == ruma.id).first()
    if asignacion_existente:
        raise HTTPException(status_code=400, detail="Esta ruma ya pertenece a una campaña")

    # Calcular toneladas actuales de la ruma
    todos_lotes = db.query(Lote).filter(Lote.ruma_id == ruma.id, ~Lote.eliminado).all()
    total_tms = sum(_calcular_tms_lote(tl, db) or 0.0 for tl in todos_lotes)

    # Crear asociación
    rel = RumaCampana(
        id_ruma=ruma.id, id_campana=campana.id, tonelaje=Decimal(str(round(total_tms, 3)))
    )
    db.add(rel)
    db.flush()

    # Actualizar datos de la campaña
    _actualizar_totales_campana(db, campana.id)

    db.commit()
    db.refresh(campana)
    return _build_campana_out(campana)


def cerrar_campana(
    db: Session, campana_id: int, datos: CampanaCerrarRequest, usuario: Usuario
) -> CampanaOut:
    campana = db.query(Campana).filter(Campana.id == campana_id).first()
    if not campana:
        raise HTTPException(status_code=404, detail="Campaña no encontrada")
    if campana.estado != EstadoCampana.ACTIVA:
        raise HTTPException(status_code=400, detail="La campaña no está activa")

    # 1. Cerrar rumas abiertas de esta campaña
    ids_ruma = [rc.id_ruma for rc in campana.rumas_campana]
    if ids_ruma:
        db.query(Ruma).filter(
            Ruma.id.in_(ids_ruma),
            Ruma.estado == EstadoRuma.ABIERTA,
        ).update({"estado": EstadoRuma.CERRADA}, synchronize_session=False)

    # 2. Cerrar campaña actual
    campana.estado = EstadoCampana.CERRADA
    campana.fecha_cierre = date.today()
    db.flush()

    # 3. Crear nueva campaña con la meta indicada
    codigo_nuevo = _siguiente_codigo_campana(db)
    nueva = Campana(
        codigo=codigo_nuevo,
        meta_oro_fino=datos.meta_oro_fino_nueva,
        fecha_inicio=date.today(),
        estado=EstadoCampana.ACTIVA,
        oro_fino_acumulado=Decimal("0"),
        total_lotes=0,
        total_toneladas=Decimal("0"),
        total_rumas=0,
        gerencia_id=usuario.id,
    )
    db.add(nueva)
    db.commit()
    db.refresh(campana)
    return _build_campana_out(campana)


def editar_meta_campana(
    db: Session, campana_id: int, datos: CampanaEditarMeta, usuario: Usuario
) -> CampanaOut:
    campana = db.query(Campana).filter(Campana.id == campana_id).first()
    if not campana:
        raise HTTPException(status_code=404, detail="Campaña no encontrada")
    campana.meta_oro_fino = datos.meta_oro_fino
    db.commit()
    db.refresh(campana)
    return _build_campana_out(campana)


# ──────────────────────────────────────────────────────────────────────────────
# RUMAS
# ──────────────────────────────────────────────────────────────────────────────


def listar_rumas(db: Session) -> list[RumaLista]:
    """Lista todas las rumas (puedes agregar filtros por estado o asignación)"""
    rumas = db.query(Ruma).order_by(Ruma.id.desc()).all()
    resultado = []
    for ruma in rumas:
        totales = _calcular_totales_ruma(ruma.lotes, db)
        esta_asignada = len(ruma.rumas_campana) > 0
        resultado.append(
            RumaLista(
                id=ruma.id,
                codigo=ruma.codigo,
                numero_ruma=ruma.numero_ruma,
                fecha_creacion=ruma.fecha_creacion or date.today(),
                estado=ruma.estado,
                asignada=esta_asignada,
                **totales,
            )
        )
    return resultado


def crear_ruma(db: Session, usuario: Usuario) -> RumaOut:
    anio = date.today().year
    numero = _siguiente_numero_ruma_independiente(db)
    codigo = f"RMA{anio}-{numero:03d}"

    ruma = Ruma(
        numero_ruma=numero,
        codigo=codigo,
        fecha_creacion=date.today(),
        estado=EstadoRuma.ABIERTA,
    )
    db.add(ruma)
    db.flush()

    campana_activa = db.query(Campana).filter(Campana.estado == EstadoCampana.ACTIVA).first()
    if campana_activa:
        _actualizar_totales_campana(db, campana_activa.id)

    db.commit()
    db.refresh(ruma)
    return _build_ruma_out(ruma, db)


def obtener_ruma(db: Session, ruma_id: int) -> RumaOut:
    ruma = _get_ruma_o_404(db, ruma_id)
    return _build_ruma_out(ruma, db)


def asignar_lotes(
    db: Session, ruma_id: int, datos: AsignarLotesRequest, usuario: Usuario
) -> RumaOut:
    """
    Reemplaza la lista de lotes asignados a la ruma.
    - Desvincula lotes que ya no están en la lista.
    - Vincula los nuevos, validando habilitado_ruma=True y sin otra ruma.
    """
    ruma = _get_ruma_o_404(db, ruma_id)
    if ruma.estado == EstadoRuma.CERRADA:
        raise HTTPException(status_code=400, detail="No se pueden asignar lotes a una ruma cerrada")

    ips_nuevas = set(datos.ips)

    # Lotes actualmente en la ruma
    lotes_actuales = db.query(Lote).filter(Lote.ruma_id == ruma_id, ~Lote.eliminado).all()
    ips_actuales = {la.ip for la in lotes_actuales}

    # Desvincular los que ya no van
    for lote in lotes_actuales:
        if lote.ip not in ips_nuevas:
            lote.ruma_id = None

    # Vincular los nuevos
    ips_a_agregar = ips_nuevas - ips_actuales
    for ip in ips_a_agregar:
        lote = db.query(Lote).filter(Lote.ip == ip, ~Lote.eliminado).first()
        if not lote:
            raise HTTPException(status_code=404, detail=f"Lote {ip} no encontrado")
        if not lote.habilitado_ruma:
            raise HTTPException(status_code=400, detail=f"Lote {ip} no está habilitado para ruma")
        if lote.ruma_id is not None and lote.ruma_id != ruma_id:
            raise HTTPException(
                status_code=400,
                detail=f"Lote {ip} ya está asignado a otra ruma",
            )
        lote.ruma_id = ruma_id

    db.flush()

    # Actualizar tonelaje en RumaCampana
    todos_lotes = db.query(Lote).filter(Lote.ruma_id == ruma_id, ~Lote.eliminado).all()
    total_tms = sum(_calcular_tms_lote(tl, db) or 0.0 for tl in todos_lotes)

    rel = db.query(RumaCampana).filter(RumaCampana.id_ruma == ruma_id).first()
    if rel:
        rel.tonelaje = Decimal(str(round(total_tms, 3)))
        db.flush()
        # Actualizar datos de la campaña
        _actualizar_totales_campana(db, rel.id_campana)

    db.commit()
    db.refresh(ruma)
    return _build_ruma_out(ruma, db)


def cerrar_ruma(db: Session, ruma_id: int, usuario: Usuario) -> RumaOut:
    ruma = _get_ruma_o_404(db, ruma_id)
    if ruma.estado == EstadoRuma.CERRADA:
        raise HTTPException(status_code=400, detail="La ruma ya está cerrada")
    ruma.estado = EstadoRuma.CERRADA
    db.commit()
    db.refresh(ruma)
    return _build_ruma_out(ruma, db)


def listar_lotes_disponibles(db: Session) -> list[LoteDisponibleOut]:
    """
    Lotes habilitados para ruma, sin ruma asignada.
    No eliminados.
    """
    lotes = (
        db.query(Lote)
        .filter(
            Lote.habilitado_ruma == True,  # noqa: E712
            Lote.ruma_id.is_(None),
            ~Lote.eliminado,
        )
        .all()
    )
    resultado = []
    for lote in lotes:
        proveedor, acopiador = _proveedor_acopiador_lote(lote)
        pesaje = db.query(Pesaje).filter(Pesaje.lote_id == lote.id).first()
        fecha_rec = None
        if pesaje and pesaje.fecha_fin:
            dt = pesaje.fecha_fin
            fecha_rec = dt.date() if hasattr(dt, "date") else dt
        dias = (date.today() - fecha_rec).days if fecha_rec else 0

        resultado.append(
            LoteDisponibleOut(
                ip=lote.ip,
                proveedor=proveedor,
                acopiador=acopiador,
                tmh=_calcular_tmh_lote(lote, db),
                tms=_calcular_tms_lote(lote, db),
                ley_avg=_ley_vigente(lote, db),
                rec_porc=_rec_vigente(lote, db),
                tipo_material=lote.tipo_material,
                volado=bool(lote.volado),
                dias_almacen=dias,
            )
        )
    return resultado


def habilitar_lote_manual(
    db: Session, ip: str, usuario: Usuario, motivo: str | None = None
) -> dict:
    """Habilita manualmente un lote para ruma. Solo Admin/Gerencia/Comercial."""
    lote = db.query(Lote).filter(Lote.ip == ip, ~Lote.eliminado).first()
    if not lote:
        raise HTTPException(status_code=404, detail=f"Lote {ip} no encontrado")
    if lote.habilitado_ruma:
        raise HTTPException(status_code=400, detail="El lote ya está habilitado para ruma")

    lote.habilitado_ruma = True
    lote.fecha_habilitacion = datetime.utcnow()
    lote.habilitado_por = usuario.id
    db.commit()
    return {"ip": ip, "habilitado_ruma": True, "habilitado_por": usuario.id}
