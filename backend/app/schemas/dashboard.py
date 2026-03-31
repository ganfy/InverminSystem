from pydantic import BaseModel


class DashboardKPIs(BaseModel):
    au_real_100: float = 0.0
    au_real_rec: float = 0.0
    tmh_stock: float = 0.0
    tms_stock: float = 0.0
    oz_stock: float = 0.0


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
    estado: str


class DashboardResponse(BaseModel):
    kpis: DashboardKPIs
    lotes: list[LoteDashboard]
