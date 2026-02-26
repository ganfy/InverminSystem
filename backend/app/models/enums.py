"""
Enumeraciones del sistema — fuente única de verdad para estados y tipos.

Reglas:
- Todo estado o tipo que aparezca en la BD como string tiene su enum aquí.
- Los services y schemas SIEMPRE usan estos enums, nunca strings literales.
- Los check constraints de BD se generan desde estos enums (ver migraciones).
- La tabla `codigos` usa estos valores como referencia para labels y colores en frontend.

Agregar un estado nuevo:
    1. Agregarlo aquí.
    2. Generar migración que regenere el check constraint.
    3. Actualizar lógica de flujo en el service correspondiente.

Quitar un estado:
    1. Migrar registros existentes en la BD.
    2. Eliminarlo aquí.
    3. Regenerar check constraint.
"""

from enum import Enum

# =============================================================================
# ESTADOS DE FLUJO OPERATIVO
# =============================================================================


class EstadoSesion(str, Enum):
    """Estados de una sesión de descarga en balanza."""

    EN_PROCESO = "EN_PROCESO"
    PAUSADO = "PAUSADO"
    COMPLETO = "COMPLETO"


class EstadoLote(str, Enum):
    """
    Ciclo de vida de un lote.
    Flujo normal: RECEPCIONADO → LIQUIDADO → FACTURADO → PAGADO → ASIGNADO_RUMA
    """

    RECEPCIONADO = "RECEPCIONADO"
    ASIGNADO_RUMA = "ASIGNADO_RUMA"
    LIQUIDADO = "LIQUIDADO"
    FACTURADO = "FACTURADO"
    PAGADO = "PAGADO"


class EstadoLiquidacion(str, Enum):
    """
    Ciclo de vida de una liquidación.
    Flujo: BORRADOR → GENERADA → FACTURADA → PAGADA
    Una liquidación PAGADA no puede modificarse por ningún rol.
    """

    BORRADOR = "BORRADOR"
    GENERADA = "GENERADA"
    FACTURADA = "FACTURADA"
    PAGADA = "PAGADA"


class EstadoCampana(str, Enum):
    """Solo puede haber una campaña ACTIVA a la vez (validado por trigger)."""

    ACTIVA = "ACTIVA"
    CERRADA = "CERRADA"


class EstadoRuma(str, Enum):
    ABIERTA = "ABIERTA"
    CERRADA = "CERRADA"


class EstadoAnalisis(str, Enum):
    """
    Estado de un análisis de ley o recuperación.
    DESCARTADO: marcado manualmente por Comercial/Gerencia/Admin con justificación.
    """

    PENDIENTE = "PENDIENTE"
    ACTIVO = "ACTIVO"
    DESCARTADO = "DESCARTADO"


class EstadoComprobante(str, Enum):
    EMITIDA = "EMITIDA"
    PARCIALMENTE_PAGADA = (
        "PARCIALMENTE_PAGADA"  # por si se hacen pagos parciales a una factura grande eventualmente
    )
    PAGADA = "PAGADA"
    ANULADA = "ANULADA"


# =============================================================================
# TIPOS DE ENTIDAD Y ROLES COMERCIALES
# =============================================================================


class TipoEntidad(str, Enum):
    """Tipo jurídico de una entidad comercial."""

    EMPRESA = "EMPRESA"
    PERSONA_NATURAL = "PERSONA_NATURAL"
    EMPLEADO = "EMPLEADO"


class RolEntidad(str, Enum):
    """
    Roles comerciales que puede tener una entidad.
    Separados de los roles de sistema (Usuario.rol).
    Una entidad puede tener ambos simultáneamente.
    """

    PROVEEDOR = "PROVEEDOR"
    ACOPIADOR = "ACOPIADOR"


# =============================================================================
# TIPOS DE MATERIAL Y ANÁLISIS
# =============================================================================


class TipoMaterial(str, Enum):
    """Tipo de mineral recibido en balanza."""

    MINERAL = "MINERAL"
    LLAMPO = "LLAMPO"
    MLLAMPO = "MLLAMPO"


class TipoAnalisis(str, Enum):
    """
    Origen del análisis de ley.
    - planta:     laboratorio interno Paititi
    - externo:    laboratorio externo (usa CIP, nunca ve IP)
    - minero:     ley presentada por el proveedor
    - dirimencia: análisis neutral para resolver conflictos
    """

    PLANTA = "planta"
    EXTERNO = "externo"
    MINERO = "minero"
    DIRIMENCIA = "dirimencia"


class OrigenDatos(str, Enum):
    """Cómo se ingresaron los datos de un análisis."""

    MANUAL = "manual"  # Ingreso directo por laboratorista
    CERTIFICADO = "certificado"  # Extraído de PDF por OCR


class OrigenMuestra(str, Enum):
    """
    Cómo se calculó la ley comercial final en liquidaciones_lotes.
    Trazabilidad de la decisión de Gerencia/Comercial.
    """

    CABEZA = "cabeza"  # Ley del análisis de cabeza (si existe)
    COLA = "cola"  # Ley del análisis de cola (si existe)
    LIQUIDO = "liquido"  # Ley del análisis de líquido (si existe)


# =============================================================================
# TIPOS DE COMPROBANTE Y PAGO
# =============================================================================


class TipoComprobante(str, Enum):
    FACTURA = "FACTURA"
    NOTA_DEBITO = "NOTA_DEBITO"
    NOTA_CREDITO = "NOTA_CREDITO"


class MetodoPago(str, Enum):
    TRANSFERENCIA = "TRANSFERENCIA"
    EFECTIVO = "EFECTIVO"
    CHEQUE = "CHEQUE"


# =============================================================================
# ROLES DE SISTEMA (usuarios)
# =============================================================================


class RolSistema(str, Enum):
    """
    Roles de usuario del sistema — controlan acceso RBAC.
    Separados de RolEntidad (roles comerciales de proveedores/acopiadores).
    """

    ADMIN = "Admin"
    GERENCIA = "Gerencia"
    COMERCIAL = "Comercial"
    LABORATORISTA = "Laboratorista"
    OPERADOR_BALANZA = "OperadorBalanza"
    TECNICO_MUESTREO = "TecnicoMuestreo"


# =============================================================================
# OPERACIONES RBAC
# =============================================================================


class Operacion(str, Enum):
    """Operaciones disponibles en la matriz de permisos."""

    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    VIEW = "VIEW"


# =============================================================================
# HELPER — para generar check constraints desde enums
# =============================================================================


def valores_enum(enum_class) -> str:
    """
    Genera el string SQL para un check constraint IN desde un enum.

    Uso en migraciones:
        op.create_check_constraint(
            "ck_lotes_estado_valido", "lotes",
            f"estado IN ({valores_enum(EstadoLote)})"
        )
    """
    valores = ", ".join(f"'{e.value}'" for e in enum_class)
    return valores
