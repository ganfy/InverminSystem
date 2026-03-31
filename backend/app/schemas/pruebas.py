from datetime import datetime

from pydantic import BaseModel


# --- Base y Operaciones CRUD ---
class PruebaMetalurgicaBase(BaseModel):
    malla_porcentaje: float | None = None
    porcentaje_nacn: float | None = None
    ph_inicial: float | None = None
    ph_final: float | None = None
    adicion_nacn: float | None = None
    adicion_naoh: float | None = None
    gasto_agno3: float | None = None
    fecha_ingreso: datetime


class PruebaMetalurgicaCreate(PruebaMetalurgicaBase):
    pass


class PruebaMetalurgicaOut(PruebaMetalurgicaBase):
    id: int
    lote_id: int
    fecha_salida: datetime | None = None
    creado_por: int | None = None

    class Config:
        from_attributes = True


# --- Esquema para la Tabla Principal ---
class LotePruebaList(BaseModel):
    ip: str
    fecha_recepcion: datetime | None = None
    fecha_salida: datetime | None = None
    malla_porcentaje: float | None = None
    gasto_agno3: float | None = None
    estado: str


# --- Esquemas para la Sincronización Offline ---
class PruebaOfflineItem(BaseModel):
    offline_id: str
    ip: str
    datos: PruebaMetalurgicaCreate


class SyncResult(BaseModel):
    offline_id: str
    server_id: int | None = None
    error: str | None = None


class SyncPruebasRequest(BaseModel):
    pruebas: list[PruebaOfflineItem]


class SyncPruebasResponse(BaseModel):
    resultados: list[SyncResult]
