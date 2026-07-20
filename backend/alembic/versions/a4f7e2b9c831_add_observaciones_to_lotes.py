"""Add observaciones to lotes

Revision ID: a4f7e2b9c831
Revises: 533090621f00
Create Date: 2026-07-20 15:00:00.000000

"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a4f7e2b9c831"
down_revision: str | Sequence[str] | None = "533090621f00"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Agrega la columna observaciones a la tabla lotes."""
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [c["name"] for c in inspector.get_columns("lotes")]
    if "observaciones" not in columns:
        op.add_column(
            "lotes",
            sa.Column("observaciones", sa.String(length=500), nullable=True),
        )


def downgrade() -> None:
    """Elimina la columna observaciones de la tabla lotes."""
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [c["name"] for c in inspector.get_columns("lotes")]
    if "observaciones" in columns:
        op.drop_column("lotes", "observaciones")
