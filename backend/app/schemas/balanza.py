"""
Schemas Pydantic — Módulo Balanza
Cubre: SesionDescarga, Lote, Pesaje, LoteEliminado (auditoría).
"""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, field_validator, model_validator

# =============================================================================
# ENUMS / LITERALES  (espejo de models.enums para validación en capa schema)
# =============================================================================

TIPOS_MATERIAL = ("Mineral", "Llampo", "M.Llampo")
ESTADOS_SESION = ("EN_PROCESO", "COMPLETO", "PAUSADO")
ESTADOS_LOTE_ELIMINABLES = ("RECEPCIONADO", "LIQUIDADO", "FACTURADO")


# =============================================================================
# PESAJE
# =============================================================================


class PesajeCrear(BaseModel):
    """Datos de pesaje enviados al crear un lote."""

    peso_inicial: Decimal  # TM — peso con carga
    peso_final: Decimal  # TM — peso sin carga (tara)
    sacos: int | None = None
    granel: bool = False
    fecha_inicio: datetime | None = None  # si no viene, el servicio usa now()

    @field_validator("peso_inicial", "peso_final")
    @classmethod
    def positivo(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("El peso debe ser mayor a 0")
        return v

    @model_validator(mode="after")
    def peso_final_mayor(self) -> "PesajeCrear":
        """
        peso_final (BRUTO = camión cargado) > peso_inicial (TARA = camión vacío).
        Alineado con check constraint: ck_pesajes_peso_final_mayor_inicial.
        peso_neto = peso_final - peso_inicial.
        """
        if self.peso_final is not None and self.peso_inicial is not None:
            if self.peso_final <= self.peso_inicial:
                raise ValueError(
                    "peso_final (bruto) debe ser MAYOR que peso_inicial (tara). "
                    "Recuerda: peso_inicial = tara del camión vacío, "
                    "peso_final = peso bruto con carga."
                )
        return self


class PesajeRespuesta(BaseModel):
    id: int
    lote_id: int
    peso_inicial: Decimal
    peso_final: Decimal
    peso_neto: Decimal
    sacos: int | None = None
    granel: bool
    numero_ticket: str | None = None
    fecha_inicio: datetime | None = None
    fecha_fin: datetime | None = None

    model_config = {"from_attributes": True}


# =============================================================================
# LOTE
# =============================================================================


class LoteCrear(BaseModel):
    """Datos para agregar un lote a una sesión existente."""

    tipo_material: str = "Mineral"
    pesaje: PesajeCrear

    @field_validator("tipo_material")
    @classmethod
    def tipo_valido(cls, v: str) -> str:
        if v not in TIPOS_MATERIAL:
            raise ValueError(f"tipo_material debe ser uno de: {TIPOS_MATERIAL}")
        return v


class LoteResumen(BaseModel):
    """Lote resumido para la lista dentro de una sesión."""

    id: int
    ip: str
    numero_lote: int
    tipo_material: str | None = None
    estado: str
    volado: bool
    peso_neto: Decimal | None = None  # del pesaje vigente
    fecha_pesaje: datetime | None = None
    eliminado: bool

    model_config = {"from_attributes": True}


class LoteDetalle(LoteResumen):
    """Lote completo con datos de pesaje — para vista de sesión."""

    pesaje: PesajeRespuesta | None = None
    habilitado_ruma: bool
    fecha_habilitacion: datetime | None = None

    model_config = {"from_attributes": True}


# =============================================================================
# SESIÓN DE DESCARGA
# =============================================================================


class SesionCrear(BaseModel):
    """Formulario de nueva sesión (RF-BAL-001)."""

    provacop_id: int
    placa: str
    carreta: str | None = None
    conductor: str | None = None
    transportista: str | None = None
    razon_social: str | None = None
    guia_remision: str | None = None
    guia_transporte: str | None = None

    @field_validator("placa")
    @classmethod
    def placa_upper(cls, v: str) -> str:
        return v.strip().upper()


class SesionLista(BaseModel):
    """Fila en la lista de sesiones (BalanzaView)."""

    id: int
    fecha_ingreso: datetime  # = creado_en del AuditMixin
    proveedor_razon_social: str
    acopiador_razon_social: str
    es_propio: bool  # acopiador == proveedor
    placa: str
    guia_remision: str | None = None
    total_lotes: int
    lotes_activos: int  # sin soft delete
    estado: str

    model_config = {"from_attributes": True}


class SesionDetalle(BaseModel):
    """Detalle completo de sesión con todos sus lotes."""

    id: int
    provacop_id: int
    proveedor_id: int
    proveedor_razon_social: str
    proveedor_ruc: str | None = None
    acopiador_id: int
    acopiador_razon_social: str
    acopiador_ruc: str | None = None
    es_propio: bool
    placa: str
    carreta: str | None = None
    conductor: str | None = None
    transportista: str | None = None
    razon_social: str | None = None
    guia_remision: str | None = None
    guia_transporte: str | None = None
    estado: str
    fecha_ingreso: datetime
    lotes: list[LoteDetalle] = []

    model_config = {"from_attributes": True}


# =============================================================================
# ELIMINAR LOTE
# =============================================================================


class EliminarLoteRequest(BaseModel):
    """Payload para eliminar un lote (RF-BAL-004)."""

    motivo: str

    @field_validator("motivo")
    @classmethod
    def motivo_no_vacio(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("El motivo no puede estar vacío")
        return v.strip()


# =============================================================================
# PROVEEDOR-ACOPIADOR DROPDOWN  (para el formulario nueva sesión)
# =============================================================================


class ProvAcopDropdown(BaseModel):
    """Opción del autocomplete al crear sesión."""

    provacop_id: int
    proveedor_id: int
    proveedor_razon_social: str
    proveedor_ruc: str | None = None
    acopiador_id: int
    acopiador_razon_social: str
    acopiador_ruc: str | None = None
    es_propio: bool

    model_config = {"from_attributes": True}
