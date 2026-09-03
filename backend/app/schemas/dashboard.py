from datetime import UTC, date, datetime

from app.schemas.liquidaciones import LiquidacionResumenOut
from pydantic import BaseModel, Field, field_validator


def naive_to_utc(v: datetime | None) -> datetime | None:
    if isinstance(v, datetime) and v.tzinfo is None:
        return v.replace(tzinfo=UTC)
    return v


class DashboardKPIs(BaseModel):
    au_real_100: float = 0.0  # gr: Σ(TMS × ley_gr_tm)
    au_real_rec: float = Field(
        0.0, description="Post-recuperación"
    )  # gr: Σ(TMS × ley_gr_tm × rec%)
    tmh_stock: float = 0.0
    tms_stock: float = 0.0
    oz_stock: float = Field(
        0.0, description="Post-recuperación"
    )  # oz totales: au_real_100 / 31.1035
    oz_habilitados: float = 0.0  # oz de lotes habilitados_ruma sin asignar a ruma
    valor_compra_total: float = 0.0
    valor_compra_promedio: float | None = Field(None, description="Post-recuperación")
    rec_liq_promedio: float | None = Field(None, description="Post-recuperación")
    rec_planta_promedio: float | None = Field(None, description="Post-recuperación")
    inter_usd_promedio: float | None = Field(None, description="Post-recuperación")
    au_comprado: float = 0.0


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
    ruma_codigo: str | None = None


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


class ResumenPagosBloque(BaseModel):
    tms_total: float = 0.0
    tms_pagado: float = 0.0
    tms_sin_pagar: float = 0.0
    gr_recuperable_total: float = 0.0
    gr_recuperable_pagado: float = 0.0
    gr_recuperable_sin_pagar: float = 0.0
    total_usd_total: float = 0.0
    total_usd_pagado: float = 0.0
    total_usd_sin_pagar: float = 0.0


class ProfitAgregado(BaseModel):
    profit_maquila: float = 0.0
    profit_rec: float = 0.0
    profit_consumo: float = 0.0
    profit_leyes: float = 0.0
    profit_total: float = 0.0
    profit_rc: float = 0.0
    profit_terminos: float | None = None
    au_comprado: float = 0.0
    valor_compra_total: float = 0.0


class DashboardResponse(BaseModel):
    kpis: DashboardKPIs
    lotes: list[LoteDashboard]
    acopiadores_tmh: list[AcopiadorTMH]
    analisis_conteo: AnalisisConteo = AnalisisConteo()
    acopiadores_stats: list[AcopiadorStats] = []
    resumen_pagos: ResumenPagosBloque = ResumenPagosBloque()
    profit: ProfitAgregado = ProfitAgregado()
    liquidaciones: list[LiquidacionResumenOut] = []


class AlertaItem(BaseModel):
    tipo: str  # VOLADO_STOCK | RETRASO_MUESTREO | RETRASO_LEY | RETRASO_RECUPERACION
    severidad: str  # CRITICA | ALTA | MEDIA
    ip: str
    proveedor: str
    acopiador: str | None
    horas_retraso: float
    descripcion: str
    fecha_ref: datetime
    cips: list[str] = []


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


# =============================================================================
# TRAZABILIDAD POR LOTE
# =============================================================================


class UsuarioResumen(BaseModel):
    id: int
    nombre_completo: str
    rol: str  # código del rol


class AccionRegistro(BaseModel):
    por: UsuarioResumen | None = None
    fecha: datetime | None = None


class TrazabilidadSesion(BaseModel):
    id: int
    placa: str | None
    carreta: str | None
    conductor: str | None
    transportista: str | None
    guia_remision: str | None
    guia_transporte: str | None
    registro: AccionRegistro


class TrazabilidadPesaje(BaseModel):
    numero_ticket: str | None
    sacos: int | None
    granel: bool
    peso_inicial: float
    peso_final: float
    peso_neto: float
    fecha_inicio: datetime | None
    fecha_fin: datetime | None
    es_manual: bool
    justificacion_manual: str | None
    registro: AccionRegistro


class TrazabilidadMuestreo(BaseModel):
    intento: int
    peso_humedo: float
    peso_seco: float
    porcentaje_humedad: float | None
    tms_calculado: float | None
    observaciones: str | None
    registro: AccionRegistro


class TrazabilidadPrueba(BaseModel):
    cip: str | None
    fecha_ingreso: datetime | None
    fecha_salida: datetime | None  # fecha_ingreso + 48h
    malla_porcentaje: float | None
    porcentaje_nacn: float | None
    ph_inicial: float | None
    ph_final: float | None
    adicion_nacn: float | None
    adicion_naoh: float | None
    gasto_agno3: float | None
    registro: AccionRegistro

    @field_validator("fecha_ingreso", "fecha_salida", mode="before")
    @classmethod
    def validate_dates(cls, v):
        return naive_to_utc(v)


class TrazabilidadAnalisisLey(BaseModel):
    id: int
    cip: str | None
    laboratorio: str
    tipo_analisis: str
    material: str
    ley_final: float | None
    ley_gr_tm: float | None
    origen_datos: str
    fecha_analisis: date | None
    certificado_url: str | None
    vigente: bool
    descarte: AccionRegistro | None = None
    justificacion_descarte: str | None
    registro: AccionRegistro


class TrazabilidadAnalisisRec(BaseModel):
    id: int
    cip: str | None
    laboratorio: str
    ley_cabeza: float | None
    ley_cola: float | None
    ley_liquido: float | None
    recuperacion: float | None
    estado: str
    origen_datos: str
    fecha_analisis: date | None
    certificado_url: str | None
    vigente: bool
    descarte: AccionRegistro | None = None
    justificacion_descarte: str | None
    registro: AccionRegistro


class TrazabilidadRuma(BaseModel):
    codigo: str
    estado: str
    fecha_creacion: date | None
    campana: str | None  # código de campaña


class TrazabilidadLiquidacion(BaseModel):
    id: int
    numero_liquidacion: str | None
    estado: str
    precio_oro_usd: float | None
    valor_total_usd: float | None
    fino_recuperable: float | None
    ley_comercial: float | None
    usa_dirimencia: bool
    generacion: AccionRegistro
    cierre: AccionRegistro | None = None


class TrazabilidadAuditoria(BaseModel):
    registro_lote: AccionRegistro
    habilitacion_ruma: AccionRegistro
    cambio_estado: AccionRegistro


class TrazabilidadMapeoCIP(BaseModel):
    id: int
    codigo_cip: str
    laboratorio: str | None
    fecha_envio: date | None
    tipo_muestra: str | None


class TrazabilidadLoteResponse(BaseModel):
    ip: str
    estado: str
    tipo_material: str | None
    volado: bool
    dirimencia: bool
    habilitado_ruma: bool
    proveedor: str
    ruc_proveedor: str | None
    acopiador: str | None
    sesion: TrazabilidadSesion
    pesajes: list[TrazabilidadPesaje]
    muestreos: list[TrazabilidadMuestreo]
    prueba_metalurgica: TrazabilidadPrueba | None
    analisis_ley: list[TrazabilidadAnalisisLey]
    analisis_recuperacion: list[TrazabilidadAnalisisRec]
    ruma: TrazabilidadRuma | None
    liquidacion: TrazabilidadLiquidacion | None
    auditoria: TrazabilidadAuditoria
    mapeos_cip: list[TrazabilidadMapeoCIP] = []
