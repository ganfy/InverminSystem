from collections import defaultdict
from datetime import date

from app.models.enums import EstadoLote, TipoAnalisis
from app.models.models import (
    AnalisisLey,
    AnalisisRecuperacion,
    Lote,
    MapeoCIP,
    Muestreo,
    Pesaje,
    SesionDescarga,
)
from app.schemas.dashboard import AcopiadorTMH, DashboardKPIs, DashboardResponse, LoteDashboard
from sqlalchemy.orm import Session

_DIAS_HABILITADO = 30  # días de almacén para considerar lote "habilitado"


def _calcular_estado_analisis(
    tiene_cip: bool,
    tiene_ley: bool,
    tiene_rec_completa: bool,
    tiene_humedad: bool,
) -> str:
    if not tiene_cip:
        return "SIN_DATOS"
    if not tiene_humedad:
        return "FALTA_MUESTREO"
    if not tiene_ley:
        return "FALTA_LEY"
    if not tiene_rec_completa:
        return "FALTA_REC"
    return "LISTO"


def _calcular_estado_lote(lote: Lote, dias: int, tiene_recuperacion: bool) -> str:
    if lote.volado:
        return "VOLADO"
    if lote.dirimencia:
        return "DIRIMENCIA"
    if tiene_recuperacion:
        return "COMPLETO"
    if lote.habilitado_ruma or dias >= _DIAS_HABILITADO:
        return "HABILITADO"
    return "EN_PROCESO"


