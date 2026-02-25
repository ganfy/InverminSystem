from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # segundos hasta expiración del access token
    rol: str
    nombre: str


class RefreshRequest(BaseModel):
    refresh_token: str


class UsuarioMe(BaseModel):
    """Datos del usuario autenticado actual."""

    id: int
    username: str
    nombre_completo: str
    rol: str
    email: str | None = None

    model_config = {"from_attributes": True}
