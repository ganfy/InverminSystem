"""change_fk_parametros_comerciales

Revision ID: 77beea852a2c
Revises: 7ee8666ed7a6
Create Date: 2026-02-27 13:02:47.340145

"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "77beea852a2c"
down_revision: str | Sequence[str] | None = "7ee8666ed7a6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column(
        "analisis_detalle",
        "origen",
        existing_type=sa.INTEGER(),
        type_=sa.String(length=20),
        existing_nullable=False,
    )


def downgrade() -> None:
    pass
