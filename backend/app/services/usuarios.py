"""
Service de gestión de usuarios.
Lógica de negocio pura — sin dependencias de FastAPI.
Errores como ValueError para que el router los convierta a HTTPException.
"""

from app.core.security import hash_password, verify_password
from app.models.models import Rol, Usuario
from app.schemas.usuarios import UsuarioCrear, UsuarioEditar
from sqlalchemy.orm import Session


def _get_rol(db: Session, codigo: str) -> Rol:
    rol = db.query(Rol).filter_by(codigo=codigo).first()
    if not rol:
        raise ValueError(f"Rol '{codigo}' no encontrado")
    return rol


def listar_usuarios(db: Session) -> list[Usuario]:
    return db.query(Usuario).order_by(Usuario.id).all()


def obtener_usuario(db: Session, usuario_id: int) -> Usuario:
    user = db.query(Usuario).filter_by(id=usuario_id).first()
    if not user:
        raise ValueError(f"Usuario {usuario_id} no encontrado")
    return user


def crear_usuario(
    db: Session,
    datos: UsuarioCrear,
    creado_por: int,
) -> Usuario:
    # Verificar unicidad de username
    if db.query(Usuario).filter_by(username=datos.username).first():
        raise ValueError(f"El username '{datos.username}' ya está en uso")

    rol = _get_rol(db, datos.rol_codigo)

    usuario = Usuario(
        username=datos.username,
        password_hash=hash_password(datos.password),
        nombre_completo=datos.nombre_completo,
        rol_id=rol.id,
        email=datos.email,
        activo=True,
        creado_por=creado_por,
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


def editar_usuario(
    db: Session,
    usuario_id: int,
    datos: UsuarioEditar,
    modificado_por: int,
) -> Usuario:
    usuario = obtener_usuario(db, usuario_id)

    if datos.nombre_completo is not None:
        usuario.nombre_completo = datos.nombre_completo

    if datos.email is not None:
        usuario.email = datos.email

    if datos.rol_codigo is not None:
        rol = _get_rol(db, datos.rol_codigo)
        usuario.rol_id = rol.id

    usuario.modificado_por = modificado_por
    db.commit()
    db.refresh(usuario)
    return usuario


def cambiar_estado(
    db: Session,
    usuario_id: int,
    activo: bool,
    modificado_por: int,
) -> Usuario:
    usuario = obtener_usuario(db, usuario_id)

    # No se puede desactivar a sí mismo
    if usuario_id == modificado_por:
        raise ValueError("No puedes desactivarte a ti mismo")

    usuario.activo = activo
    usuario.modificado_por = modificado_por
    db.commit()
    db.refresh(usuario)
    return usuario


def cambiar_password(
    db: Session,
    usuario_id: int,
    password_actual: str,
    password_nuevo: str,
) -> None:
    """
    Cambio de password por el propio usuario.
    Requiere verificar password actual.
    """
    usuario = obtener_usuario(db, usuario_id)

    if not verify_password(password_actual, usuario.password_hash):
        raise ValueError("La contraseña actual es incorrecta")

    usuario.password_hash = hash_password(password_nuevo)
    usuario.modificado_por = usuario_id
    db.commit()


def resetear_password(
    db: Session,
    usuario_id: int,
    password_nuevo: str,
    modificado_por: int,
) -> None:
    """
    Reset de password por Admin — no requiere password actual.
    """
    usuario = obtener_usuario(db, usuario_id)
    usuario.password_hash = hash_password(password_nuevo)
    usuario.modificado_por = modificado_por
    db.commit()
