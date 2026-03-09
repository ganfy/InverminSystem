"""
Service de gestión de terceros (proveedores/acopiadores).
Lógica de negocio pura — sin dependencias de FastAPI.
"""

from uuid import uuid4

from app.models.enums import RolEntidad, TipoEntidad
from app.models.models import (
    Entidad,
    EntidadRol,
    ParametrosComerciales,
    ProveedorAcopiador,
    Rol,
    SesionDescarga,
)
from app.schemas.entidades import (
    ParametrosSchema,
    TerceroCrear,
    TerceroEditar,
    TipoAcopiador,
)
from sqlalchemy.orm import Session

# =============================================================================
# HELPERS INTERNOS
# =============================================================================


def _get_rol(db: Session, codigo: str) -> Rol:
    rol = db.query(Rol).filter_by(codigo=codigo).first()
    if not rol:
        raise ValueError(f"Rol '{codigo}' no configurado en el sistema")
    return rol


def _asignar_rol(db: Session, entidad: Entidad, codigo_rol: str) -> EntidadRol:
    """Asigna un rol a una entidad si no lo tiene ya."""
    rol = _get_rol(db, codigo_rol)
    existing = db.query(EntidadRol).filter_by(entidad_id=entidad.id, rol_id=rol.id).first()
    if existing:
        if not existing.activo:
            existing.activo = True
        return existing
    er = EntidadRol(entidad_id=entidad.id, rol_id=rol.id, activo=True)
    db.add(er)
    db.flush()
    return er


def _get_or_crear_provacop(
    db: Session,
    proveedor: Entidad,
    acopiador: Entidad,
) -> ProveedorAcopiador:
    """Obtiene o crea la relación proveedor-acopiador."""
    existing = (
        db.query(ProveedorAcopiador)
        .filter_by(
            proveedor_id=proveedor.id,
            acopiador_id=acopiador.id,
        )
        .first()
    )
    if existing:
        return existing
    pa = ProveedorAcopiador(
        proveedor_id=proveedor.id,
        acopiador_id=acopiador.id,
    )
    db.add(pa)
    db.flush()
    return pa


def _actualizar_parametros(
    db: Session,
    provacop: ProveedorAcopiador,
    datos: ParametrosSchema,
    usuario_id: int,
) -> ParametrosComerciales:
    """Crea o actualiza parámetros comerciales para una relación provacop."""
    pc = db.query(ParametrosComerciales).filter_by(provacop_id=provacop.id).first()

    if not pc:
        pc = ParametrosComerciales(
            provacop_id=provacop.id,
            creado_por=usuario_id,
        )
        db.add(pc)

    # Actualizar solo los campos que vienen en el payload
    campos = [
        "umbral_recup_bajo",
        "umbral_recup_medio",
        "umbral_recup_alto",
        "lim_ley_inferior",
        "lim_ley_superior",
        "gasto_acopio",
        "gasto_consumo",
        "maquila",
        "comision",
        "lim_ley_comercial",
        "dscto_ley_comercial",
        "porcentaje_ley_comercial",
        "riesgo_comercial",
    ]
    for campo in campos:
        valor = getattr(datos, campo, None)
        if valor is not None:
            setattr(pc, campo, valor)

    pc.modificado_por = usuario_id
    db.flush()
    return pc


def _get_parametros_acopiador(db: Session, acopiador_id: int) -> ParametrosComerciales | None:
    """
    Obtiene parámetros existentes de un acopiador con cualquier proveedor.
    Útil para pre-llenar el formulario cuando se selecciona un acopiador conocido.
    """
    return (
        db.query(ParametrosComerciales)
        .join(ProveedorAcopiador)
        .filter(ProveedorAcopiador.acopiador_id == acopiador_id)
        .first()
    )


def _serializar_tercero(
    entidad: Entidad,
    provacop: ProveedorAcopiador | None,
    db: Session,
) -> dict:
    """Construye el dict de respuesta para un tercero."""
    acopiador_data = None
    parametros_data = None

    if provacop:
        acopiador = provacop.acopiador
        acopiador_data = {
            "id": acopiador.id,
            "razon_social": acopiador.razon_social,
            "ruc": acopiador.ruc,
            "es_propio": acopiador.id == entidad.id,
        }
        if provacop.parametros:
            pc = provacop.parametros
            parametros_data = {
                "id": pc.id,
                "provacop_id": pc.provacop_id,
                "umbral_recup_bajo": pc.umbral_recup_bajo,
                "umbral_recup_medio": pc.umbral_recup_medio,
                "lim_ley_inferior": pc.lim_ley_inferior,
                "lim_ley_superior": pc.lim_ley_superior,
                "gasto_acopio": pc.gasto_acopio,
                "gasto_consumo": pc.gasto_consumo,
                "maquila": pc.maquila,
                "comision": pc.comision,
                "lim_ley_comercial": pc.lim_ley_comercial,
                "dscto_ley_comercial": pc.dscto_ley_comercial,
                "porcentaje_ley_comercial": pc.porcentaje_ley_comercial,
                "riesgo_comercial": pc.riesgo_comercial,
            }

    return {
        "id": entidad.id,
        "razon_social": entidad.razon_social,
        "ruc": entidad.ruc,
        "referencia": entidad.referencia,
        "telefono": entidad.telefono,
        "email": entidad.email,
        "activo": entidad.activo,
        "provacop_id": provacop.id if provacop else None,
        "acopiador": acopiador_data,
        "parametros": parametros_data,
    }


