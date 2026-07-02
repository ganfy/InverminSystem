"""add_sub_tipo_to_analisis_recuperacion

Revision ID: b2c3d4e5f6a1
Revises: a1b2c3d4e5f6
Create Date: 2026-06-22 12:00:00.000000

Agrega columna sub_tipo a analisis_recuperacion para diferenciar registros
de Sólidos (SOLIDOS) y Solución/Absorción Atómica (SOLUCION) en Reconocimientos.
Los registros existentes (legacy) quedarán con sub_tipo = NULL.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b2c3d4e5f6a1"
down_revision: str | Sequence[str] | None = "a1b2c3d4e5f6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add sub_tipo column to analisis_recuperacion."""
    op.add_column(
        "analisis_recuperacion",
        sa.Column(
            "sub_tipo",
            sa.String(10),
            nullable=True,
            comment="Sub-tipo de reconocimiento: SOLIDOS | SOLUCION | NULL (legacy)",
        ),
    )


def downgrade() -> None:
    """Remove sub_tipo column from analisis_recuperacion."""
    op.drop_column("analisis_recuperacion", "sub_tipo")
