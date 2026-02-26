"""
Dependencies de FastAPI para inyección en endpoints.

Uso típico:
    @router.get("/algo")
    def mi_endpoint(
        current_user: Usuario = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
        ...
"""

import logging

from app.core.database import get_db
from app.core.security import decode_token, is_token_revoked
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

# Extrae el token del header Authorization: Bearer <token>
bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
):
    """
    Valida el token JWT y retorna el usuario autenticado.
    Verifica: firma válida, no expirado, no revocado, usuario activo.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas o sesión expirada",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_token(credentials.credentials)
    except JWTError as exc:
        raise credentials_exception from exc

    # Solo access tokens son válidos para endpoints normales
    if payload.get("type") != "access":
        raise credentials_exception

    # Verificar blacklist
    jti = payload.get("jti")
    if not jti or is_token_revoked(jti, db):
        raise credentials_exception

    user_id = payload.get("sub")
    if not user_id:
        raise credentials_exception

    # Importar aquí para evitar circular imports
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
        raise credentials_exception

    return user


def get_current_user_payload(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> dict:
    """
    Retorna el payload del token sin consultar la BD.
    Útil cuando solo necesitas el rol del token para validación rápida.
    """
    try:
        payload = decode_token(credentials.credentials)
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
        ) from exc

    jti = payload.get("jti")
    if not jti or is_token_revoked(jti, db):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sesión revocada",
        )
    return payload


# ── RBAC helpers ──────────────────────────────────────────────────────────────


def require_roles(*roles: str):
    """
    Dependency factory que exige que el usuario tenga uno de los roles
    indicados. Usar para casos simples donde no se necesita la matriz
    completa de permisos.

    Uso:
        @router.delete("/lotes/{id}")
        def eliminar_lote(
            current_user = Depends(require_roles("Admin", "Gerencia", "Comercial")),
            db: Session = Depends(get_db),
        ):
            ...
    """

    def _check(current_user=Depends(get_current_user)):
        rol_codigo = current_user.rol.codigo if current_user.rol else None
        if rol_codigo not in roles:
            logger.warning(
                "ACCESO_DENEGADO usuario=%s rol=%s roles_requeridos=%s",
                current_user.username,
                rol_codigo,
                roles,
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acción restringida. Roles permitidos: {', '.join(roles)}",
            )
        return current_user

    return _check


def check_permiso(modulo: str, operacion: str):
    """
    Dependency factory que verifica la tabla permisos (RBAC granular).
    Consulta la matriz rol x módulo x operación.

    Admin tiene acceso total y omite la consulta a la tabla.
    Los intentos denegados se registran en el log de auditoría (RF-SYS-001).

    Uso:
        @router.post("/sesiones")
        def crear_sesion(
            current_user = Depends(check_permiso("BALANZA", "CREATE")),
            db: Session = Depends(get_db),
        ):
            ...
    """

    def _check(
        current_user=Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
        from app.models.enums import RolSistema
        from app.models.models import Modulo, Operacion, Permiso

        rol_codigo = current_user.rol.codigo if current_user.rol else None

        # Admin tiene acceso total — no consultar la tabla
        if rol_codigo == RolSistema.ADMIN:
            return current_user

        tiene_permiso = (
            db.query(Permiso)
            .join(Modulo, Permiso.modulo_id == Modulo.id)
            .join(Operacion, Permiso.operacion_id == Operacion.id)
            .filter(
                Permiso.rol_id == current_user.rol_id,
                Modulo.codigo == modulo,
                Operacion.codigo == operacion,
                Permiso.permitido,
            )
            .first()
        )

        if not tiene_permiso:
            # RF-SYS-001: registrar intento no autorizado en log de auditoría
            logger.warning(
                "ACCESO_DENEGADO usuario=%s rol=%s modulo=%s operacion=%s",
                current_user.username,
                rol_codigo,
                modulo,
                operacion,
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tiene permisos para realizar esta acción",
            )

        return current_user

    return _check
