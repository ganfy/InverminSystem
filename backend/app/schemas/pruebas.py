from datetime import datetime
from decimal import Decimal

from app.models.enums import TipoMuestra
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
    # cip ya no existe en el modelo - se obtiene desde mapeo_cip
    cips_recuperacion: list[str] = []  # CIPs de recuperación generados para este lote
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
    cip_asignado: str | None = None  # primer CIP de recuperación (si fue etiquetado)
    etiquetado: bool = False


# ── Etiquetado ────────────────────────────────────────────────────────────────


class EtiquetarPruebaRequest(BaseModel):
    tipo: TipoMuestra = TipoMuestra.RECUPERACION_INTERNO


class EtiquetadoPruebaOut(BaseModel):
    ip: str
    cip: str
    tipo: TipoMuestra
    mensaje: str = "Etiqueta de recuperación generada"


# ── Pruebas listas para recuperación ─────────────────────────────────────────


class PruebaRecuperacionItem(BaseModel):
    """
    Prueba COMPLETADO cuyo lote ya tiene ley planta calculable.
    Comercial usa esto para crear el registro pendiente de recuperación
    en el laboratorio interno.
    """

    ip: str
    cip: str  # CIP de recuperación interno
    lote_id: int
    proveedor: str
    fecha_salida: datetime | None
    ley_cabeza: Decimal  # ley planta calculada (snapshot al crear pending)
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