def _get_provacop_de_entidad(db: Session, entidad_id: int) -> ProveedorAcopiador | None:
    """Busca relación donde la entidad es proveedor O acopiador."""
    # Primero buscar como proveedor
    pa = db.query(ProveedorAcopiador).filter_by(proveedor_id=entidad_id).first()
    if pa:
        return pa

    # Si no, buscar como acopiador
    return db.query(ProveedorAcopiador).filter_by(acopiador_id=entidad_id).first()


# =============================================================================
# OPERACIONES PÚBLICAS
# =============================================================================


def listar_terceros(
    db: Session,
    activo: bool | None = None,
) -> list[dict]:
    """
    Lista UNA FILA POR PROVACOP.
    Un proveedor con 2 acopiadores aparece 2 veces.
    """
    query = (
        db.query(Entidad, ProveedorAcopiador)
        .join(EntidadRol, EntidadRol.entidad_id == Entidad.id)
        .join(Rol, Rol.id == EntidadRol.rol_id)
        .join(
            ProveedorAcopiador,
            ProveedorAcopiador.proveedor_id == Entidad.id,
        )
        .filter(Rol.codigo == RolEntidad.PROVEEDOR)
    )
    if activo is not None:
        query = query.filter(Entidad.activo == activo)

    filas = query.order_by(Entidad.razon_social).all()

    resultado = []
    for entidad, provacop in filas:
        acopiador_nombre = provacop.acopiador.razon_social if provacop.acopiador else None
        resultado.append(
            {
                "id": entidad.id,
                "provacop_id": provacop.id,
                "razon_social": entidad.razon_social,
                "ruc": entidad.ruc,
                "referencia": entidad.referencia,
                "activo": entidad.activo,
                "acopiador": acopiador_nombre,
            }
        )
    return resultado


def obtener_tercero(db: Session, entidad_id: int) -> dict:
    entidad = db.query(Entidad).filter_by(id=entidad_id).first()
    if not entidad:
        raise ValueError(f"Tercero {entidad_id} no encontrado")
    provacop = _get_provacop_de_entidad(db, entidad_id)
    return _serializar_tercero(entidad, provacop, db)


def crear_tercero(
    db: Session,
    datos: TerceroCrear,
    usuario_id: int,
) -> dict:
    # ── Buscar si ya existe entidad con ese RUC
    proveedor = db.query(Entidad).filter_by(ruc=datos.ruc).first() if datos.ruc else None

    if proveedor is None:
        # Crear entidad nueva
        proveedor = Entidad(
            ruc=datos.ruc,
            razon_social=datos.razon_social,
            referencia=datos.referencia,
            telefono=datos.telefono,
            email=datos.email,
            tipo=TipoEntidad.EMPRESA,
            activo=True,
            creado_por=usuario_id,
        )
        db.add(proveedor)
        db.flush()
    # Si ya existe: reutilizar sin modificar sus datos

    # Asignar rol PROVEEDOR (idempotente — no duplica si ya lo tiene)
    _asignar_rol(db, proveedor, RolEntidad.PROVEEDOR)

    # Acopiador
    if datos.tipo_acopiador in (TipoAcopiador.SIN_ACOPIADOR, TipoAcopiador.PROPIO):
        acopiador = proveedor
        _asignar_rol(db, proveedor, RolEntidad.ACOPIADOR)

    elif datos.tipo_acopiador == TipoAcopiador.TERCERO:
        if datos.acopiador_id:
            acopiador = db.query(Entidad).filter_by(id=datos.acopiador_id).first()
            if not acopiador:
                raise ValueError(f"Acopiador {datos.acopiador_id} no encontrado")
        elif datos.acopiador_nuevo:
            ruc_acopiador = datos.acopiador_nuevo.ruc or f"ACOP-{uuid4().hex[:8].upper()}"
            if datos.acopiador_nuevo.ruc:
                if db.query(Entidad).filter_by(ruc=ruc_acopiador).first():
                    raise ValueError(f"Ya existe una entidad con RUC {ruc_acopiador}")
            acopiador = Entidad(
                ruc=ruc_acopiador,
                razon_social=datos.acopiador_nuevo.razon_social,
                tipo=TipoEntidad.PERSONA_NATURAL,
                activo=True,
                creado_por=usuario_id,
            )
            db.add(acopiador)
            db.flush()
        else:
            raise ValueError("Debe indicar acopiador_id o acopiador_nuevo para tipo 'tercero'")

        _asignar_rol(db, acopiador, RolEntidad.ACOPIADOR)

    # ── Verificar que esta combinación proveedor-acopiador no exista ya
    combinacion_existente = (
        db.query(ProveedorAcopiador)
        .filter_by(
            proveedor_id=proveedor.id,
            acopiador_id=acopiador.id,
        )
        .first()
    )
    if combinacion_existente:
        raise ValueError("Ya existe una relación entre este proveedor y ese acopiador.")

    provacop = _get_or_crear_provacop(db, proveedor, acopiador)

    # Parámetros comerciales
    if datos.parametros:
        _actualizar_parametros(db, provacop, datos.parametros, usuario_id)

    db.commit()
    db.refresh(proveedor)

    provacop = _get_provacop_de_entidad(db, proveedor.id)
    return _serializar_tercero(proveedor, provacop, db)


