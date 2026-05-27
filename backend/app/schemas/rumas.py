"""
Schemas del módulo de Rumas y Campañas.
"""

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field

# ── CAMPAÑAS ──────────────────────────────────────────────────────────────────


class CampanaCreate(BaseModel):
    meta_oro_fino: Decimal = Field(default=Decimal("5000.00"), gt=0)


class CampanaEditarMeta(BaseModel):
    meta_oro_fino: Decimal = Field(..., gt=0)


class CampanaCerrarRequest(BaseModel):
    """Al cerrar campaña se crea la siguiente; se pide la meta de la nueva."""

    meta_oro_fino_nueva: Decimal = Field(
        ..., gt=0, description="Meta en gramos para la nueva campaña"
    )


class CampanaOut(BaseModel):
    id: int
    codigo: str
    meta_oro_fino: Decimal
    fecha_inicio: date
    fecha_cierre: date | None
    estado: str
    oro_fino_acumulado: Decimal
    total_lotes: int
    total_toneladas: Decimal
    total_rumas: int
    # calculados
    progreso_pct: float
    dias_transcurridos: int | None

    model_config = {"from_attributes": True}


# ── RUMAS ─────────────────────────────────────────────────────────────────────


class RumaCreate(BaseModel):
    """Crear ruma vacía en la campaña activa."""

    pass  # el código se genera en el backend


class LoteRumaItem(BaseModel):
    """Lote dentro del detalle de una ruma."""

    ip: str
    proveedor: str
    tmh: float
    tms: float | None
    ley_avg: float | None
    rec_porc: float | None
    tipo_material: str | None
    habilitado_ruma: bool
    volado: bool

    model_config = {"from_attributes": True}


class RumaOut(BaseModel):
    id: int
    codigo: str
    numero_ruma: int
    fecha_creacion: date
    estado: str
    lotes: list[LoteRumaItem] = []
    # totales calculados
    total_lotes: int = 0
    total_tms: float = 0.0
    ley_ponderada: float | None = None
    rec_promedio: float | None = None
    pct_llampo: float | None = None

    model_config = {"from_attributes": True}


class RumaLista(BaseModel):
    """Vista resumida para el listado de rumas."""

    id: int
    codigo: str
    numero_ruma: int
    fecha_creacion: date
    estado: str
    total_lotes: int = 0
    total_tms: float = 0.0
    ley_ponderada: float | None = None
    rec_promedio: float | None = None

    model_config = {"from_attributes": True}


class AsignarLotesRequest(BaseModel):
    """Batch: lista de IPs a asignar a la ruma (reemplaza la asignación actual)."""

    ips: list[str] = Field(..., min_length=1)


class LoteDisponibleOut(BaseModel):
    """Lote habilitado para ruma, sin ruma asignada aún."""

    ip: str
    proveedor: str
    acopiador: str | None
    tmh: float
    tms: float | None
    ley_avg: float | None
    rec_porc: float | None
    tipo_material: str | None
    volado: bool
    dias_almacen: int

    model_config = {"from_attributes": True}


class HabilitarRumaRequest(BaseModel):
    motivo: str | None = None
