"""ampliar decimales ley a 5

Revision ID: b5f8e3c0d942
Revises: a4f7e2b9c831
Create Date: 2026-07-30 15:30:00.000000

"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b5f8e3c0d942"
down_revision: str | Sequence[str] | None = "a4f7e2b9c831"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        "analisis_ley",
        "ley_fino",
        type_=sa.Numeric(precision=10, scale=5),
        existing_nullable=True,
    )
    op.alter_column(
        "analisis_ley",
        "ley_grueso",
        type_=sa.Numeric(precision=10, scale=5),
        existing_nullable=True,
    )
    op.alter_column(
        "analisis_ley",
        "ley_final",
        type_=sa.Numeric(precision=10, scale=5),
        existing_nullable=True,
    )
    op.alter_column(
        "analisis_detalle",
        "ley",
        type_=sa.Numeric(precision=10, scale=5),
        existing_nullable=True,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        "analisis_ley",
        "ley_fino",
        type_=sa.Numeric(precision=10, scale=4),
        existing_nullable=True,
    )
    op.alter_column(
        "analisis_ley",
        "ley_grueso",
        type_=sa.Numeric(precision=10, scale=4),
        existing_nullable=True,
    )
    op.alter_column(
        "analisis_ley",
        "ley_final",
        type_=sa.Numeric(precision=10, scale=4),
        existing_nullable=True,
    )
    op.alter_column(
        "analisis_detalle",
        "ley",
        type_=sa.Numeric(precision=10, scale=4),
        existing_nullable=True,
    )
