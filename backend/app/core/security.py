import uuid
from datetime import UTC, datetime, timedelta

import app.core.config
import bcrypt
from jose import jwt
from sqlalchemy.orm import Session

settings = app.core.config.get_settings()


# ── Hashing de contraseñas ────────────────────────────────────────────────────
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


# ── JWT ───────────────────────────────────────────────────────────────────────


def _build_token(
    subject: str,
    rol: str,
    token_type: str,
    expires_delta: timedelta,
) -> tuple[str, str, datetime]:
    """
    Construye un JWT. Retorna (token, jti, expires_at).
    jti (JWT ID) es el ID único del token, usado para la blacklist.
    """
    jti = str(uuid.uuid4())
    expires_at = datetime.now(UTC) + expires_delta

    payload = {
        "sub": subject,  # user_id como string
        "rol": rol,
        "type": token_type,
        "jti": jti,
        "exp": expires_at,
        "iat": datetime.now(UTC),
    }
    token = jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)
    return token, jti, expires_at


def create_access_token(user_id: int, rol: str) -> tuple[str, str, datetime]:
    """Retorna (access_token, jti, expires_at)."""
    return _build_token(
        subject=str(user_id),
        rol=rol,
        token_type="access",
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )


def create_refresh_token(user_id: int, rol: str) -> tuple[str, str, datetime]:
    """Retorna (refresh_token, jti, expires_at)."""
    return _build_token(
        subject=str(user_id),
        rol=rol,
        token_type="refresh",
        expires_delta=timedelta(days=settings.refresh_token_expire_days),
    )


def decode_token(token: str) -> dict:
    """
    Decodifica y valida un JWT.
    Lanza JWTError si el token es inválido o expirado.
    """
    return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])


# ── Blacklist ─────────────────────────────────────────────────────────────────
# Se importa el modelo aquí para evitar circular imports con models/__init__


def is_token_revoked(jti: str, db: Session) -> bool:
    """Verifica si el jti está en la blacklist."""
    from app.models.auth import TokenRevocado

    return db.query(TokenRevocado).filter(TokenRevocado.jti == jti).first() is not None


def revoke_token(jti: str, expires_at: datetime, db: Session) -> None:
    """Agrega el jti a la blacklist."""
    from app.models.auth import TokenRevocado

    revocado = TokenRevocado(jti=jti, expira_en=expires_at)
    db.add(revocado)
    db.commit()


def cleanup_expired_tokens(db: Session) -> int:
    """
    Elimina tokens expirados de la blacklist.
    Llamar periódicamente (ej: tarea diaria o en el startup).
    Retorna la cantidad de tokens eliminados.
    """
    from app.models.auth import TokenRevocado

    now = datetime.now(UTC)
    deleted = (
        db.query(TokenRevocado)
        .filter(TokenRevocado.expira_en < now)
        .delete(synchronize_session=False)
    )
    db.commit()
    return deleted
