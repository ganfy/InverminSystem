"""
Modelos relacionados con autenticación.
Separados de models.py principal para mantener cohesión.
"""

from app.models.base import Base
from sqlalchemy import Column, DateTime, Index, Integer, String, func


class TokenRevocado(Base):
    """
    Blacklist de tokens JWT revocados.

    Al hacer logout o al desactivar un usuario, el jti del token
    se agrega aquí. Cada request autenticado verifica que su jti
    no esté en esta tabla.

    cleanup_expired_tokens() en security.py limpia registros vencidos
    para mantener la tabla pequeña. Con 11 usuarios y tokens de 30 min,
    esta tabla nunca crecerá significativamente.
    """

    __tablename__ = "tokens_revocados"

    id = Column(Integer, primary_key=True, autoincrement=True)
    jti = Column(String(36), unique=True, nullable=False)  # JWT ID
    expira_en = Column(DateTime(timezone=True), nullable=False)
    revocado_en = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        # Índice en expira_en para que el cleanup sea rápido
        Index("ix_tokens_revocados_expira_en", "expira_en"),
    )
