from datetime import date, datetime
from decimal import Decimal

from app.models.enums import OrigenDatos, TipoAnalisis
from pydantic import BaseModel, Field

# ── Análisis de Ley (Fire Assay triple sampling) ──────────────────────────────


class AnalisisLeyCreate(BaseModel):
    cip: str = Field(..., description="Código CIP de la muestra")
    laboratorio: str = Field(..., description="Nombre del laboratorio")
    tipo_analisis: TipoAnalisis = Field(..., description="planta | externo | minero | dirimencia")
    material: str = Field("Au", description="Material analizado")
    ley_fino: Decimal = Field(..., gt=0, description="Oz/TC fracción -140 (malla fina)")
    ley_grueso: Decimal = Field(..., gt=0, description="Oz/TC fracción +140 (malla gruesa)")
    origen_datos: str = OrigenDatos.MANUAL
    fecha_analisis: date | None = None


class AnalisisLeyOut(BaseModel):
    id: int
    lote_id: int
    lote_ip: str | None = None  # Solo si el solicitante tiene permiso
    cip: str | None
    laboratorio: str
    tipo_analisis: str
    material: str
    ley_fino: Decimal
    ley_grueso: Decimal
    ley_final: Decimal
    ley_gr_tm: Decimal
    vigente: bool
    fecha_analisis: date | None
    certificado_url: str | None
    descartado_por: int | None = None
    fecha_descarte: datetime | None = None
    justificacion_descarte: str | None = None

    model_config = {"from_attributes": True}


# ── Análisis de Recuperación ──────────────────────────────────────────────────


class AnalisisRecuperacionCreate(BaseModel):
    """Para registro manual directo (laboratorio externo via certificado, o lab propio sin pending)."""

    cip: str
    laboratorio: str
    ley_cabeza: Decimal = Field(..., gt=0)
    ley_cola: Decimal = Field(..., ge=0)
    ley_liquido: Decimal | None = None
    origen_datos: str = OrigenDatos.MANUAL
    fecha_analisis: date | None = None


class CompletarRecuperacionRequest(BaseModel):
    """Para que laboratorista complete un pending (ley_cola + ley_liquido)."""

    ley_cola: Decimal = Field(..., ge=0)
    ley_liquido: Decimal | None = None
    fecha_analisis: date | None = None


class EnviarRecuperacionInternaRequest(BaseModel):
    """
    Comercial crea un registro pendiente de recuperación para el laboratorio interno.
    El CIP debe ser de tipo RecuperacionInterno.
    Si el lote tiene solo 1 CIP interno, se puede omitir (se usa automáticamente).
    """

    cip: str | None = None  # None → sistema elige el único RecuperacionInterno del lote
    laboratorio: str = "Laboratorio Interno"


class AnalisisRecuperacionOut(BaseModel):
    id: int
    lote_id: int
    lote_ip: str | None = None
    cip: str | None
    laboratorio: str
    ley_cabeza: Decimal | None
    ley_cola: Decimal | None
    ley_liquido: Decimal | None
    recuperacion: Decimal | None
    estado: str  # PENDIENTE | COMPLETADO
    vigente: bool
    fecha_analisis: date | None
    certificado_url: str | None
    descartado_por: int | None = None
    fecha_descarte: datetime | None = None

    model_config = {"from_attributes": True}


# ── Acciones de Comercial ─────────────────────────────────────────────────────


class DescartarRequest(BaseModel):
    justificacion: str


# ── Vista Laboratorista: por CIP ──────────────────────────────────────────────


class CIPAnalisisOut(BaseModel):
    cip: str
    lote_id: int
    lote_ip: str | None = None  # None para Laboratorista, IP real para Comercial
    fecha_envio: date | None
    tipo_muestra: str | None
    laboratorio_destino: str | None
    estado_ley: str  # PENDIENTE | COMPLETADO (para CIPs tipo Laboratorio)
    estado_recuperacion: str  # PENDIENTE | COMPLETADO (para CIPs tipo Recuperacion*)
    analisis_ley: list[AnalisisLeyOut] = []
    analisis_recuperacion: list[AnalisisRecuperacionOut] = []


# ── Vista Comercial: por Lote/IP ──────────────────────────────────────────────


class CIPResumen(BaseModel):
    """Resumen de un CIP con su tipo para la vista de Comercial."""

    codigo_cip: str
    tipo_muestra: str | None
    laboratorio: str | None


class LoteLabOut(BaseModel):
    ip: str
    lote_id: int
    proveedor: str
    material: str | None
    fecha_recepcion: datetime | None
    cips: list[str]  # todos los CIPs del lote (compatibilidad)
    cips_detalle: list[CIPResumen] = []  # CIPs con tipo para UI
    ley_planta: Decimal | None = None  # calculada on-the-fly
    ley_minero: Decimal | None = None  # del análisis tipo minero vigente
    analisis_ley: list[AnalisisLeyOut]
    analisis_recuperacion: list[AnalisisRecuperacionOut]
    tiene_dirimencia: bool


# ── Sync Offline ──────────────────────────────────────────────────────────────


class AnalisisLeyOfflineItem(BaseModel):
    offline_id: str
    datos: AnalisisLeyCreate


class AnalisisRecuperacionOfflineItem(BaseModel):
    offline_id: str
    datos: AnalisisRecuperacionCreate


class SyncLaboratorioRequest(BaseModel):
    analisis_ley: list[AnalisisLeyOfflineItem] = []
    analisis_recuperacion: list[AnalisisRecuperacionOfflineItem] = []


class SyncResultado(BaseModel):
    offline_id: str
    server_id: int | None
    error: str | None


class SyncLaboratorioResponse(BaseModel):
    resultados_ley: list[SyncResultado] = []
    resultados_recuperacion: list[SyncResultado] = []
