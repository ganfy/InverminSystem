"""add params_profit to liquidaciones_lotes

Revision ID: 38fdbf885962
Revises: e3f1a2b4c5d6
Create Date: 2026-09-04 08:48:42.769671

"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "38fdbf885962"
down_revision: str | Sequence[str] | None = "e3f1a2b4c5d6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "liquidaciones_lotes",
        sa.Column("params_profit", sa.JSON, nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("liquidaciones_lotes", "params_profit")