def editar_tercero(
    db: Session,
    entidad_id: int,
    datos: TerceroEditar,
    usuario_id: int,
) -> dict:
    entidad = db.query(Entidad).filter_by(id=entidad_id).first()
    if not entidad:
        raise ValueError(f"Tercero {entidad_id} no encontrado")

    if datos.razon_social is not None:
        entidad.razon_social = datos.razon_social
    if datos.referencia is not None:
        entidad.referencia = datos.referencia
    if datos.telefono is not None:
        entidad.telefono = datos.telefono
    if datos.email is not None:
        entidad.email = datos.email
    entidad.modificado_por = usuario_id

    if datos.parametros:
        provacop = _get_provacop_de_entidad(db, entidad_id)
        if not provacop:
            raise ValueError("Este tercero no tiene relación comercial configurada")
        _actualizar_parametros(db, provacop, datos.parametros, usuario_id)

    db.commit()
    db.refresh(entidad)

    provacop = _get_provacop_de_entidad(db, entidad_id)
    return _serializar_tercero(entidad, provacop, db)


def cambiar_estado(
    db: Session,
    entidad_id: int,
    activo: bool,
    usuario_id: int,
) -> dict:
    entidad = db.query(Entidad).filter_by(id=entidad_id).first()
    if not entidad:
        raise ValueError(f"Tercero {entidad_id} no encontrado")
    entidad.activo = activo
    entidad.modificado_por = usuario_id
    db.commit()
    db.refresh(entidad)
    provacop = _get_provacop_de_entidad(db, entidad_id)
    return _serializar_tercero(entidad, provacop, db)


def listar_acopiadores(db: Session) -> list[dict]:
    """
    Lista entidades con rol ACOPIADOR para poblar el dropdown.
    Incluye los parámetros existentes para pre-llenar el formulario.
    """
    acopiadores = (
        db.query(Entidad)
        .join(EntidadRol, EntidadRol.entidad_id == Entidad.id)
        .join(Rol, Rol.id == EntidadRol.rol_id)
        .filter(
            Rol.codigo == RolEntidad.ACOPIADOR,
            EntidadRol.activo.is_(True),
            Entidad.activo.is_(True),
        )
        .order_by(Entidad.razon_social)
        .all()
    )
    return [{"id": a.id, "razon_social": a.razon_social, "ruc": a.ruc} for a in acopiadores]


def obtener_parametros_acopiador(db: Session, acopiador_id: int) -> dict | None:
    """
    Retorna parámetros existentes de un acopiador para pre-llenar el formulario
    cuando se selecciona un acopiador conocido en la pantalla de creación.
    """
    pc = _get_parametros_acopiador(db, acopiador_id)
    if not pc:
        return None
    return {
        "id": pc.id,
        "provacop_id": pc.provacop_id,
        "umbral_recup_bajo": pc.umbral_recup_bajo,
        "umbral_recup_medio": pc.umbral_recup_medio,
        "lim_ley_inferior": pc.lim_ley_inferior,
        "lim_ley_superior": pc.lim_ley_superior,
        "gasto_acopio": pc.gasto_acopio,
        "gasto_consumo": pc.gasto_consumo,
        "maquila": pc.maquila,
        "comision": pc.comision,
        "lim_ley_comercial": pc.lim_ley_comercial,
        "dscto_ley_comercial": pc.dscto_ley_comercial,
        "porcentaje_ley_comercial": pc.porcentaje_ley_comercial,
        "riesgo_comercial": pc.riesgo_comercial,
    }


