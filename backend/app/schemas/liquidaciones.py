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
