"""
Schemas de entidades (proveedores/acopiadores).
Orientados a la pantalla de gestión de terceros.
"""

from enum import Enum

from pydantic import BaseModel, EmailStr, field_validator


class TipoAcopiador(str, Enum):
    """Opciones del dropdown de acopiador en la UI."""

    SIN_ACOPIADOR = "sin_acopiador"  # autogestiona, misma entidad
    PROPIO = "propio"  # explícito pero misma entidad
    TERCERO = "tercero"  # otra entidad existente


# =============================================================================
# PARÁMETROS COMERCIALES
# =============================================================================


class ParametrosSchema(BaseModel):
    """
    Parámetros comerciales por relación proveedor-acopiador.
    Todos opcionales en edición — solo se actualizan los que vienen.
    """

    # Umbrales de recuperación
    umbral_recup_bajo: float | None = None  # Recuperación rango 1 (ley <)
    umbral_recup_medio: float | None = None  # Recuperación rango 2 (ley >)
    lim_ley_inferior: float | None = None  # Ley promedio desde
    lim_ley_superior: float | None = None  # Ley promedio hasta

    # Parámetros comerciales
    gasto_acopio: float | None = None
    gasto_consumo: float | None = None
    maquila: float | None = None  # %
    comision: float | None = None  # %

    # Lógica de ley comercial
    lim_ley_comercial: float | None = None  # Si ley comercial <
    dscto_ley_comercial: float | None = None  # → ley -
    porcentaje_ley_comercial: float | None = None  # Si no → ley ×

    # Extra del Excel
    riesgo_comercial: float | None = None


class ParametrosRespuesta(ParametrosSchema):
    id: int
    provacop_id: int

    model_config = {"from_attributes": True}


# =============================================================================
# RESPUESTAS
# =============================================================================


class AcopiadorResumen(BaseModel):
    """Datos básicos del acopiador para mostrar en detalle del proveedor."""

    id: int
    razon_social: str
    ruc: str | None = None
    es_propio: bool  # True si es la misma entidad que el proveedor

    model_config = {"from_attributes": True}


class TerceroRespuesta(BaseModel):
    """Detalle completo de un tercero — pantalla de edición."""

    id: int
    razon_social: str
    ruc: str | None = None
    referencia: str | None = None
    telefono: str | None = None
    email: str | None = None
    activo: bool
    provacop_id: int | None = None
    acopiador: AcopiadorResumen | None = None
    parametros: ParametrosRespuesta | None = None

    model_config = {"from_attributes": True}


class TerceroLista(BaseModel):
    id: int
    provacop_id: int
    razon_social: str
    ruc: str | None = None
    referencia: str | None = None
    activo: bool
    acopiador: str | None = None

    model_config = {"from_attributes": True}


class AcopiadorDropdown(BaseModel):
    """Para poblar el dropdown de selección de acopiador."""

    id: int
    razon_social: str
    ruc: str | None = None

    model_config = {"from_attributes": True}


class AcopiadorNuevo(BaseModel):
    """Payload para crear un nuevo acopiador desde la UI."""

    razon_social: str
    ruc: str | None = None  # TO DO: ver si añadir opción para registrar RUC en UI


# =============================================================================
# CREACIÓN DE TERCERO
# =============================================================================


class TerceroCrear(BaseModel):
    """
    Payload para crear un proveedor con su acopiador y parámetros.
    Refleja la pantalla 'Registrar tercero'.
    """

    # Datos del proveedor
    razon_social: str
    ruc: str | None = None
    referencia: str | None = None  # procedencia
    telefono: str | None = None
    email: EmailStr | None = None

    # Tipo de acopiador
    tipo_acopiador: TipoAcopiador

    # Solo requerido si tipo_acopiador == TERCERO
    acopiador_id: int | None = None  # entidad_id del acopiador existente
    acopiador_nuevo: AcopiadorNuevo | None = None  # datos para crear un nuevo acopiador (opcional)

    # Parámetros comerciales (opcionales al crear)
    parametros: ParametrosSchema | None = None

    @field_validator("ruc")
    @classmethod
    def ruc_valido(cls, v: str) -> str:
        v = v.strip()
        if not v.isdigit() or len(v) != 11:
            raise ValueError("El RUC debe tener exactamente 11 dígitos")
        return v

    @field_validator("razon_social")
    @classmethod
    def razon_social_valida(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2:
            raise ValueError("La razón social debe tener al menos 2 caracteres")
        return v

    def model_post_init(self, __context) -> None:
        if self.tipo_acopiador == TipoAcopiador.TERCERO and not self.acopiador_id:
            raise ValueError("Debe indicar el acopiador_id cuando tipo_acopiador es 'tercero'")


# =============================================================================
# EDICIÓN DE TERCERO
# =============================================================================


class TerceroEditar(BaseModel):
    """
    Payload para editar datos básicos y parámetros.
    Refleja la pantalla 'Editar datos de terceros'.
    """

    razon_social: str | None = None
    referencia: str | None = None
    telefono: str | None = None
    email: EmailStr | None = None
    parametros: ParametrosSchema | None = None


class CambiarAcopiadorPayload(BaseModel):
    """Payload para cambiar el acopiador de un proveedor (sin sesiones)."""

    acopiador_id: int
