from datetime import date
from decimal import Decimal

from app.models.enums import OrigenDatos, TipoAnalisis
from pydantic import BaseModel, Field

# --- ANÁLISIS DE LEY (Fire Assay) ---


class AnalisisLeyCreate(BaseModel):
    cip: str = Field(..., description="Código CIP de la muestra")
    laboratorio: str = Field(..., description="Nombre del laboratorio")
    tipo_analisis: TipoAnalisis = Field(..., description="Ej: planta, externo, minero, dirimencia")
    material: str = Field("Au", description="Por defecto Au")
    ley_fino: Decimal
    ley_grueso: Decimal
    origen_datos: str | None = OrigenDatos.MANUAL
    fecha_analisis: date | None = None


class AnalisisLeyOut(BaseModel):
    id: int
    lote_id: int
    cip: str | None
    laboratorio: str
    tipo_analisis: str
    ley_fino: Decimal
    ley_grueso: Decimal
    ley_final: Decimal
    ley_gr_tm: Decimal
    vigente: bool
    fecha_analisis: date | None
    certificado_url: str | None

    class Config:
        from_attributes = True


# --- ANÁLISIS DE RECUPERACIÓN (Botella) ---


class AnalisisRecuperacionCreate(BaseModel):
    cip: str
    laboratorio: str
    ley_cabeza: Decimal
    ley_cola: Decimal
    ley_liquido: Decimal
    origen_datos: str | None = OrigenDatos.MANUAL
    fecha_analisis: date | None = None


class AnalisisRecuperacionOut(BaseModel):
    id: int
    lote_id: int
    cip: str | None
    laboratorio: str
    ley_cabeza: Decimal
    ley_cola: Decimal
    ley_liquido: Decimal
    recuperacion: Decimal
    vigente: bool
    fecha_analisis: date | None
    certificado_url: str | None

    class Config:
        from_attributes = True


# --- SYNC OFFLINE ---
class AnalisisLeyOfflineItem(BaseModel):
    offline_id: str
    datos: AnalisisLeyCreate


class SyncLaboratorioRequest(BaseModel):
    analisis_ley: list[AnalisisLeyOfflineItem] = []
    # Aquí podríamos agregar recuperacion_offline


# Añade esto al final del archivo
class MuestraLaboratorioItem(BaseModel):
    cip: str
    fecha_envio: date | None
    tipo_muestra: str | None
    estado_ley: str  # PENDIENTE | COMPLETADO
    estado_recuperacion: str  # PENDIENTE | COMPLETADO
