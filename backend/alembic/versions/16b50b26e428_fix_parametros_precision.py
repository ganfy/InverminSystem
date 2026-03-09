"""fix_parametros_precision

Revision ID: 16b50b26e428
Revises: 9f009acaf520
Create Date: 2026-03-09 11:19:12.358389

"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "16b50b26e428"
down_revision: str | Sequence[str] | None = "9f009acaf520"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        "parametros_comerciales",
        "lim_ley_comercial",
        type_=sa.Numeric(precision=8, scale=3),
        existing_nullable=True,
    )
    op.alter_column(
        "parametros_comerciales",
        "dscto_ley_comercial",
        type_=sa.Numeric(precision=8, scale=3),
        existing_nullable=True,
    )
    op.alter_column(
        "parametros_comerciales",
        "porcentaje_ley_comercial",
        type_=sa.Numeric(precision=8, scale=3),
        existing_nullable=True,
    )
    op.alter_column(
        "parametros_comerciales",
        "lim_ley_inferior",
        type_=sa.Numeric(precision=8, scale=3),
        existing_nullable=True,
    )
    op.alter_column(
        "parametros_comerciales",
        "lim_ley_superior",
        type_=sa.Numeric(precision=8, scale=3),
        existing_nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "parametros_comerciales",
        "lim_ley_comercial",
        type_=sa.Numeric(precision=5, scale=3),
        existing_nullable=True,
    )
    op.alter_column(
        "parametros_comerciales",
        "dscto_ley_comercial",
        type_=sa.Numeric(precision=5, scale=3),
        existing_nullable=True,
    )
    op.alter_column(
        "parametros_comerciales",
        "porcentaje_ley_comercial",
        type_=sa.Numeric(precision=5, scale=3),
        existing_nullable=True,
    )
    op.alter_column(
        "parametros_comerciales",
        "lim_ley_inferior",
        type_=sa.Numeric(precision=5, scale=3),
        existing_nullable=True,
    )
    op.alter_column(
        "parametros_comerciales",
        "lim_ley_superior",
        type_=sa.Numeric(precision=5, scale=3),
        existing_nullable=True,
    )