def _contar_sesiones_provacop(db: Session, provacop_id: int) -> int:
    """Retorna cuántas sesiones de balanza existen para esta relación provacop."""
    return db.query(SesionDescarga).filter_by(provacop_id=provacop_id).count()


def cambiar_acopiador(
    db: Session,
    entidad_id: int,
    nuevo_acopiador_id: int,
    usuario_id: int,
) -> dict:
    """
    Cambia el acopiador de un proveedor.
    Solo permitido si la relación actual NO tiene sesiones registradas.
    """
    entidad = db.query(Entidad).filter_by(id=entidad_id).first()
    if not entidad:
        raise ValueError(f"Tercero {entidad_id} no encontrado")

    provacop = _get_provacop_de_entidad(db, entidad_id)
    if not provacop:
        raise ValueError("Este proveedor no tiene relación comercial registrada")

    # ── Bloqueo si hay sesiones ───────────────────────────────────────────────
    n_sesiones = _contar_sesiones_provacop(db, provacop.id)
    if n_sesiones > 0:
        raise ValueError(
            f"No se puede cambiar el acopiador: este proveedor ya tiene "
            f"{n_sesiones} sesión(es) registrada(s) en balanza. "
            f"El acopiador forma parte del registro histórico."
        )

    # ── Verificar que el nuevo acopiador existe ───────────────────────────────
    nuevo_acopiador = db.query(Entidad).filter_by(id=nuevo_acopiador_id).first()
    if not nuevo_acopiador:
        raise ValueError(f"Acopiador {nuevo_acopiador_id} no encontrado")

    # ── Verificar que no existe ya esa combinación ────────────────────────────
    existe = (
        db.query(ProveedorAcopiador)
        .filter_by(
            proveedor_id=entidad_id,
            acopiador_id=nuevo_acopiador_id,
        )
        .first()
    )
    if existe:
        raise ValueError("Ya existe una relación con ese acopiador")

    # ── Actualizar: borrar params y cambiar FK ────────────────────────────────
    if provacop.parametros:
        db.delete(provacop.parametros)
        db.flush()

    provacop.acopiador_id = nuevo_acopiador_id
    db.commit()
    db.refresh(entidad)

    provacop = _get_provacop_de_entidad(db, entidad_id)
    return _serializar_tercero(entidad, provacop, db)


def eliminar_tercero(
    db: Session,
    entidad_id: int,
    usuario_id: int,
) -> None:
    """
    Elimina un tercero (proveedor) de forma permanente.
    Solo permitido si la relación comercial NO tiene sesiones registradas.
    Solo Admin y Gerencia pueden ejecutar esto (validado en el router).
    """
    entidad = db.query(Entidad).filter_by(id=entidad_id).first()
    if not entidad:
        raise ValueError(f"Tercero {entidad_id} no encontrado")

    provacop = _get_provacop_de_entidad(db, entidad_id)

    # ── Bloqueo si hay sesiones ───────────────────────────────────────────────
    if provacop:
        n_sesiones = _contar_sesiones_provacop(db, provacop.id)
        if n_sesiones > 0:
            raise ValueError(
                f"No se puede eliminar: este proveedor tiene "
                f"{n_sesiones} sesión(es) registrada(s) en balanza."
            )

        # Borrar en orden por FK: params → provacop
        if provacop.parametros:
            db.delete(provacop.parametros)
            db.flush()
        db.delete(provacop)
        db.flush()

    # Borrar roles de entidad y la entidad misma
    db.query(EntidadRol).filter_by(entidad_id=entidad_id).delete()
    db.flush()
    db.delete(entidad)
    db.commit()


def buscar_por_ruc(db: Session, ruc: str) -> dict | None:
    """Busca entidad con rol PROVEEDOR por RUC. Retorna None si no existe."""
    entidad = (
        db.query(Entidad)
        .join(EntidadRol, EntidadRol.entidad_id == Entidad.id)
        .join(Rol, Rol.id == EntidadRol.rol_id)
        .filter(Rol.codigo == RolEntidad.PROVEEDOR, Entidad.ruc == ruc)
        .first()
    )
    if not entidad:
        return None
    provacop = _get_provacop_de_entidad(db, entidad.id)
    return _serializar_tercero(entidad, provacop, db)
