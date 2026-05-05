from datetime import date

from app.models.models import AnalisisRecuperacion, Lote, Muestreo, Pesaje, SesionDescarga
from app.schemas.dashboard import DashboardKPIs, DashboardResponse, LoteDashboard
from sqlalchemy.orm import Session

_DIAS_HABILITADO = 30  # días de almacén para considerar lote "habilitado"


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

    # Pre-cargar lote_ids con recuperación vigente en una sola query
    ids_con_recuperacion: set[int] = {
        row[0]
        for row in db.query(AnalisisRecuperacion.lote_id)
        .filter(AnalisisRecuperacion.vigente == True)  # noqa: E712
        .distinct()
        .all()
    }

    kpis = DashboardKPIs()
    lotes_resumen = []

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

        tiene_rec = lote.id in ids_con_recuperacion
        estado_display = lote.estado if lote.estado else "EN_PROCESO"
        estado_lote = _calcular_estado_lote(lote, dias, tiene_rec)

        lotes_resumen.append(
            LoteDashboard(
                ip=lote.ip,
                tmh=round(tmh, 3),
                tms=tms,
                h2o_porc=h2o_porc,
                proveedor=proveedor_nombre,
                ruc=proveedor_ruc,
                ley_avg=None,
                rec_porc=None,
                acopiador=acopiador_nombre,
                estado=estado_display,
                estado_lote=estado_lote,
            )
        )

    kpis.tmh_stock = round(kpis.tmh_stock, 2)
    kpis.tms_stock = round(kpis.tms_stock, 2)
    lotes_resumen.sort(key=lambda x: x.ip, reverse=True)

    return DashboardResponse(kpis=kpis, lotes=lotes_resumen)
