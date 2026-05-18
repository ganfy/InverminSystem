from pydantic import BaseModel


class DashboardKPIs(BaseModel):
    au_real_100: float = 0.0  # gr: Σ(TMS × ley_gr_tm)
    au_real_rec: float = 0.0  # gr: Σ(TMS × ley_gr_tm × rec%)
    tmh_stock: float = 0.0
    tms_stock: float = 0.0
    oz_stock: float = 0.0  # oz totales: au_real_100 / 31.1035
    oz_habilitados: float = 0.0  # oz de lotes habilitados_ruma sin asignar a ruma


class LoteDashboard(BaseModel):
    ip: str
    tmh: float
    tms: float | None
    h2o_porc: float | None
    proveedor: str
    ruc: str | None
    ley_avg: float | None
    rec_porc: float | None
    acopiador: str | None
    estado: str  # ciclo de vida: RECEPCIONADO, ASIGNADO_RUMA, LIQUIDADO…
    estado_analisis: str  # pipeline análisis: SIN_DATOS | EN_LAB | FALTA_REC | LISTO
    habilitado_ruma: bool
    volado: bool
    dirimencia: bool
    dias_almacen: int
    tiene_rec_pendiente: bool = False


class AcopiadorTMH(BaseModel):
    acopiador: str
    enero: float = 0.0
    febrero: float = 0.0
    marzo: float = 0.0
    abril: float = 0.0
    mayo: float = 0.0
    junio: float = 0.0
    julio: float = 0.0
    agosto: float = 0.0
    septiembre: float = 0.0
    octubre: float = 0.0
    noviembre: float = 0.0
    diciembre: float = 0.0
    total: float = 0.0


class DashboardResponse(BaseModel):
    kpis: DashboardKPIs
    lotes: list[LoteDashboard]
    acopiadores_tmh: list[AcopiadorTMH]
