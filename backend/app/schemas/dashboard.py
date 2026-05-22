from datetime import datetime

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


class AnalisisConteo(BaseModel):
    listo: int = 0
    falta_rec: int = 0
    falta_ley: int = 0
    falta_muestreo: int = 0
    sin_datos: int = 0


class AcopiadorStats(BaseModel):
    acopiador: str
    lotes: int = 0
    tms: float = 0.0
    oz: float = 0.0
    ley_prom: float | None = None


class DashboardResponse(BaseModel):
    kpis: DashboardKPIs
    lotes: list[LoteDashboard]
    acopiadores_tmh: list[AcopiadorTMH]
    analisis_conteo: AnalisisConteo = AnalisisConteo()
    acopiadores_stats: list[AcopiadorStats] = []


class AlertaItem(BaseModel):
    tipo: str  # VOLADO_STOCK | RETRASO_MUESTREO | RETRASO_LEY | RETRASO_RECUPERACION
    severidad: str  # CRITICA | ALTA | MEDIA
    ip: str
    proveedor: str
    acopiador: str | None
    horas_retraso: float
    descripcion: str
    fecha_ref: datetime


class AlertasConfig(BaseModel):
    horas_pesado_muestreo: float = 24.0
    horas_muestreo_ley: float = 24.0
    horas_ley_recuperacion: float = 72.0
    dias_volado_stock: float = 30.0


class AlertasResponse(BaseModel):
    alertas: list[AlertaItem]
    config: AlertasConfig
    total_criticas: int = 0
    total_altas: int = 0
    total_medias: int = 0
