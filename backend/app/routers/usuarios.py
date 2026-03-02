"""
Router de gestión de usuarios.
Todos los endpoints requieren rol Admin, excepto cambiar-password
que puede hacerlo cualquier usuario autenticado sobre sí mismo.
"""

from app.core.database import get_db
from app.core.deps import check_permiso, get_current_user
from app.schemas.usuarios import (
    CambiarPassword,
    ResetPassword,
    UsuarioCrear,
    UsuarioEditar,
    UsuarioLista,
    UsuarioRespuesta,
)
from app.services import usuarios as svc
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

router = APIRouter(prefix="/admin/usuarios", tags=["Usuarios"])


def _rol_str(usuario) -> str:
    return usuario.rol.codigo if usuario.rol else "SIN_ROL"


def _serializar(usuario) -> dict:
    return {
        "id": usuario.id,
        "username": usuario.username,
        "nombre_completo": usuario.nombre_completo,
        "rol": _rol_str(usuario),
        "email": usuario.email,
        "activo": usuario.activo,
    }


@router.get("", response_model=list[UsuarioLista])
def listar_usuarios(
    current_user=Depends(check_permiso("ADMINISTRACION", "VIEW")),
    db: Session = Depends(get_db),
):
    """Lista todos los usuarios del sistema."""
    usuarios = svc.listar_usuarios(db)
    return [_serializar(u) for u in usuarios]


@router.post("", response_model=UsuarioRespuesta, status_code=status.HTTP_201_CREATED)
def crear_usuario(
    datos: UsuarioCrear,
    current_user=Depends(check_permiso("ADMINISTRACION", "CREATE")),
    db: Session = Depends(get_db),
):
    """Crea un nuevo usuario del sistema. Solo Admin."""
    try:
        usuario = svc.crear_usuario(db, datos, creado_por=current_user.id)
        return _serializar(usuario)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.get("/{usuario_id}", response_model=UsuarioRespuesta)
def obtener_usuario(
    usuario_id: int,
    current_user=Depends(check_permiso("ADMINISTRACION", "VIEW")),
    db: Session = Depends(get_db),
):
    """Retorna detalle de un usuario."""
    try:
        usuario = svc.obtener_usuario(db, usuario_id)
        return _serializar(usuario)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.put("/{usuario_id}", response_model=UsuarioRespuesta)
def editar_usuario(
    usuario_id: int,
    datos: UsuarioEditar,
    current_user=Depends(check_permiso("ADMINISTRACION", "UPDATE")),
    db: Session = Depends(get_db),
):
    """Edita nombre, rol o email de un usuario. Solo Admin."""
    try:
        usuario = svc.editar_usuario(db, usuario_id, datos, modificado_por=current_user.id)
        return _serializar(usuario)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.patch("/{usuario_id}/activar", response_model=UsuarioRespuesta)
def activar_usuario(
    usuario_id: int,
    current_user=Depends(check_permiso("ADMINISTRACION", "UPDATE")),
    db: Session = Depends(get_db),
):
    """Activa un usuario desactivado. Solo Admin."""
    try:
        usuario = svc.cambiar_estado(db, usuario_id, activo=True, modificado_por=current_user.id)
        return _serializar(usuario)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.patch("/{usuario_id}/desactivar", response_model=UsuarioRespuesta)
def desactivar_usuario(
    usuario_id: int,
    current_user=Depends(check_permiso("ADMINISTRACION", "UPDATE")),
    db: Session = Depends(get_db),
):
    """
    Desactiva un usuario — soft delete.
    No se puede desactivar a uno mismo.
    Solo Admin.
    """
    try:
        usuario = svc.cambiar_estado(db, usuario_id, activo=False, modificado_por=current_user.id)
        return _serializar(usuario)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.patch("/{usuario_id}/reset-password", status_code=status.HTTP_204_NO_CONTENT)
def resetear_password(
    usuario_id: int,
    datos: ResetPassword,
    current_user=Depends(check_permiso("ADMINISTRACION", "UPDATE")),
    db: Session = Depends(get_db),
):
    """
    Reset de password por Admin — no requiere password actual.
    Body: { "password_nuevo": "..." }
    """
    try:
        svc.resetear_password(db, usuario_id, datos.password_nuevo, modificado_por=current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.patch("/me/cambiar-password", status_code=status.HTTP_204_NO_CONTENT)
def cambiar_password(
    datos: CambiarPassword,
    current_user=Depends(get_current_user),  # cualquier usuario autenticado
    db: Session = Depends(get_db),
):
    """
    Cambio de password por el propio usuario.
    Requiere verificar password actual.
    Disponible para todos los roles.
    """
    try:
        svc.cambiar_password(
            db,
            usuario_id=current_user.id,
            password_actual=datos.password_actual,
            password_nuevo=datos.password_nuevo,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
