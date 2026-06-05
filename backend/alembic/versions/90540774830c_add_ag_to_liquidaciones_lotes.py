"""add_ag_to_liquidaciones_lotes

Revision ID: 90540774830c
Revises: d8c256f9c9c0
Create Date: 2026-05-18 17:01:32.197408

"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "90540774830c"
down_revision: str | Sequence[str] | None = "d8c256f9c9c0"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "liquidaciones_lotes",
        sa.Column("ley_ag_gr_tm_snapshot", sa.Numeric(precision=10, scale=3), nullable=True),
    )
    op.add_column(
        "liquidaciones_lotes",
        sa.Column("spot_ag_snapshot", sa.Numeric(precision=10, scale=2), nullable=True),
    )
    op.add_column(
        "liquidaciones_lotes",
        sa.Column("valor_ag_usd", sa.Numeric(precision=12, scale=2), nullable=True),
    )
    op.add_column(
        "parametros_comerciales",
        sa.Column("umbral_ag_oz_tc", sa.Numeric(precision=8, scale=4), nullable=True),
    )
    op.add_column(
        "parametros_comerciales",
        sa.Column("rec_ag_pct", sa.Numeric(precision=5, scale=2), nullable=True),
    )
    op.add_column(
        "parametros_comerciales",
        sa.Column("descuento_ag_usd", sa.Numeric(precision=8, scale=2), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("liquidaciones_lotes", "valor_ag_usd")
    op.drop_column("liquidaciones_lotes", "spot_ag_snapshot")
    op.drop_column("liquidaciones_lotes", "ley_ag_gr_tm_snapshot")
    op.drop_column("parametros_comerciales", "umbral_ag_oz_tc")
    op.drop_column("parametros_comerciales", "rec_ag_pct")
    op.drop_column("parametros_comerciales", "descuento_ag_usd")
