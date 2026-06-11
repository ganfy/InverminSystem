"""add CERT_RECONOCIMIENTO to estado constraint

Revision ID: 3bd3e5785693
Revises: ba569ad13cda
Create Date: 2026-06-08 13:07:51.875273

"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "3bd3e5785693"
down_revision: str | Sequence[str] | None = "ba569ad13cda"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Eliminar constraint anterior
    op.drop_constraint("ck_analisis_rec_estado", "analisis_recuperacion", type_="check")
    # Recrear con el nuevo valor permitido
    op.create_check_constraint(
        "ck_analisis_rec_estado",
        "analisis_recuperacion",
        "estado IN ('PENDIENTE', 'COMPLETADO', 'CERT_COMERCIAL', 'CERT_RECONOCIMIENTO')",
    )


def downgrade() -> None:
    op.drop_constraint("ck_analisis_rec_estado", "analisis_recuperacion", type_="check")
    op.create_check_constraint(
        "ck_analisis_rec_estado",
        "analisis_recuperacion",
        "estado IN ('PENDIENTE', 'COMPLETADO', 'CERT_COMERCIAL')",
    )
