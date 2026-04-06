"""
Schemas de usuarios - gestión administrativa.
Solo accesible por Admin (RF-SYS-001 módulo ADMINISTRACIÓN).
"""

from pydantic import BaseModel, EmailStr, field_validator


class UsuarioCrear(BaseModel):
    username: str
    password: str
    nombre_completo: str
    rol_codigo: str  # Admin, Gerencia, Comercial, etc.
    email: EmailStr | None = None

    @field_validator("username")
    @classmethod
    def username_valido(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 3:
            raise ValueError("El username debe tener al menos 3 caracteres")
        if not v.replace("_", "").replace(".", "").isalnum():
            raise ValueError("El username solo puede contener letras, números, _ y .")
        return v.lower()

    @field_validator("password")
    @classmethod
    def password_valido(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres")
        return v

    @field_validator("rol_codigo")
    @classmethod
    def rol_valido(cls, v: str) -> str:
        from app.models.enums import RolSistema

        codigos_validos = [r.value for r in RolSistema]
        if v not in codigos_validos:
            raise ValueError(f"Rol inválido. Opciones: {', '.join(codigos_validos)}")
        return v


class UsuarioEditar(BaseModel):
    nombre_completo: str | None = None
    rol_codigo: str | None = None
    email: EmailStr | None = None

    @field_validator("rol_codigo")
    @classmethod
    def rol_valido(cls, v: str | None) -> str | None:
        if v is None:
            return v
        from app.models.enums import RolSistema

        codigos_validos = [r.value for r in RolSistema]
        if v not in codigos_validos:
            raise ValueError(f"Rol inválido. Opciones: {', '.join(codigos_validos)}")
        return v


class CambiarPassword(BaseModel):
    password_actual: str
    password_nuevo: str

    @field_validator("password_nuevo")
    @classmethod
    def password_valido(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres")
        return v


class ResetPassword(BaseModel):
    password_nuevo: str

    @field_validator("password_nuevo")
    @classmethod
    def password_valido(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres")
        return v


class UsuarioRespuesta(BaseModel):
    id: int
    username: str
    nombre_completo: str
    rol: str
    email: str | None = None
    activo: bool

    model_config = {"from_attributes": True}


class UsuarioLista(BaseModel):
    """Schema resumido para listado."""

    id: int
    username: str
    nombre_completo: str
    rol: str
    activo: bool

    model_config = {"from_attributes": True}
