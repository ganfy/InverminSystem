# =============================================================================
# models.py - INVERMIN PAITITI S.A.C. - Sistema ERP Comercial Minero
# =============================================================================
# Compatible con: PostgreSQL y SQL Server (via SQLAlchemy ORM)
# Para cambiar de motor, solo se modifica DATABASE_URL en database.py.
#
# COLUMNAS CALCULADAS:
#   - Las expresiones simples (suma, resta, división) usan Computed() de
#     SQLAlchemy, que traduce al dialecto correcto en cada motor.
#   - fecha_salida (PruebaMetalurgica) usa @hybrid_property en lugar de
#     Computed porque INTERVAL es sintaxis exclusiva de PostgreSQL.
#
# MÓDULO DE FACTURACIÓN (Comprobante, Pago):
#   - Gestionado por sistema externo de contabilidad.
#   - Se integra vía API.
#   - En el MVP, Lote.estado se actualiza MANUALMENTE desde el backoffice.
#     La integración automática con la API externa es post-MVP.
#
# TO DO: PUNTO DE INTEGRACIÓN FUTURA buscar "# API_CONTABILIDAD")
# TO DO: agregar enums para estados, tipos, etc. (SQLAlchemy Enum con contenido de tabla de códigos)
# TO DO: Computed a capa de servicio para cálculos agnósticos de motor
# =============================================================================

from datetime import timedelta

