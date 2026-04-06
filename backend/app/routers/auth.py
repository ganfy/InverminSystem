"""
Router de autenticación.
Endpoints: POST /auth/login, POST /auth/logout, POST /auth/refresh, GET /auth/me
"""

from datetime import UTC, datetime

from app.core.config import get_settings
from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    is_token_revoked,
    revoke_token,
    verify_password,
)
from app.schemas.auth import LoginRequest, RefreshRequest, TokenResponse, UsuarioMe
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.orm import Session

router = APIRouter(prefix="/auth", tags=["Autenticación"])
bearer_scheme = HTTPBearer()


def _get_settings():
    return get_settings()


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    """
    Autenticar usuario con username y password.
    Retorna access_token (30 min) y refresh_token (7 días).
    """
    from app.models.models import Usuario

    user = (
        db.query(Usuario)
        .filter(
            Usuario.username == data.username,
            Usuario.activo,
        )
        .first()
    )

    if not user or not verify_password(data.password, user.password_hash):
        # Mismo mensaje para no revelar si el usuario existe
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
        )

    rol_codigo = user.rol.codigo if user.rol else "SIN_ROL"
    settings = _get_settings()

    access_token, _, _ = create_access_token(user.id, rol_codigo)
    refresh_token, _, _ = create_refresh_token(user.id, rol_codigo)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.access_token_expire_minutes * 60,
        rol=rol_codigo,
        nombre=user.nombre_completo,
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh(
    data: RefreshRequest,
    db: Session = Depends(get_db),
):
    """
    Renovar access_token usando el refresh_token.

    Implementa rotación de tokens:
    - El refresh_token usado se revoca inmediatamente.
    - Se emiten un nuevo access_token y un nuevo refresh_token.
    - Si el mismo refresh_token se usa dos veces → 401 (ya está revocado).
    """
    invalid_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Refresh token inválido o expirado",
    )

    try:
        payload = decode_token(data.refresh_token)
    except JWTError as exc:
        raise invalid_exc from exc

    if payload.get("type") != "refresh":
        raise invalid_exc

    jti = payload.get("jti")
    if not jti or is_token_revoked(jti, db):
        raise invalid_exc

    user_id = payload.get("sub")
    if not user_id:
        raise invalid_exc

    from app.models.models import Usuario

    user = (
        db.query(Usuario)
        .filter(
            Usuario.id == int(user_id),
            Usuario.activo,
        )
        .first()
    )

    if not user:
        raise invalid_exc

    # Revocar el refresh token usado - evita reutilización
    expires_at = datetime.fromtimestamp(payload["exp"], tz=UTC)
    revoke_token(jti, expires_at, db)

    # Emitir nuevos tokens
    rol_codigo = user.rol.codigo if user.rol else "SIN_ROL"
    settings = _get_settings()

    access_token, _, _ = create_access_token(user.id, rol_codigo)
    new_refresh_token, _, _ = create_refresh_token(user.id, rol_codigo)

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        expires_in=settings.access_token_expire_minutes * 60,
        rol=rol_codigo,
        nombre=user.nombre_completo,
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Invalida el access_token actual agregándolo a la blacklist.
    El frontend debe eliminar ambos tokens (access y refresh) localmente.
    """
    try:
        payload = decode_token(credentials.credentials)
        jti = payload["jti"]
        expires_at = datetime.fromtimestamp(payload["exp"], tz=UTC)
        revoke_token(jti, expires_at, db)
    except (JWTError, KeyError):
        # Si el token ya era inválido, igual retornamos 204
        pass


@router.get("/me", response_model=UsuarioMe)
def me(current_user=Depends(get_current_user)):
    """Retorna los datos del usuario autenticado."""
    return {
        "id": current_user.id,
        "username": current_user.username,
        "nombre_completo": current_user.nombre_completo,
        "rol": current_user.rol.codigo if current_user.rol else None,
        "email": current_user.email,
    }
