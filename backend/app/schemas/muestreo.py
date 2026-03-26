from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


# ==========================================
# MUESTREO (HUMEDAD)
# ==========================================
class MuestreoCreate(BaseModel):
    intento: int = Field(..., ge=1, le=3, description="Número de intento (1, 2 o 3)")
    peso_humedo: Decimal = Field(..., gt=0)
    peso_seco: Decimal = Field(..., gt=0)
    observaciones: str | None = None
    fecha_muestreo: datetime | None = None


class MuestreoOut(BaseModel):
    id: int
    lote_id: int
    intento: int
    peso_humedo: Decimal
    peso_seco: Decimal
    porcentaje_humedad: Decimal
    tms_calculado: Decimal
    creado_en: datetime
    creado_por: int
    observaciones: str | None = None

    class Config:
        model_config = {"from_attributes": True}


# ==========================================
# CÓDIGOS CIP
# ==========================================
class GenerarCipsRequest(BaseModel):
    cantidad: int = Field(default=2, ge=1, le=5, description="Cantidad de bolsas para laboratorio")
    laboratorio: str | None = "Por definir"


class MapeoCIPOut(BaseModel):
    id: int
    lote_id: int
    codigo_cip: str
    laboratorio: str | None
    tipo_muestra: str | None

    class Config:
        model_config = {"from_attributes": True}


# ==========================================
# SYNC OFFLINE
# ==========================================
class MuestreoOfflineItem(BaseModel):
    offline_id: str
    ip: str
    datos: MuestreoCreate


class SyncMuestreosRequest(BaseModel):
    muestreos: list[MuestreoOfflineItem]


class SyncResult(BaseModel):
    offline_id: str
    server_id: int | None = None
    error: str | None = None


class SyncMuestreosResponse(BaseModel):
    resultados: list[SyncResult]
