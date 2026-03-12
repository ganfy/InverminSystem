"""
Schemas Pydantic — Módulo Balanza
Cubre: SesionDescarga, Lote, Pesaje, LoteEliminado (auditoría).
"""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, field_validator, model_validator

# =============================================================================
# ENUMS / LITERALES
# =============================================================================

TIPOS_MATERIAL = ("Mineral", "Llampo", "M.Llampo")
ESTADOS_SESION = ("EN_PROCESO", "COMPLETO", "PAUSADO")
ESTADOS_LOTE_ELIMINABLES = ("RECEPCIONADO", "LIQUIDADO", "FACTURADO")


# =============================================================================
# PESAJE
# =============================================================================


class PesajeCrear(BaseModel):
    """Datos de pesaje enviados al crear un lote."""

    peso_inicial: Decimal  # TM — BRUTO (camión cargado, primer pesaje)
    peso_final: Decimal  # TM — TARA  (camión vacío, segundo pesaje tras descarga)
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
    def bruto_mayor_tara(self) -> "PesajeCrear":
        """
        peso_inicial (BRUTO = camión cargado) debe ser MAYOR que
        peso_final   (TARA  = camión vacío tras descarga).
        peso_neto = peso_inicial - peso_final.
        Alineado con constraint ck_pesajes_bruto_mayor_tara.
        """
        if self.peso_inicial is not None and self.peso_final is not None:
            if self.peso_inicial <= self.peso_final:
                raise ValueError(
                    "peso_inicial (bruto) debe ser MAYOR que peso_final (tara). "
                    "Recuerda: peso_inicial = bruto (camión cargado), "
                    "peso_final = tara (camión vacío)."
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


class LoteEditar(BaseModel):
    """
    Admin: modificar datos de un lote ya registrado.
    Solo accesible con rol Admin (verificado en router).
    """

    tipo_material: str | None = None
    peso_inicial: Decimal | None = None  # BRUTO — si se envía, validar con peso_final
    peso_final: Decimal | None = None  # TARA
    sacos: int | None = None
    granel: bool | None = None

    @field_validator("tipo_material")
    @classmethod
    def tipo_valido(cls, v: str | None) -> str | None:
        if v is not None and v not in TIPOS_MATERIAL:
            raise ValueError(f"tipo_material debe ser uno de: {TIPOS_MATERIAL}")
        return v

    @model_validator(mode="after")
    def bruto_mayor_tara(self) -> "LoteEditar":
        if self.peso_inicial is not None and self.peso_final is not None:
            if self.peso_inicial <= self.peso_final:
                raise ValueError("peso_inicial (bruto) debe ser MAYOR que peso_final (tara).")
        return self


class LoteResumen(BaseModel):
    """Lote resumido para la lista dentro de una sesión."""

    id: int
    ip: str
    numero_lote: int
    tipo_material: str | None = None
    estado: str
    volado: bool
    peso_neto: Decimal | None = None
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


class SesionEditar(BaseModel):
    """
    Edición de cabecera de sesión (corrección de errores de registro).
    A nivel BD: UPDATE directo sobre sesiones_descarga.
    Cambiar provacop_id modifica el par proveedor/acopiador de toda la sesión;
    los lotes NO almacenan provacop_id, por lo que no requiere cascada.
    Solo se actualiza lo que se envíe (PATCH parcial).
    """

    provacop_id: int | None = None
    placa: str | None = None
    carreta: str | None = None
    conductor: str | None = None
    transportista: str | None = None
    razon_social: str | None = None
    guia_remision: str | None = None
    guia_transporte: str | None = None

    @field_validator("placa")
    @classmethod
    def placa_upper(cls, v: str | None) -> str | None:
        return v.strip().upper() if v else v


class SesionLista(BaseModel):
    """Fila en la lista de sesiones (BalanzaView)."""

    id: int
    fecha_ingreso: datetime
    proveedor_razon_social: str
    acopiador_razon_social: str
    es_propio: bool
    placa: str
    guia_remision: str | None = None
    total_lotes: int
    lotes_activos: int
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
# AUTOCOMPLETE PROVEEDOR-ACOPIADOR
# =============================================================================


class ProvAcopDropdown(BaseModel):
    provacop_id: int
    proveedor_id: int
    proveedor_razon_social: str
    proveedor_ruc: str | None = None
    acopiador_id: int
    acopiador_razon_social: str
    acopiador_ruc: str | None = None
    es_propio: bool

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
