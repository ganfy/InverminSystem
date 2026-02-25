from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer
from sqlalchemy.orm import declarative_base, declared_attr
from sqlalchemy.sql import func

Base = declarative_base()


class AuditMixin:
    """
    Mixin de auditoría. Hereda en los modelos que necesiten
    trazabilidad de creación y modificación.
    Uso: class Lote(AuditMixin, Base): ...
    """

    creado_en = Column(DateTime, server_default=func.now(), nullable=False)
    modificado_en = Column(DateTime, onupdate=func.now())

    # declared_attr permite que la FK a usuarios funcione correctamente en cada tabla hija (no comparte columna)
    @declared_attr
    def creado_por(cls):
        return Column(Integer, ForeignKey("usuarios.id"))

    @declared_attr
    def modificado_por(cls):
        return Column(Integer, ForeignKey("usuarios.id"))


class SoftDeleteMixin:
    """
    Mixin para eliminación lógica (soft delete).
    Hereda en modelos que no deben borrarse físicamente.
    """

    eliminado = Column(Boolean, default=False, nullable=False)

    @declared_attr
    def eliminado_por(cls):
        return Column(Integer, ForeignKey("usuarios.id"))

    eliminado_en = Column(DateTime)