from app.models.base import AuditMixin, Base, SoftDeleteMixin
from app.models.enums import (
    EstadoCampana,
    EstadoLiquidacion,
    EstadoLote,
    EstadoRuma,
    EstadoSesion,
    OrigenDatos,
)
from sqlalchemy import (
    Boolean,
    Column,
    Computed,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

# =============================================================================
# RBAC: ROLES, MÓDULOS, OPERACIONES, PERMISOS
# =============================================================================


class Rol(Base):
    """
    Roles del sistema. Dos usos:
    1. Roles de acceso: Admin, Gerencia, Comercial, Laboratorista,
       OperadorBalanza, TecnicoMuestreo.
    2. Roles comerciales de entidades: PROVEEDOR, ACOPIADOR.
    """

    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    codigo = Column(String(20), unique=True, nullable=False)
    nombre = Column(String(50), nullable=False)

    entidades_roles = relationship("EntidadRol", back_populates="rol")
    permisos = relationship("Permiso", back_populates="rol")


class Modulo(Base):
    """Módulos del sistema: BALANZA, MUESTREO, LABORATORIO, etc."""

    __tablename__ = "modulos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    codigo = Column(String(30), unique=True, nullable=False)
    nombre = Column(String(60), nullable=False)

    permisos = relationship("Permiso", back_populates="modulo")


class Operacion(Base):
    """Operaciones: CREATE, UPDATE, DELETE, VIEW."""

    __tablename__ = "operaciones"

    id = Column(Integer, primary_key=True, autoincrement=True)
    codigo = Column(String(20), unique=True, nullable=False)
    nombre = Column(String(50), nullable=False)

    permisos = relationship("Permiso", back_populates="operacion")


class Permiso(AuditMixin, Base):
    """
    Matriz de permisos RBAC: rol x módulo x operación → permitido (bool).
    AuditMixin: creado_en, creado_por, modificado_en, modificado_por.
    """

    __tablename__ = "permisos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    rol_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    modulo_id = Column(Integer, ForeignKey("modulos.id"), nullable=False)
    operacion_id = Column(Integer, ForeignKey("operaciones.id"), nullable=False)
    permitido = Column(Boolean, nullable=False, default=False)

    rol = relationship("Rol", back_populates="permisos")
    modulo = relationship("Modulo", back_populates="permisos")
    operacion = relationship("Operacion", back_populates="permisos")

    __table_args__ = (
        UniqueConstraint(
            "rol_id",
            "modulo_id",
            "operacion_id",
            name="uq_permiso_rol_modulo_op",
        ),
    )


# =============================================================================
# USUARIOS
# =============================================================================


class Usuario(AuditMixin, Base):
    """
    Usuarios del sistema con autenticación JWT + bcrypt.
    Roles válidos (RF-SYS-001): Admin, Gerencia, Comercial,
    Laboratorista, OperadorBalanza, TecnicoMuestreo.
    AuditMixin: creado_en, creado_por, modificado_en, modificado_por.
    """

    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    nombre_completo = Column(String(200), nullable=False)
    rol_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    email = Column(String(100))
    activo = Column(Boolean, default=True)

    lotes_habilitados = relationship(
        "Lote",
        foreign_keys="Lote.habilitado_por",
        back_populates="usuario_habilitacion",
    )
    campanas_creadas = relationship(
        "Campana",
        foreign_keys="Campana.gerencia_id",
        back_populates="creador",
    )
    liquidaciones_cerradas = relationship(
        "Liquidacion",
        foreign_keys="Liquidacion.cerrado_por",
        back_populates="cerrador",
    )
    rol = relationship("Rol")


# =============================================================================
# ENTIDADES (PROVEEDORES / ACOPIADORES)
# =============================================================================


class Entidad(AuditMixin, Base):
    """
    Entidad comercial: EMPRESA, EMPLEADO o PERSONA_NATURAL.
    Una misma entidad puede tener múltiples roles simultáneos.
    AuditMixin: creado_en, creado_por, modificado_en, modificado_por.
    """

    __tablename__ = "entidades"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ruc = Column(String(11), unique=True, nullable=True)
    razon_social = Column(String(200), nullable=False)
    referencia = Column(Text)
    tipo = Column(String(30), nullable=False)  # EMPRESA | EMPLEADO | PERSONA_NATURAL
    direccion = Column(Text)
    telefono = Column(String(20))
    email = Column(String(100))
    activo = Column(Boolean, default=True)

    entidades_roles = relationship("EntidadRol", back_populates="entidad")
    # parametros = relationship(
    #     "ParametrosComerciales",
    #     back_populates="acopiador",
    #     uselist=False,
    # ) # relación a través de ProveedorAcopiador por flexibilidad


class EntidadRol(AuditMixin, Base):
    """
    Asignación N:M entre Entidad y Rol comercial (PROVEEDOR, ACOPIADOR).
    AuditMixin: creado_en, creado_por, modificado_en, modificado_por.
    """

    __tablename__ = "entidades_roles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    entidad_id = Column(Integer, ForeignKey("entidades.id"), nullable=False)
    rol_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    activo = Column(Boolean, default=True)

    entidad = relationship("Entidad", back_populates="entidades_roles")
    rol = relationship("Rol", back_populates="entidades_roles")

    __table_args__ = (UniqueConstraint("entidad_id", "rol_id", name="uq_entidad_rol"),)


class ProveedorAcopiador(Base):
    """
    Relación comercial específica entre PROVEEDOR y ACOPIADOR.
    Una entidad puede ser su propio acopiador.
    Su id (provacop_id) es FK en SesionDescarga, Liquidacion.
    Sin AuditMixin: tabla asociativa sin historial de cambios propio.
    """

    __tablename__ = "proveedor_acopiador"

    id = Column(Integer, primary_key=True, autoincrement=True)
    proveedor_id = Column(Integer, ForeignKey("entidades.id"))
    acopiador_id = Column(Integer, ForeignKey("entidades.id"))

    proveedor = relationship("Entidad", foreign_keys=[proveedor_id])
    acopiador = relationship("Entidad", foreign_keys=[acopiador_id])
    sesiones = relationship("SesionDescarga", back_populates="provacop")
    liquidaciones = relationship("Liquidacion", back_populates="provacop")

    __table_args__ = (
        UniqueConstraint("proveedor_id", "acopiador_id", name="uq_proveedor_acopiador"),
    )
    parametros = relationship("ParametrosComerciales", back_populates="provacop", uselist=False)


class ParametrosComerciales(AuditMixin, Base):
    """
    Parámetros comerciales por acopiador (RF-ENT-003).
    Solo Admin y Gerencia pueden crear/modificar. Comercial: solo lectura.
    AuditMixin: creado_en, creado_por, modificado_en, modificado_por.
    """

    __tablename__ = "parametros_comerciales"

    id = Column(Integer, primary_key=True, autoincrement=True)
    provacop_id = Column(Integer, ForeignKey("proveedor_acopiador.id"), nullable=False, unique=True)
    umbral_recup_bajo = Column(Numeric(5, 2))
    umbral_recup_medio = Column(Numeric(5, 2))
    riesgo_comercial = Column(Numeric(5, 2))
    lim_ley_comercial = Column(Numeric(8, 3))
    dscto_ley_comercial = Column(Numeric(8, 3))
    porcentaje_ley_comercial = Column(Numeric(8, 3))
    lim_ley_inferior = Column(Numeric(8, 3))
    lim_ley_superior = Column(Numeric(8, 3))
    gasto_acopio = Column(Numeric(10, 2))  # USD
    gasto_consumo = Column(Numeric(10, 2))  # USD
    maquila = Column(Numeric(5, 2))  # %
    comision = Column(Numeric(5, 2))  # %

    provacop = relationship("ProveedorAcopiador", back_populates="parametros")


# =============================================================================
# BALANZA
# =============================================================================


class SesionDescarga(AuditMixin, Base):
    """
    Sesión de descarga: agrupa los lotes de un mismo vehículo/guías.
    Solo OperadorBalanza y Admin pueden crear (RF-BAL-001).
    Una vez COMPLETO, no se puede modificar (RF-SYS-001 regla 8).
    AuditMixin: creado_en, creado_por, modificado_en, modificado_por.
    """

    __tablename__ = "sesiones_descarga"

    id = Column(Integer, primary_key=True, autoincrement=True)
    offline_id = Column(String(36), unique=True)  # UUID para sincronización offline
    provacop_id = Column(Integer, ForeignKey("proveedor_acopiador.id"), nullable=False)
    placa = Column(String(10), nullable=False)
    carreta = Column(String(10))
    conductor = Column(String(200))
    transportista = Column(String(200))
    razon_social = Column(String(200))
    guia_remision = Column(String(50))
    guia_transporte = Column(String(50))
    estado = Column(String(20), nullable=False, default=EstadoSesion.EN_PROCESO)

    provacop = relationship("ProveedorAcopiador", back_populates="sesiones")
    lotes = relationship("Lote", back_populates="sesion")
    documentos = relationship("SesionDocumento", back_populates="sesion")


class SesionDocumento(AuditMixin, Base):
    """
    Documentos adjuntos a una sesión de descarga.
    Almacenados en disco local del servidor (/storage/sesiones/...).
    Tipos: GUIA_REMISION, GUIA_TRANSPORTE, LICENCIA_CONDUCIR, OTRO.
    Cualquier rol con acceso a Balanza puede subir (Admin, OperadorBalanza).
    Upload implementado en módulo Balanza (RF-BAL-001).
    """

    __tablename__ = "sesion_documentos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sesion_id = Column(Integer, ForeignKey("sesiones_descarga.id"), nullable=False)
    tipo_documento = Column(
        String(30), nullable=False
    )  # Valores: GUIA_REMISION, GUIA_TRANSPORTE, LICENCIA_CONDUCIR, OTRO
    nombre_original = Column(
        String(255), nullable=False
    )  # Nombre del archivo tal como lo subió el usuario
    ruta_archivo = Column(
        String(500), nullable=False
    )  # Ruta relativa en servidor: /storage/sesiones/{año}/{mes}/{sesion_id}/{archivo}

    sesion = relationship("SesionDescarga", back_populates="documentos")


class Lote(AuditMixin, SoftDeleteMixin, Base):
    """
    Lote individual de mineral. Núcleo del sistema.
    IP (Ingreso Planta) se auto-genera secuencialmente: IP-0001, IP-0002...

    ESTADOS Y TRANSICIONES:
        RECEPCIONADO → LIQUIDADO → FACTURADO → PAGADO → ASIGNADO_RUMA

    MVP: Los estados FACTURADO y PAGADO se actualizan MANUALMENTE
         por Admin/Comercial desde el backoffice.
    POST-MVP: Se actualizarán automáticamente vía webhook/polling
              de la API del sistema de contabilidad externo.
              (Buscar "# API_CONTABILIDAD" en este archivo)

    HABILITADO PARA RUMA: Un lote puede entrar a ruma si:
        - Automático: estado IN (FACTURADO, PAGADO), o
                      volado=True AND fecha_recepcion + 30 días <= hoy
        - Manual: Admin/Comercial/Gerencia lo habilitan explícitamente.

    SoftDeleteMixin: eliminado, eliminado_por, eliminado_en.
    AuditMixin: creado_en, creado_por, modificado_en, modificado_por.
    REGLA: estado=PAGADO bloquea la eliminación (RF-BAL-004).
    """

    __tablename__ = "lotes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sesion_id = Column(Integer, ForeignKey("sesiones_descarga.id"), nullable=False)
    ip = Column(String(20), unique=True, nullable=False)
    numero_lote = Column(Integer, nullable=False)
    tipo_material = Column(String(20))  # Mineral | Llampo | M.Llampo
    ruma_id = Column(Integer, ForeignKey("rumas.id"))
    estado = Column(String(30), nullable=False, default=EstadoLote.RECEPCIONADO)
    # Flags de negocio
    volado = Column(Boolean, default=False)  # ley muy baja
    dirimencia = Column(Boolean, default=False)  # tuvo análisis de dirimencia
    habilitado_ruma = Column(Boolean, default=False)
    fecha_habilitacion = Column(DateTime)
    habilitado_por = Column(Integer, ForeignKey("usuarios.id"))
    # Auditoría de cambio de estado
    estado_modificado_por = Column(Integer, ForeignKey("usuarios.id"))
    fecha_modificacion_estado = Column(DateTime)

    sesion = relationship("SesionDescarga", back_populates="lotes")
    ruma = relationship("Ruma", back_populates="lotes")
    usuario_habilitacion = relationship(
        "Usuario",
        foreign_keys=[habilitado_por],
        back_populates="lotes_habilitados",
    )
    pesajes = relationship("Pesaje", back_populates="lote")
    muestreos = relationship("Muestreo", back_populates="lote")
    mapeo_cip = relationship("MapeoCIP", back_populates="lote", uselist=False)
    analisis_ley = relationship(
        "AnalisisLey",
        foreign_keys="AnalisisLey.lote_id",
        back_populates="lote",
    )
    analisis_recuperacion = relationship(
        "AnalisisRecuperacion",
        foreign_keys="AnalisisRecuperacion.lote_id",
        back_populates="lote",
    )
    liquidaciones_lotes = relationship(
        "LiquidacionLote",
        foreign_keys="LiquidacionLote.lote_id",
        back_populates="lote",
    )
    modificador_estado = relationship("Usuario", foreign_keys=[estado_modificado_por])

    __table_args__ = (UniqueConstraint("sesion_id", "numero_lote", name="uq_lote_sesion_numero"),)


class Pesaje(Base, AuditMixin):
    """
    Registro de pesaje por lote (peso inicial → peso final).
    """

    __tablename__ = "pesajes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    lote_id = Column("lote_id", Integer, ForeignKey("lotes.id"), nullable=False)
    sacos = Column(Integer)
    peso_inicial = Column(Numeric(10, 2), nullable=False)  # TM
    peso_final = Column(Numeric(10, 2), nullable=False)  # TM
    peso_neto = Column(
        Numeric(10, 2),
        Computed("peso_inicial - peso_final", persisted=True),
        nullable=False,
    )  # TO DO: calcular en servicio y guardar aquí, porque no es solo peso_final - peso_inicial (puede haber ajustes manuales por tara, humedad, etc.)
    numero_ticket = Column(String(50), unique=True)
    fecha_inicio = Column(DateTime)
    fecha_fin = Column(DateTime, server_default=func.now())
    es_manual = Column(Boolean, default=False, nullable=False)
    justificacion_manual = Column(String(255), nullable=True)
    granel = Column(Boolean, default=False)

    lote = relationship("Lote", back_populates="pesajes")


class LoteEliminado(Base):
    """
    Tabla de auditoría de lotes eliminados (RF-BAL-004).
    Snapshot inmutable generado en el momento de la eliminación.
    La fuente de verdad del lote sigue siendo la tabla lotes (soft delete),
    pero esta tabla garantiza trazabilidad aunque cambien los datos maestros.

    datos_originales almacena JSON como Text para compatibilidad con
    PostgreSQL y SQL Server. En el service se serializa/deserializa con json.dumps/loads.

    Ejemplo de datos_originales:
    {
        "ip": "IP-0042",
        "proveedor_ruc": "20123456789",
        "proveedor_razon_social": "Minera XYZ S.A.C.",
        "acopiador_ruc": "10987654321",
        "acopiador_razon_social": "Juan Pérez",
        "tipo_material": "Mineral",
        "peso_neto_tm": 12.45,
        "estado_al_eliminar": "RECEPCIONADO",
        "sesion_id": 17
    }
    """

    __tablename__ = "lotes_eliminados"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ip = Column(String(20), nullable=False)  # copia, no FK
    eliminado_por = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    fecha_eliminacion = Column(DateTime, server_default=func.now())
    motivo = Column(Text)
    datos_originales = Column(Text, nullable=False)  # JSON serializado

    usuario = relationship("Usuario", foreign_keys=[eliminado_por])

    # TO DO: hacer snapshot en service al eliminar lote, serializando datos relevantes a JSON y guardando aquí.


# =============================================================================
# MUESTREO
# =============================================================================


class Muestreo(AuditMixin, Base):
    """
    Hasta 3 intentos de muestreo por lote (RF-MUE-005).
    porcentaje_humedad: columna calculada por la BD.
    tms_calculado: se calcula en Python (service layer) porque depende
                   del peso total del lote (TMH), no solo de este registro.
    Alertas de negocio (se validan en el service, no en la BD):
        - % humedad fuera de [0, 50]: ERROR, repetir muestreo.
    AuditMixin: creado_en, creado_por, modificado_en, modificado_por.
    """

    __tablename__ = "muestreos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    lote_id = Column(Integer, ForeignKey("lotes.id"), nullable=False)
    intento = Column(Integer, nullable=False)
    peso_humedo = Column(Numeric(10, 3), nullable=False)
    peso_seco = Column(Numeric(10, 3), nullable=False)
    porcentaje_humedad = Column(
        Numeric(5, 2),
        Computed(
            """
            CASE
                WHEN peso_humedo = 0 THEN 0
                ELSE ((peso_humedo - peso_seco) / peso_humedo) * 100
            END
            """,
            persisted=True,
        ),
    )
    tms_calculado = Column(Numeric(10, 2))  # calculado en service y guardado aquí
    observaciones = Column(Text)

    lote = relationship("Lote", back_populates="muestreos")

    __table_args__ = (UniqueConstraint("lote_id", "intento", name="uq_muestreo_lote_intento"),)


# =============================================================================
# CIP (CONFIDENCIALIDAD)
# =============================================================================


class MapeoCIP(Base):
    """
    Mapeo CONFIDENCIAL IP ↔ CIP (RF-LAB-001).
    Los laboratorios externos solo reciben el CIP, nunca el IP ni el proveedor.
    Solo Admin, Gerencia y Comercial pueden ver esta tabla.
    Formato: CIP-#######-A# (ej: CIP-163546K-A2)
    Sin AuditMixin: inmutable una vez creado.
    """

    __tablename__ = "mapeo_cip"

    id = Column(Integer, primary_key=True, autoincrement=True)
    lote_id = Column(Integer, ForeignKey("lotes.id"), nullable=False)
    ruma_id = Column(Integer, ForeignKey("rumas.id"))
    codigo_cip = Column(String(20), unique=True, nullable=False)
    laboratorio = Column(String(50))
    fecha_envio = Column(Date)
    tipo_muestra = Column(String(50))

    lote = relationship("Lote", back_populates="mapeo_cip")
    ruma = relationship("Ruma")
    analisis_ley = relationship(
        "AnalisisLey",
        foreign_keys="AnalisisLey.cip",
        back_populates="mapeo_cip",
    )
    analisis_recuperacion = relationship(
        "AnalisisRecuperacion",
        foreign_keys="AnalisisRecuperacion.cip",
        back_populates="mapeo_cip",
    )
    prueba_metalurgica = relationship(
        "PruebaMetalurgica",
        back_populates="mapeo_cip",
        uselist=False,
    )


# =============================================================================
# LABORATORIO
# =============================================================================


class AnalisisLey(AuditMixin, Base):
    """
    Análisis de ley: Fire Assay, triple sampling Fino1-Grueso-Fino2.
    Tipos: planta | externo | minero | dirimencia.
    ley_final: columna calculada (ley_fino + ley_grueso).
    REGLA: Al registrar tipo='dirimencia', marcar vigente=False en todos
           los demás análisis del mismo IP (implementar en service o trigger).
    AuditMixin: creado_en, creado_por, modificado_en, modificado_por.
    """

    __tablename__ = "analisis_ley"

    id = Column(Integer, primary_key=True, autoincrement=True)
    lote_id = Column(Integer, ForeignKey("lotes.id"), nullable=False)
    cip = Column(String(20), ForeignKey("mapeo_cip.codigo_cip"))
    laboratorio = Column(String(50), nullable=False)
    tipo_analisis = Column(String(20), nullable=False)  # sin default — siempre explícito
    material = Column(String(10), default="Au")
    ley_fino = Column(Numeric(10, 4))
    ley_grueso = Column(Numeric(10, 4))
    ley_final = Column(Numeric(10, 4))
    # TO DO: calcular en service y guardar aquí ley_fino + ley_grueso
    ley_gr_tm = Column(Numeric(10, 3))  # Oz/TC × 34.2857, calculado en service
    origen_datos = Column(String(20), default=OrigenDatos.MANUAL)
    fecha_analisis = Column(Date)
    certificado_url = Column(Text)
    vigente = Column(Boolean, default=True)
    descartado_por = Column(Integer, ForeignKey("usuarios.id"))
    fecha_descarte = Column(DateTime)
    justificacion_descarte = Column(Text)

    lote = relationship("Lote", back_populates="analisis_ley")
    mapeo_cip = relationship("MapeoCIP", foreign_keys=[cip], back_populates="analisis_ley")
    detalles = relationship(
        "AnalisisDetalle",
        foreign_keys="AnalisisDetalle.analisis_id",
        back_populates="analisis_ley",
    )
    descartador = relationship("Usuario", foreign_keys=[descartado_por])


class AnalisisDetalle(Base):
    """
    Detalle de cada muestra: Fino1, Grueso, Fino2 (triple sampling).
    'origen' es código de tabla Codigo (grupo: TIPO_MUESTRA_ANALISIS).
    Sin AuditMixin: inmutable una vez registrado.
    """

    __tablename__ = "analisis_detalle"

    id = Column(Integer, primary_key=True, autoincrement=True)
    analisis_id = Column(Integer, ForeignKey("analisis_ley.id"))
    recuperacion_id = Column(Integer, ForeignKey("analisis_recuperacion.id"))
    origen = Column(String(20), nullable=False)
    peso = Column(Numeric(10, 4))
    ley = Column(Numeric(10, 4))
    numero_ensayo = Column(Integer, default=1)

    analisis_ley = relationship(
        "AnalisisLey",
        foreign_keys=[analisis_id],
        back_populates="detalles",
    )
    analisis_recuperacion = relationship(
        "AnalisisRecuperacion",
        foreign_keys=[recuperacion_id],
    )


class AnalisisRecuperacion(AuditMixin, Base):
    """
    Análisis de recuperación: leyes de cabeza, cola y líquido.
    recuperacion: columna calculada.
    Validación física (en service): ley_cabeza > ley_cola.
    AuditMixin: creado_en, creado_por, modificado_en, modificado_por.
    """

    __tablename__ = "analisis_recuperacion"

    id = Column(Integer, primary_key=True, autoincrement=True)
    lote_id = Column(Integer, ForeignKey("lotes.id"), nullable=False)
    cip = Column(String(20), ForeignKey("mapeo_cip.codigo_cip"))
    laboratorio = Column(String(50), nullable=False)
    ley_cabeza = Column(Numeric(10, 4))
    ley_cola = Column(Numeric(10, 4))
    ley_liquido = Column(Numeric(10, 4))
    recuperacion = Column(
        Numeric(5, 2),
        Computed("((ley_cabeza - ley_cola) / ley_cabeza) * 100", persisted=True),
    )
    origen_datos = Column(String(20), default=OrigenDatos.MANUAL)
    fecha_analisis = Column(Date)
    certificado_url = Column(Text)
    vigente = Column(Boolean, default=True)
    descartado_por = Column(Integer, ForeignKey("usuarios.id"))
    fecha_descarte = Column(DateTime)
    justificacion_descarte = Column(Text)

    lote = relationship("Lote", back_populates="analisis_recuperacion")
    mapeo_cip = relationship(
        "MapeoCIP",
        foreign_keys=[cip],
        back_populates="analisis_recuperacion",
    )
    descartador = relationship("Usuario", foreign_keys=[descartado_por])


# =============================================================================
# PRUEBAS METALÚRGICAS
# =============================================================================


class PruebaMetalurgica(AuditMixin, Base):
    """
    Preparación de muestras para análisis metalúrgico (RF-PM-001).

    S
    Alerta de negocio (en service): malla_porcentaje fuera de [88, 94] → WARNING.
    AuditMixin: creado_en, creado_por, modificado_en, modificado_por.
    """

    __tablename__ = "pruebas_metalurgicas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    cip = Column(String(20), ForeignKey("mapeo_cip.codigo_cip"))
    fecha_ingreso = Column(DateTime, nullable=False)
    malla_porcentaje = Column(Numeric(5, 2))
    porcentaje_nacn = Column(Numeric(5, 2))
    ph_inicial = Column(Numeric(4, 2))
    ph_final = Column(Numeric(4, 2))
    adicion_nacn = Column(Numeric(10, 4))  # gramos
    adicion_naoh = Column(Numeric(10, 4))  # gramos
    gasto_agno3 = Column(Numeric(10, 4))  # ml

    @hybrid_property
    def fecha_salida(self):
        """fecha_ingreso + 48 horas."""
        if self.fecha_ingreso:
            return self.fecha_ingreso + timedelta(hours=48)
        return None

    mapeo_cip = relationship("MapeoCIP", back_populates="prueba_metalurgica")


# =============================================================================
# CAMPAÑAS
# =============================================================================


class Campana(AuditMixin, Base):
    """
    Campaña de producción con meta de oro fino (RF-CAMP-001).
    REGLA: Solo 1 campaña ACTIVA a la vez.
    Al cerrar: reiniciar contador de rumas y crear nueva campaña automáticamente.
    Solo Admin y Gerencia pueden cerrar (RF-CAMP-002).
    AuditMixin: creado_en, creado_por, modificado_en, modificado_por.
    """

    __tablename__ = "campanas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    codigo = Column(String(50), unique=True, nullable=False)  # CAMP2026-01
    meta_oro_fino = Column(Numeric(10, 2), default=5000.00)  # gramos
    fecha_inicio = Column(Date, nullable=False)
    fecha_cierre = Column(Date)
    estado = Column(String(20), default=EstadoCampana.ACTIVA)  # ACTIVA | CERRADA
    oro_fino_acumulado = Column(Numeric(10, 2), default=0)
    total_lotes = Column(Integer, default=0)
    total_toneladas = Column(Numeric(10, 2), default=0)
    total_rumas = Column(Integer, default=0)
    gerencia_id = Column(Integer, ForeignKey("usuarios.id"))

    creador = relationship(
        "Usuario",
        foreign_keys="[Campana.gerencia_id]",
        back_populates="campanas_creadas",
    )
    rumas_campana = relationship("RumaCampana", back_populates="campana")


# =============================================================================
# RUMAS
# =============================================================================


class Ruma(AuditMixin, Base):
    """
    Agrupación de lotes para procesamiento conjunto.
    Código: CAMP2026-01-001. Se reinicia a 001 al cerrar campaña.

    ESTADO:
        ABIERTA  → lotes pueden modificarse
        CERRADA  → bloqueada para edición
    Regla de cierre: por definir. Candidato natural: al cerrar la campaña
    asociada. Por ahora se cierra manualmente.

    AuditMixin: creado_en, creado_por, modificado_en, modificado_por.
    Cuando se cierre la ruma, modificado_por registra quién lo hizo.
    """

    __tablename__ = "rumas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    numero_ruma = Column(Integer, nullable=False)
    codigo = Column(String(20), unique=True, nullable=False)  # CAMP2026-01-001
    codigo_ant = Column(String(20), unique=True)  # vínculo con campaña previa
    fecha_creacion = Column(Date, server_default=func.current_date())
    estado = Column(String(20), default=EstadoRuma.ABIERTA)  # ABIERTA | CERRADA

    lotes = relationship("Lote", back_populates="ruma")
    rumas_campana = relationship("RumaCampana", back_populates="ruma")


class RumaCampana(Base):
    """
    Tabla asociativa Ruma ↔ Campaña.
    Registra el tonelaje de la ruma perteneciente a cada campaña.
    Sin AuditMixin: tabla asociativa.
    """

    __tablename__ = "rumas_campanas"

    id_ruma = Column(Integer, ForeignKey("rumas.id"), primary_key=True)
    id_campana = Column(Integer, ForeignKey("campanas.id"), primary_key=True)
    tonelaje = Column(Numeric(10, 2), nullable=False)

    ruma = relationship("Ruma", back_populates="rumas_campana")
    campana = relationship("Campana", back_populates="rumas_campana")


# =============================================================================
# LIQUIDACIONES
# =============================================================================


class Liquidacion(AuditMixin, Base):
    """
    Liquidación generada para un proveedor-acopiador.
    Estados: GENERADA → FACTURADO → PAGADO.

    MVP: Los estados FACTURADO y PAGADO se actualizan MANUALMENTE
         por Admin o Comercial desde la vista de detalle del lote.
    POST-MVP: Se actualizarán automáticamente desde la API de contabilidad.
              # API_CONTABILIDAD: agregar campo ref_comprobante_externo = Column(String)
              # y un endpoint webhook POST /liquidaciones/{id}/sync-estado

    REGLA: Una vez PAGADA no puede modificarse (RF-SYS-001 regla 5).
    AuditMixin: creado_en, creado_por, modificado_en, modificado_por.
    """

    __tablename__ = "liquidaciones"

    id = Column(Integer, primary_key=True, autoincrement=True)
    numero_liquidacion = Column(String(50), unique=True)
    provacop_id = Column(Integer, ForeignKey("proveedor_acopiador.id"), nullable=False)
    precio_oro_usd = Column(Numeric(10, 2))  # scraping o entrada manual (RF-LIQ-005)
    valor_total_usd = Column(Numeric(12, 2))  # calculado en service
    estado = Column(String(20), default=EstadoLiquidacion.GENERADA)
    cerrado_por = Column(Integer, ForeignKey("usuarios.id"))
    fecha_cierre = Column(DateTime)
    pdf_url = Column(Text)

    # API_CONTABILIDAD (POST-MVP): descomentar cuando se integre la API externa
    # ref_comprobante_externo = Column(String(100))   # ID devuelto por la API
    # estado_comprobante_cache = Column(String(30))   # cache del estado externo

    provacop = relationship("ProveedorAcopiador", back_populates="liquidaciones")
    cerrador = relationship(
        "Usuario",
        foreign_keys=[cerrado_por],
        back_populates="liquidaciones_cerradas",
    )
    liquidacion_lotes = relationship("LiquidacionLote", back_populates="liquidacion")


class LiquidacionLote(AuditMixin, Base):
    """
    Snapshot N:M de valores comerciales al momento de liquidar.
    Inmutable por diseño una vez creado.
    """

    __tablename__ = "liquidaciones_lotes"

    liquidacion_id = Column(Integer, ForeignKey("liquidaciones.id"), primary_key=True)
    lote_id = Column(Integer, ForeignKey("lotes.id"), primary_key=True)
    fecha_emision = Column(Date)
    fecha_recepcion = Column(Date)
    ley_comercial = Column(Numeric(10, 4))
    usa_dirimencia = Column(Boolean, default=False)
    oz_tc_planta = Column(Numeric(10, 4))
    oz_tc_comercial = Column(Numeric(10, 4))
    oz_tc_minero = Column(Numeric(10, 4))
    oz_tc_promedio = Column(Numeric(10, 4))
    porcentaje_rec_liquido = Column(Numeric(5, 2))
    porcentaje_rec_planta = Column(Numeric(5, 2))
    fino_recuperable = Column(Numeric(10, 4))
    gasto_acopio_liquidacion = Column(Numeric(10, 2))
    bono = Column(Numeric(10, 2))
    insumos_liquidacion = Column(Numeric(10, 2))

    liquidacion = relationship("Liquidacion", back_populates="liquidacion_lotes")
    lote = relationship("Lote", back_populates="liquidaciones_lotes")


# =============================================================================
# CONFIGURACIÓN Y CATÁLOGOS
# =============================================================================


class Codigo(Base):
    """
    Catálogo de codificaciones para combos del sistema.
    Grupos: TIPOS_MATERIAL, ESTADOS_LOTE, TIPOS_ANALISIS, TIPO_MUESTRA_ANALISIS...
    Sin AuditMixin: datos de catálogo.
    """

    __tablename__ = "codigos"

    grupo = Column(Integer, primary_key=True)
    item = Column(Integer, primary_key=True)
    nombre = Column(String(50), nullable=False)
    descripcion = Column(String(100))
    campo1 = Column(String(200))
    campo2 = Column(String(200))
    campo3 = Column(String(200))


class Configuracion(AuditMixin, Base):
    """
    Parámetros globales editables: vol_muestra_default, meta_oro_fino, etc.
    Solo Admin puede modificar.
    AuditMixin: creado_en, creado_por, modificado_en, modificado_por.
    """

    __tablename__ = "configuraciones"

    id = Column(Integer, primary_key=True, autoincrement=True)
    clave = Column(String(100), unique=True, nullable=False)
    valor = Column(String(200), nullable=False)
    descripcion = Column(String(200))


# =============================================================================
# API_CONTABILIDAD - COMPROBANTES Y PAGOS (POST-MVP)
# =============================================================================
# Estos modelos se activarán cuando se defina el contrato con la API del
# sistema de contabilidad externo.
#
# Para activar:
#   1. Descomentar las clases de abajo.
#   2. Descomentar ref_comprobante_externo en Liquidacion.
#   3. Crear la migración: alembic revision --autogenerate -m "add comprobantes externos"
#   4. Implementar ContabilidadClient en app/services/contabilidad_client.py
#
# En el MVP, Admin/Comercial cambian Liquidacion.estado manualmente a
# FACTURADO o PAGADO, lo que a su vez actualiza Lote.estado.
# =============================================================================

# class ComprobanteExterno(Base):
#     """
#     Referencia a comprobantes del sistema de contabilidad externo.
#     Este sistema NO gestiona lógica contable: solo guarda el ID externo
#     para trazabilidad y para consultar la API cuando se necesite.
#     estado_cache se sincroniza periódicamente (polling o webhook).
#     """
#     __tablename__ = "comprobantes_externos"
#
#     id                    = Column(Integer, primary_key=True, autoincrement=True)
#     id_externo            = Column(String(100), unique=True, nullable=False)
#     tipo                  = Column(String(20))       # FACTURA | NOTA_DEBITO | NOTA_CREDITO
#     numero                = Column(String(50))       # para mostrar al usuario
#     liquidacion_id        = Column(Integer, ForeignKey("liquidaciones.id"), nullable=False)
#     provacop_id           = Column(Integer, ForeignKey("proveedor_acopiador.id"))
#     estado_cache          = Column(String(30))       # EMITIDA | PAGADA | ANULADA
#     monto_total           = Column(Numeric(10, 2))
#     fecha_emision         = Column(Date)
#     ultima_sincronizacion = Column(DateTime)
#     creado_en             = Column(DateTime, server_default=func.now())
#
#     liquidacion = relationship("Liquidacion")


# class PagoExterno(Base):
#     """
#     Referencia a pagos registrados en el sistema de contabilidad externo.
#     Solo se almacena para trazabilidad local. La fuente de verdad es su API.
#     """
#     __tablename__ = "pagos_externos"
#
#     id                    = Column(Integer, primary_key=True, autoincrement=True)
#     id_externo            = Column(String(100), unique=True, nullable=False)
#     comprobante_externo_id= Column(Integer, ForeignKey("comprobantes_externos.id"))
#     fecha_pago            = Column(Date)
#     monto                 = Column(Numeric(10, 2))
#     metodo_pago           = Column(String(50))
#     sincronizado_en       = Column(DateTime, server_default=func.now())
#
#     comprobante_externo = relationship("ComprobanteExterno")
