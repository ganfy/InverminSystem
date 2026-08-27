"""
Schemas del modulo de liquidaciones.
"""

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field

# ── Requests ──────────────────────────────────────────────────────────────────


class LotePreviewInput(BaseModel):
    ip: str
    bono: Decimal | None = Decimal("0")
    rec_liq_override: Decimal | None = None
    gasto_acopio_override: Decimal | None = None
    gasto_consumo_override: Decimal | None = None
    spot_usd_override: Decimal | None = None
    spot_ag_usd_override: Decimal | None = None


class LiquidacionPreviewRequest(BaseModel):
    provacop_id: int
    lotes: list[LotePreviewInput]
    spot_usd: Decimal | None = None
    spot_ag_usd: Decimal | None = Field(None, gt=0, description="Precio spot plata USD/Oz Troy")
    fecha_liquidacion: date | None = None


class LiquidacionCreate(BaseModel):
    provacop_id: int
    lotes: list[LotePreviewInput]
    spot_usd: Decimal | None = None
    spot_ag_usd: Decimal | None = Field(None, gt=0, description="Precio spot plata USD/Oz Troy")
    fecha_liquidacion: date | None = None
    numero_liquidacion: str | None = None  # si None: auto-generado
    como_borrador: bool = (
        False  # si True, no se asigna número ni fecha de emisión, y estado queda en BORRADOR
    )


class LiquidacionEstadoUpdate(BaseModel):
    estado: str  # GENERADA | FACTURADA | PAGADA


# ── Response items ────────────────────────────────────────────────────────────


class AlertaLote(BaseModel):
    tipo: str  # VOLADO | VENCIMIENTO_30D | SIN_LEY_MINERO | SIN_RECUPERACION | SIN_PARAMS
    mensaje: str
    critico: bool  # bloquea creacion si True


class LoteDisponible(BaseModel):
    ip: str
    proveedor: str | None = None
    acopiador: str | None = None
    provacop_id: int | None = None
    tipo_material: str | None
    fecha_recepcion: date | None
    dias_almacen: int
    tms: float | None
    tmh: float | None
    sacos: int | None
    volado: bool
    alerta_vencimiento: bool
    ley_comercial: float | None = None
    oz_tc_planta: float | None = None
    oz_tc_minero: float | None = None
    porcentaje_rec: float | None = None
    usa_dirimencia: bool = False
    listo_para_liquidar: bool = False
    liquidacion_id: int | None = None
    numero_liquidacion: str | None = None
    guia_remision: str | None = None


class LoteFinancieroOut(BaseModel):
    ip: str
    proveedor: str | None = None
    fecha_recepcion: date | None
    tmh: Decimal
    pct_humedad: Decimal
    tms: Decimal
    sacos: int | None

    # Leyes
    oz_tc_planta: Decimal
    oz_tc_comercial: Decimal
    oz_tc_minero: Decimal
    oz_tc_promedio: Decimal

    # Recuperacion
    pct_rec_liq: Decimal
    pct_rec_planta: Decimal | None

    # Parametros comerciales aplicados
    maquila: Decimal  # TC US$/TC calculado
    riesgo: Decimal
    spot_usd: Decimal
    insumos_acopio: Decimal
    insumos_consumo: Decimal
    insumos_total: Decimal
    bono: Decimal
    factor: Decimal

    # Resultados
    precio_x_tms: Decimal
    total_usd: Decimal
    fino_recuperable: Decimal  # Oz troy compradas

    # Profits Operativos (Calculados dinámicamente)
    profit_maquila: Decimal | None = None
    profit_rec: Decimal | None = None
    profit_consumo: Decimal | None = None
    profit_leyes: Decimal | None = None
    profit_total: Decimal | None = None

    usa_dirimencia: bool
    alertas: list[AlertaLote]

    # Plata (Ag) — presentes solo si aplica
    ley_ag_gr_tm: Decimal | None = None
    ley_ag_oz_tc: Decimal | None = None
    spot_ag_usd: Decimal | None = None
    valor_ag_usd: Decimal | None = None
    aplica_ag: bool = False

    # Spot histórico por fecha de recepción
    fecha_spot_efectiva: date | None = None  # fecha del LBMA Fix usado
    spot_desde_historico: bool = False  # True si vino de spot_historico, False si fue fallback

    model_config = {"from_attributes": True}


class LiquidacionPreviewOut(BaseModel):
    provacop_id: int
    proveedor_razon_social: str
    proveedor_ruc: str | None
    acopiador_nombre: str
    spot_usd: Decimal | None = None
    lotes: list[LoteFinancieroOut]

    # Totales
    total_usd: Decimal
    total_tms: Decimal
    total_tmh: Decimal
    total_oz_compradas: Decimal
    count_lotes: int

    alertas_globales: list[AlertaLote]
    puede_generar: bool
    total_ag_usd: Decimal = Decimal("0")  # solo si aplica Ag
    hay_ag: bool = False


class LiquidacionLoteOut(LoteFinancieroOut):
    liquidacion_id: int
    fecha_emision: date | None

    model_config = {"from_attributes": True}


class LiquidacionResumenOut(BaseModel):
    id: int
    numero_liquidacion: str
    estado: str
    provacop_id: int
    proveedor_razon_social: str
    proveedor_ruc: str | None
    acopiador_nombre: str
    spot_usd: Decimal | None = None
    total_usd: Decimal
    count_lotes: int
    fecha_creacion: datetime

    model_config = {"from_attributes": True}


class LiquidacionDetalleOut(LiquidacionResumenOut):
    lotes: list[LiquidacionLoteOut]
    pdf_url: str | None
    fecha_cierre: datetime | None

    model_config = {"from_attributes": True}


class LiquidacionesKPIOut(BaseModel):
    borradores: int
    generadas: int
    lotes_liquidables: int
    valor_pendiente_usd: float


class LiquidacionLoteParamsUpdate(BaseModel):
    """Edición manual de parámetros por Admin/Gerencia en liquidaciones NO generadas."""

    bono: Decimal | None = Decimal("0")
    rec_liq_override: Decimal | None = None
    riesgo_override: Decimal | None = None
    maquila_override: Decimal | None = None
    gasto_acopio_override: Decimal | None = None
    gasto_consumo_override: Decimal | None = None
    spot_usd_override: Decimal | None = None
    spot_ag_usd_override: Decimal | None = None
