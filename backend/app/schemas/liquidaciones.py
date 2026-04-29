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
    rec_liq_override: Decimal | None = None  # sobreescribir % rec liquidacion


class LiquidacionPreviewRequest(BaseModel):
    provacop_id: int
    lotes: list[LotePreviewInput]
    spot_usd: Decimal = Field(..., gt=0, description="Precio spot del oro en USD/Oz Troy")
    fecha_liquidacion: date | None = None


class LiquidacionCreate(BaseModel):
    provacop_id: int
    lotes: list[LotePreviewInput]
    spot_usd: Decimal = Field(..., gt=0)
    fecha_liquidacion: date | None = None
    numero_liquidacion: str | None = None  # si None: auto-generado


class LiquidacionEstadoUpdate(BaseModel):
    estado: str  # GENERADA | FACTURADA | PAGADA


# ── Response items ────────────────────────────────────────────────────────────


class AlertaLote(BaseModel):
    tipo: str  # VOLADO | VENCIMIENTO_30D | SIN_LEY_MINERO | SIN_RECUPERACION | SIN_PARAMS
    mensaje: str
    critico: bool  # bloquea creacion si True


class LoteFinancieroOut(BaseModel):
    ip: str
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

    usa_dirimencia: bool
    alertas: list[AlertaLote]

    class Config:
        from_attributes = True


class LiquidacionPreviewOut(BaseModel):
    provacop_id: int
    proveedor_razon_social: str
    proveedor_ruc: str | None
    acopiador_nombre: str
    spot_usd: Decimal
    lotes: list[LoteFinancieroOut]

    # Totales
    total_usd: Decimal
    total_tms: Decimal
    total_tmh: Decimal
    total_oz_compradas: Decimal
    count_lotes: int

    alertas_globales: list[AlertaLote]
    puede_generar: bool  # False si hay alertas criticas


class LiquidacionLoteOut(LoteFinancieroOut):
    liquidacion_id: int
    fecha_emision: date | None

    class Config:
        from_attributes = True


class LiquidacionResumenOut(BaseModel):
    id: int
    numero_liquidacion: str
    estado: str
    provacop_id: int
    proveedor_razon_social: str
    proveedor_ruc: str | None
    acopiador_nombre: str
    spot_usd: Decimal
    total_usd: Decimal
    count_lotes: int
    fecha_creacion: datetime

    class Config:
        from_attributes = True


class LiquidacionDetalleOut(LiquidacionResumenOut):
    lotes: list[LiquidacionLoteOut]
    pdf_url: str | None
    fecha_cierre: datetime | None

    class Config:
        from_attributes = True


# ── Salida: selector de relaciones proveedor-acopiador ────────────────────────


class ProvacoPSelectorOut(BaseModel):
    id: int
    proveedor: str
    proveedor_ruc: str | None
    acopiador: str
    tiene_parametros: bool
    # Parámetros comerciales (si existen) para preview en wizard paso 3
    maquila: Decimal | None = None
    comision: Decimal | None = None
    gasto_acopio: Decimal | None = None
    gasto_consumo: Decimal | None = None
    riesgo_comercial: Decimal | None = None

    model_config = {"from_attributes": True}


# ── Salida: lote liquidable (tab "Lotes liquidables" + paso 2 del wizard) ─────


class LoteLiquidableOut(BaseModel):
    lote_id: int
    ip: str
    provacop_id: int
    proveedor: str
    acopiador: str
    ruc_proveedor: str | None
    material: str | None
    estado: str
    fecha_recepcion: datetime | None
    # Datos calculados de análisis
    tms: float | None  # del último muestreo
    ley_comercial: float | None  # oz/tc: promedio labs o dirimencia
    ley_gr_tm: float | None  # ley_comercial * 34.2857
    usa_dirimencia: bool
    oz_tc_planta: float | None  # promedio planta+externo
    oz_tc_minero: float | None  # ley tipo minero
    porcentaje_rec: float | None  # % recuperación del análisis vigente

    model_config = {"from_attributes": True}


# ── Creación de liquidación (POST /liquidaciones) ─────────────────────────────


class LiquidacionCreate(BaseModel):
    provacop_id: int
    precio_oro_usd: Decimal = Field(..., gt=0, description="Precio Au USD/oz (entrada manual)")
    lote_ids: list[int] = Field(..., min_length=1, description="IDs de lotes a incluir")


# ── Detalle de lote dentro de una liquidación ─────────────────────────────────


class LiquidacionLoteOut(BaseModel):
    lote_id: int
    ip: str
    material: str | None = None
    tms: float | None = None
    ley_comercial: Decimal | None
    usa_dirimencia: bool
    oz_tc_planta: Decimal | None
    oz_tc_comercial: Decimal | None
    oz_tc_minero: Decimal | None
    oz_tc_promedio: Decimal | None
    porcentaje_rec_liquido: Decimal | None
    porcentaje_rec_planta: Decimal | None
    fino_recuperable: Decimal | None
    gasto_acopio_liquidacion: Decimal | None
    bono: Decimal | None
    insumos_liquidacion: Decimal | None

    model_config = {"from_attributes": True}


# ── Salida completa de liquidación ────────────────────────────────────────────


class LiquidacionOut(BaseModel):
    id: int
    numero_liquidacion: str | None
    provacop_id: int
    proveedor: str
    acopiador: str
    ruc_proveedor: str | None = None
    precio_oro_usd: Decimal | None
    valor_total_usd: Decimal | None
    estado: str
    pdf_url: str | None
    creado_en: datetime | None
    lotes: list[LiquidacionLoteOut] = []

    model_config = {"from_attributes": True}


# ── Item de lista (tabla dashboard) ──────────────────────────────────────────


class LiquidacionListItem(BaseModel):
    id: int
    numero_liquidacion: str | None
    provacop_id: int
    proveedor: str
    acopiador: str
    num_lotes: int
    tms_total: float | None
    precio_oro_usd: Decimal | None
    valor_total_usd: Decimal | None
    estado: str
    pdf_url: str | None
    creado_en: datetime | None

    model_config = {"from_attributes": True}


# ── KPIs del dashboard ────────────────────────────────────────────────────────


class LiquidacionesKPIOut(BaseModel):
    borradores: int
    generadas: int
    lotes_liquidables: int
    valor_pendiente_usd: float


# ── Cambio de estado ──────────────────────────────────────────────────────────


class CambiarEstadoRequest(BaseModel):
    estado: str = Field(..., description="BORRADOR | GENERADA | FACTURADA | PAGADA")
