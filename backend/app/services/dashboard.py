from app.models.models import Lote, Muestreo, Pesaje, SesionDescarga
from app.schemas.dashboard import DashboardKPIs, DashboardResponse, LoteDashboard
from sqlalchemy.orm import Session


def obtener_resumen_dashboard(db: Session) -> DashboardResponse:
    # 1. Obtener todos los lotes activos
    lotes_db = db.query(Lote).filter(~Lote.eliminado).all()

    kpis = DashboardKPIs()
    lotes_resumen = []

    for lote in lotes_db:
        # 2. Obtener TMH real desde la tabla Pesaje (Bruto - Tara)
        tmh = 0.0
        pesaje = db.query(Pesaje).filter(Pesaje.lote_id == lote.id).first()
        if pesaje and pesaje.peso_inicial and pesaje.peso_final:
            if pesaje.peso_inicial > pesaje.peso_final:
                tmh = float(pesaje.peso_inicial - pesaje.peso_final)

        kpis.tmh_stock += tmh

        # Variables para cálculos
        h2o_porc = None
        tms = None

        # 3. Buscar Muestreo para calcular %H2O y TMS
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

        # 4. Extraer datos del proveedor desde Sesion -> ProvAcop
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

        estado_display = lote.estado if lote.estado else "EN PROCESO"
        # 5. Armar la fila del schema Dashboard
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
            )
        )
    # Redondear KPIs finales
    kpis.tmh_stock = round(kpis.tmh_stock, 2)
    kpis.tms_stock = round(kpis.tms_stock, 2)

    # Ordenar por IP descendente
    lotes_resumen.sort(key=lambda x: x.ip, reverse=True)

    return DashboardResponse(kpis=kpis, lotes=lotes_resumen)
