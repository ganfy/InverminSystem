from datetime import UTC, date, datetime
from decimal import Decimal

from app.models.enums import TipoMuestra
from pydantic import BaseModel, field_validator


def naive_to_utc(v: datetime | None) -> datetime | None:
    if isinstance(v, datetime) and v.tzinfo is None:
        return v.replace(tzinfo=UTC)
    return v


# ── Base CRUD ─────────────────────────────────────────────────────────────────


class PruebaMetalurgicaBase(BaseModel):
    malla_porcentaje: float | None = None
    porcentaje_nacn: float | None = None
    ph_inicial: float | None = None
    ph_final: float | None = None
    adicion_nacn: float | None = None
    adicion_naoh: float | None = None
    gasto_agno3: float | None = None
    fecha_ingreso: datetime | None = None

    @field_validator("fecha_ingreso", mode="before")
    @classmethod
    def validate_fecha_ingreso(cls, v):
        return naive_to_utc(v)


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

    @field_validator("fecha_salida", mode="before")
    @classmethod
    def validate_fecha_salida(cls, v):
        return naive_to_utc(v)


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

    @field_validator("fecha_recepcion", "fecha_ingreso", "fecha_salida", mode="before")
    @classmethod
    def validate_dates(cls, v):
        return naive_to_utc(v)


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

    @field_validator("fecha_salida", mode="before")
    @classmethod
    def validate_fecha_salida(cls, v):
        return naive_to_utc(v)


# ── Recuperaciones (vista Pruebas: leyes de cola + recuperación) ─────────────


class RecuperacionItem(BaseModel):
    """Resultado de análisis de recuperación: leyes de cola y % recuperación.
    Expuesto a TecnicoMuestreo sin mostrar ley_cabeza.
    """

    ip: str
    cip: str | None = None
    proveedor: str
    fecha_analisis: date | None
    # Ley cola sólidos
    ley_cola_au_oz_tc: Decimal | None = None  # oz/TC (campo ley_cola de DB)
    ley_cola_au_gr_tm: Decimal | None = None  # g/TM = oz_tc × 34.2857
    ley_cola_ag_gr_tm: Decimal | None = None  # g/TM directo del campo
    # Solución líquida (ambos en g/m³)
    solucion_au_g_m3: Decimal | None = None  # ley_liquido × 34.2857
    solucion_ag_g_m3: Decimal | None = None  # campo solucion_ag_g_m3
    # Resultado
    recuperacion: Decimal | None = None
    vigente: bool


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
