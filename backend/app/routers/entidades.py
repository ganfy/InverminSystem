"""
Router de gestión de terceros (proveedores/acopiadores).
Endpoints orientados a la pantalla de gestión de terceros.
"""

from app.core.database import get_db
from app.core.deps import check_permiso
from app.schemas.entidades import (
    AcopiadorDropdown,
    CambiarAcopiadorPayload,
    ParametrosRespuesta,
    TerceroCrear,
    TerceroEditar,
    TerceroLista,
    TerceroRespuesta,
)
from app.services import entidades as svc
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

router = APIRouter(prefix="/terceros", tags=["Terceros"])


@router.get("", response_model=list[TerceroLista])
def listar_terceros(
    activo: bool | None = Query(None, description="Filtrar por estado activo/inactivo"),
    current_user=Depends(check_permiso("TERCEROS", "VIEW")),
    db: Session = Depends(get_db),
):
    """Lista proveedores con datos básicos de su acopiador."""
    return svc.listar_terceros(db, activo=activo)


@router.post("", response_model=TerceroRespuesta, status_code=status.HTTP_201_CREATED)
def crear_tercero(
    datos: TerceroCrear,
    current_user=Depends(check_permiso("TERCEROS", "CREATE")),
    db: Session = Depends(get_db),
):
    """
    Crea un proveedor con su acopiador y parámetros comerciales.
    Todo en una sola operación — refleja la pantalla 'Registrar tercero'.
    """
    try:
        return svc.crear_tercero(db, datos, usuario_id=current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.get("/acopiadores", response_model=list[AcopiadorDropdown])
def listar_acopiadores(
    current_user=Depends(check_permiso("TERCEROS", "VIEW")),
    db: Session = Depends(get_db),
):
    """
    Lista acopiadores activos para poblar el dropdown en la UI.
    Endpoint separado y liviano — no incluye parámetros.
    """
    return svc.listar_acopiadores(db)


@router.get("/acopiadores/{acopiador_id}/parametros", response_model=ParametrosRespuesta | None)
def obtener_parametros_acopiador(
    acopiador_id: int,
    current_user=Depends(check_permiso("TERCEROS", "VIEW")),
    db: Session = Depends(get_db),
):
    """
    Retorna parámetros existentes de un acopiador.
    Usado para pre-llenar el formulario cuando se selecciona un acopiador conocido.
    Retorna null si el acopiador no tiene parámetros previos.
    """
    return svc.obtener_parametros_acopiador(db, acopiador_id)


@router.get("/buscar-ruc/{ruc}", response_model=TerceroRespuesta | None)
def buscar_por_ruc(
    ruc: str,
    current_user=Depends(check_permiso("TERCEROS", "VIEW")),
    db: Session = Depends(get_db),
):
    """
    Busca un proveedor por RUC para auto-completar el formulario.
    Retorna null si no existe — no es un error.
    """
    return svc.buscar_por_ruc(db, ruc)


@router.get("/{entidad_id}", response_model=TerceroRespuesta)
def obtener_tercero(
    entidad_id: int,
    current_user=Depends(check_permiso("TERCEROS", "VIEW")),
    db: Session = Depends(get_db),
):
    """Detalle completo de un tercero — pantalla de edición."""
    try:
        return svc.obtener_tercero(db, entidad_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.put("/{entidad_id}", response_model=TerceroRespuesta)
def editar_tercero(
    entidad_id: int,
    datos: TerceroEditar,
    current_user=Depends(check_permiso("TERCEROS", "UPDATE")),
    db: Session = Depends(get_db),
):
    """
    Edita datos básicos y parámetros comerciales.
    Refleja la pantalla 'Editar datos de terceros'.
    """
    try:
        return svc.editar_tercero(db, entidad_id, datos, usuario_id=current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.patch("/{entidad_id}/activar", response_model=TerceroRespuesta)
def activar_tercero(
    entidad_id: int,
    current_user=Depends(check_permiso("TERCEROS", "UPDATE")),
    db: Session = Depends(get_db),
):
    """Activa un tercero desactivado."""
    try:
        return svc.cambiar_estado(db, entidad_id, activo=True, usuario_id=current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.patch("/{entidad_id}/desactivar", response_model=TerceroRespuesta)
def desactivar_tercero(
    entidad_id: int,
    current_user=Depends(check_permiso("TERCEROS", "UPDATE")),
    db: Session = Depends(get_db),
):
    """Desactiva un tercero — soft delete."""
    try:
        return svc.cambiar_estado(db, entidad_id, activo=False, usuario_id=current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.patch("/{entidad_id}/acopiador", response_model=TerceroRespuesta)
def cambiar_acopiador(
    entidad_id: int,
    datos: CambiarAcopiadorPayload,
    current_user=Depends(check_permiso("TERCEROS", "UPDATE")),
    db: Session = Depends(get_db),
):
    """
    Cambia el acopiador de un proveedor.
    Bloqueado si ya existen sesiones de balanza para esta relación.
    Solo Admin y Gerencia (TERCEROS UPDATE).
    """
    try:
        return svc.cambiar_acopiador(
            db,
            entidad_id,
            datos.acopiador_id,
            usuario_id=current_user.id,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e


@router.delete("/{entidad_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_tercero(
    entidad_id: int,
    current_user=Depends(check_permiso("TERCEROS", "DELETE")),
    db: Session = Depends(get_db),
):
    """
    Elimina permanentemente un tercero sin sesiones en balanza.
    Solo Admin (TERCEROS DELETE según RBAC).
    """
    try:
        svc.eliminar_tercero(db, entidad_id, usuario_id=current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e
