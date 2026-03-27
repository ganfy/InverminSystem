"""add offline id to sessions

Revision ID: 31534ef17722
Revises: 377bf1835f8a
Create Date: 2026-03-16 15:21:50.024138

"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "31534ef17722"
down_revision: str | Sequence[str] | None = "377bf1835f8a"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    conn = op.get_bind()

    if conn.dialect.name != "mssql":
        op.alter_column(
            "pesajes",
            "peso_neto",
            existing_type=sa.NUMERIC(precision=10, scale=2),
            nullable=False,
            existing_server_default=sa.Computed("(peso_inicial - peso_final)", persisted=True),
        )

    op.add_column(
        "sesiones_descarga",
        sa.Column("offline_id", sa.String(length=36), nullable=True, unique=True),
    )
    op.create_index(
        "ix_sesiones_descarga_offline_id",
        "sesiones_descarga",
        ["offline_id"],
        unique=True,
    )


def downgrade() -> None:
    pass
