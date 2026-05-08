"""add CERT_COMERCIAL to estado constraint

Revision ID: d8c256f9c9c0
Revises: db93dd08305f
Create Date: 2026-05-08 12:18:36.355977

"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d8c256f9c9c0"
down_revision: str | Sequence[str] | None = "db93dd08305f"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Eliminar constraint anterior
    op.drop_constraint("ck_analisis_rec_estado", "analisis_recuperacion", type_="check")
    # Recrear con el nuevo valor permitido
    op.create_check_constraint(
        "ck_analisis_rec_estado",
        "analisis_recuperacion",
        "estado IN ('PENDIENTE', 'COMPLETADO', 'CERT_COMERCIAL')",
    )


def downgrade() -> None:
    op.drop_constraint("ck_analisis_rec_estado", "analisis_recuperacion", type_="check")
    op.create_check_constraint(
        "ck_analisis_rec_estado",
        "analisis_recuperacion",
        "estado IN ('PENDIENTE', 'COMPLETADO')",
    )