def obtener_resumen_dashboard(db: Session) -> DashboardResponse:
    lotes_db = db.query(Lote).filter(~Lote.eliminado).all()

    # Pre-cargar sets en queries únicas (evita N+1)
    ids_con_cip: set[int] = {row[0] for row in db.query(MapeoCIP.lote_id).distinct().all()}

    # Pre-cargar todas las Leyes vigentes (excluyendo minero)
    leyes_db = (
        db.query(AnalisisLey.lote_id, AnalisisLey.tipo_analisis, AnalisisLey.ley_gr_tm)
        .filter(
            AnalisisLey.vigente == True,  # noqa: E712
            AnalisisLey.tipo_analisis != TipoAnalisis.MINERO,
        )
        .all()
    )

    leyes_por_lote = defaultdict(list)
    ids_con_ley = set()
    for lote_id, tipo, valor in leyes_db:
        ids_con_ley.add(lote_id)
        leyes_por_lote[lote_id].append({"tipo": tipo, "valor": valor})

    # Pre-cargar todas las Recuperaciones vigentes
    recs_db = (
        db.query(
            AnalisisRecuperacion.lote_id,
            AnalisisRecuperacion.estado,
            AnalisisRecuperacion.recuperacion,
        )
        .filter(AnalisisRecuperacion.vigente == True)  # noqa: E712
        .all()
    )

    recs_por_lote = defaultdict(list)
    ids_con_recuperacion = set()
    for lote_id, estado, valor in recs_db:
        ids_con_recuperacion.add(lote_id)
        recs_por_lote[lote_id].append({"estado": estado, "valor": valor})

    # ids con recuperación COMPLETADA y sin ninguna PENDIENTE
    ids_rec_completa: set[int] = set()
    ids_rec_pendiente: set[int] = set()
    for lote_id, recs in recs_por_lote.items():
        has_completado = any(r["estado"] in ("COMPLETADO", "CERT_COMERCIAL") for r in recs)
        has_pendiente = any(r["estado"] == "PENDIENTE" for r in recs)
        if has_pendiente:
            ids_rec_pendiente.add(lote_id)
        if has_completado and not has_pendiente:
            ids_rec_completa.add(lote_id)

    kpis = DashboardKPIs()
    lotes_resumen = []

    # Estructura para almacenar sumatorias: { acopiador: { mes_num: sum_tmh } }
    tmh_por_acopiador_mes = defaultdict(lambda: defaultdict(float))

    for lote in lotes_db:
        pesaje = db.query(Pesaje).filter(Pesaje.lote_id == lote.id).first()
        tmh = 0.0
        if pesaje and pesaje.peso_inicial and pesaje.peso_final:
            if pesaje.peso_inicial > pesaje.peso_final:
                tmh = float(pesaje.peso_inicial - pesaje.peso_final)

        kpis.tmh_stock += tmh

        h2o_porc = None
        tms = None

        muestreo = (
            db.query(Muestreo)
            .filter(Muestreo.lote_id == lote.id)
            .order_by(Muestreo.creado_en.desc())
            .first()
        )

        if muestreo and muestreo.peso_humedo and muestreo.peso_seco:
            ph = float(muestreo.peso_humedo)
            ps = float(muestreo.peso_seco)
            if ph > 0:
                h2o_porc = round(((ph - ps) / ph) * 100, 2)
                tms = round(tmh * (1 - (h2o_porc / 100)), 3)
                kpis.tms_stock += tms

        # tiene_humedad DEBE evaluarse después del bloque de muestreo
        tiene_humedad = tms is not None

        sesion = db.query(SesionDescarga).filter(SesionDescarga.id == lote.sesion_id).first()
        proveedor_nombre = "---"
        proveedor_ruc = "---"
        acopiador_nombre = "---"

        if sesion and getattr(sesion, "provacop", None):
            if getattr(sesion.provacop, "proveedor", None):
                proveedor_nombre = sesion.provacop.proveedor.razon_social
                proveedor_ruc = sesion.provacop.proveedor.ruc
            if getattr(sesion.provacop, "acopiador", None):
                acopiador_nombre = sesion.provacop.acopiador.razon_social

        # Días en almacén
        fecha_rec = None
        if lote.pesajes:
            dt = lote.pesajes[0].fecha_fin
            fecha_rec = dt.date() if hasattr(dt, "date") else dt
        dias = (date.today() - fecha_rec).days if fecha_rec else 0

        is_volado_30d = bool(lote.volado) and dias >= _DIAS_HABILITADO
        is_facturado_o_pagado = lote.estado in (EstadoLote.FACTURADO, EstadoLote.PAGADO)
        habilitado_ruma = bool(lote.habilitado_ruma) or is_volado_30d or is_facturado_o_pagado

        estado_analisis = _calcular_estado_analisis(
            tiene_cip=lote.id in ids_con_cip,
            tiene_ley=lote.id in ids_con_ley,
            tiene_rec_completa=lote.id in ids_rec_completa,
            tiene_humedad=tiene_humedad,
        )

        # --- ACUMULACIÓN DE TMH POR MES Y ACOPIADOR ---
        if acopiador_nombre and fecha_rec:
            mes_num = fecha_rec.month
            tmh_por_acopiador_mes[acopiador_nombre][mes_num] += tmh

        estado_analisis = _calcular_estado_analisis(
            tiene_cip=lote.id in ids_con_cip,
            tiene_ley=lote.id in ids_con_ley,
            tiene_rec_completa=lote.id in ids_rec_completa,
            tiene_humedad=tiene_humedad,
        )

        # --- CÁLCULO DE LEY PROMEDIO O COMERCIAL ---
        ley_prom = None
        leyes_del_lote = leyes_por_lote.get(lote.id, [])
        if leyes_del_lote:
            # Buscar primero si tiene ley comercial con valor registrado
            ley_comercial = next(
                (
                    ley["valor"]
                    for ley in leyes_del_lote
                    if ley["tipo"] in (TipoAnalisis.COMERCIAL, "ley_comercial")
                    and ley["valor"] is not None
                ),
                None,
            )

            if ley_comercial is not None:
                ley_prom = float(ley_comercial)
            else:
                # Si no hay comercial, se promedian las demás leyes válidas registradas
                valores_ley = [
                    float(ley["valor"]) for ley in leyes_del_lote if ley["valor"] is not None
                ]
                if valores_ley:
                    ley_prom = round(sum(valores_ley) / len(valores_ley), 3)

        # --- CÁLCULO DE RECUPERACIÓN PROMEDIO O COMERCIAL ---
        rec_prom = None
        recs_del_lote = recs_por_lote.get(lote.id, [])
        if recs_del_lote:
            # Buscar primero si tiene certificado comercial con valor registrado
            rec_comercial = next(
                (
                    r["valor"]
                    for r in recs_del_lote
                    if r["estado"] == "CERT_COMERCIAL" and r["valor"] is not None
                ),
                None,
            )

            if rec_comercial is not None:
                rec_prom = float(rec_comercial)
            else:
                # Si no hay comercial, se promedian las que tengan estado "COMPLETADO"
                valores_rec = [
                    float(r["valor"])
                    for r in recs_del_lote
                    if r["estado"] == "COMPLETADO" and r["valor"] is not None
                ]
                if valores_rec:
                    rec_prom = round(sum(valores_rec) / len(valores_rec), 2)

        if tms is not None and ley_prom is not None:
            au_lote = tms * ley_prom
            kpis.au_real_100 += au_lote
            if rec_prom is not None:
                kpis.au_real_rec += au_lote * rec_prom / 100
            # Usamos el flag unificado para las Onzas Habilitadas del KPI global
            if habilitado_ruma and lote.ruma_id is None:
                kpis.oz_habilitados += au_lote / 31.1035

        lotes_resumen.append(
            LoteDashboard(
                ip=lote.ip,
                tmh=round(tmh, 3),
                tms=tms,
                h2o_porc=h2o_porc,
                proveedor=proveedor_nombre,
                ruc=proveedor_ruc,
                ley_avg=ley_prom,
                rec_porc=rec_prom,
                acopiador=acopiador_nombre,
                estado=lote.estado if lote.estado else "RECEPCIONADO",
                estado_analisis=estado_analisis,
                habilitado_ruma=habilitado_ruma,
                volado=bool(lote.volado),
                dirimencia=bool(lote.dirimencia),
                dias_almacen=dias,
                tiene_rec_pendiente=lote.id in ids_rec_pendiente,
            )
        )

    kpis.tmh_stock = round(kpis.tmh_stock, 2)
    kpis.tms_stock = round(kpis.tms_stock, 2)
    kpis.au_real_100 = round(kpis.au_real_100, 2)
    kpis.au_real_rec = round(kpis.au_real_rec, 2)
    kpis.oz_stock = round(kpis.au_real_100 / 31.1035, 3)
    kpis.oz_habilitados = round(kpis.oz_habilitados, 3)

    lotes_resumen.sort(key=lambda x: x.ip, reverse=True)

    acopiadores_tmh_list = []
    for acop_name, meses_dict in tmh_por_acopiador_mes.items():
        acopiadores_tmh_list.append(
            AcopiadorTMH(
                acopiador=acop_name,
                enero=round(meses_dict[1], 2),
                febrero=round(meses_dict[2], 2),
                marzo=round(meses_dict[3], 2),
                abril=round(meses_dict[4], 2),
                mayo=round(meses_dict[5], 2),
                junio=round(meses_dict[6], 2),
                julio=round(meses_dict[7], 2),
                agosto=round(meses_dict[8], 2),
                septiembre=round(meses_dict[9], 2),
                octubre=round(meses_dict[10], 2),
                noviembre=round(meses_dict[11], 2),
                diciembre=round(meses_dict[12], 2),
                total=round(sum(meses_dict.values()), 2),
            )
        )

    # Ordenamos de mayor a menor según el tonelaje total traído
    acopiadores_tmh_list.sort(key=lambda x: x.total, reverse=True)

    return DashboardResponse(kpis=kpis, lotes=lotes_resumen, acopiadores_tmh=acopiadores_tmh_list)
