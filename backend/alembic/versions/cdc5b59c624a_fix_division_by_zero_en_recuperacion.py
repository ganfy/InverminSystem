"""Fix division by zero en recuperacion

Revision ID: cdc5b59c624a
Revises: c3d4e5f6a7b8
Create Date: 2026-06-25 10:33:08.899745

"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "cdc5b59c624a"
down_revision: str | Sequence[str] | None = "c3d4e5f6a7b8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("UPDATE analisis_recuperacion SET ley_cabeza = NULL WHERE ley_cabeza = 0;")
    # SQL Server computed column syntax: ALTER TABLE t ADD col AS (expr) PERSISTED
    op.execute("ALTER TABLE analisis_recuperacion DROP COLUMN recuperacion;")
    op.execute(
        "ALTER TABLE analisis_recuperacion ADD recuperacion AS ("
        "CASE "
        "WHEN ley_cabeza IS NOT NULL AND ley_cola IS NOT NULL AND ley_cabeza > 0 "
        "THEN CAST(((ley_cabeza - ley_cola) * 100.0) / NULLIF(ley_cabeza, 0) AS NUMERIC(5, 2)) "
        "ELSE NULL END) PERSISTED"
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("ALTER TABLE analisis_recuperacion DROP COLUMN recuperacion;")
    op.execute(
        "ALTER TABLE analisis_recuperacion ADD recuperacion AS ("
        "CASE "
        "WHEN ley_cabeza IS NOT NULL AND ley_cola IS NOT NULL AND ley_cabeza > 0 "
        "THEN CAST(((ley_cabeza - ley_cola) * 100.0) / ley_cabeza AS NUMERIC(5, 2)) "
        "ELSE NULL END) PERSISTED"
    )
