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
    cip: str
    laboratorio: str
    ley_cabeza: Decimal = Field(..., gt=0)
    ley_cola: Decimal = Field(..., ge=0)
    ley_liquido: Decimal | None = None
    origen_datos: str = OrigenDatos.MANUAL
    fecha_analisis: date | None = None


class AnalisisRecuperacionOut(BaseModel):
    id: int
    lote_id: int
    lote_ip: str | None = None
    cip: str | None
    laboratorio: str
    ley_cabeza: Decimal
    ley_cola: Decimal
    ley_liquido: Decimal | None
    recuperacion: Decimal | None
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
    laboratorio_destino: str | None  # laboratorio en mapeo_cip
    estado_ley: str  # PENDIENTE | COMPLETADO
    estado_recuperacion: str
    analisis_ley: list[AnalisisLeyOut] = []
    analisis_recuperacion: list[AnalisisRecuperacionOut] = []


# ── Vista Comercial: por Lote/IP ──────────────────────────────────────────────


class LoteLabOut(BaseModel):
    ip: str
    lote_id: int
    proveedor: str
    material: str | None
    fecha_recepcion: datetime | None
    cips: list[str]
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
