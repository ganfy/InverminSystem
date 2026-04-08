from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

# ── Base CRUD ─────────────────────────────────────────────────────────────────


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
    cip: str | None = None
    fecha_salida: datetime | None = None
    creado_por: int | None = None

    model_config = {"from_attributes": True}


# ── Lista principal ───────────────────────────────────────────────────────────


class LotePruebaList(BaseModel):
    ip: str
    fecha_recepcion: datetime | None = None
    fecha_ingreso: datetime | None = None
    fecha_salida: datetime | None = None
    malla_porcentaje: float | None = None
    gasto_agno3: float | None = None
    estado: str  # PENDIENTE | EN PROCESO | COMPLETADO
    # Etiquetado
    cip_asignado: str | None = None  # CIP de recuperación (si fue etiquetado)
    etiquetado: bool = False


# ── Etiquetado (nuevo) ────────────────────────────────────────────────────────


class EtiquetadoPruebaOut(BaseModel):
    ip: str
    cip: str
    mensaje: str = "Etiqueta de recuperación generada"


# ── Pruebas listas para recuperación (nuevo) ─────────────────────────────────


class PruebaRecuperacionItem(BaseModel):
    """
    Prueba COMPLETADO cuyo lote ya tiene ley planta calculada.
    Se usa en Laboratorio para pre-llenar ley_cabeza en análisis de recuperación.
    """

    ip: str
    cip: str  # CIP de la prueba (para recuperación)
    lote_id: int
    proveedor: str
    fecha_salida: datetime | None  # cuando se completaron las 48h
    ley_cabeza: Decimal  # ley planta promediada por Comercial
    tiene_analisis_recuperacion: bool = False


# ── Sync Offline ──────────────────────────────────────────────────────────────


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
