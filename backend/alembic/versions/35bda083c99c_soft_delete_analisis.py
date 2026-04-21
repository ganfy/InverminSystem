"""soft delete analisis

Revision ID: 35bda083c99c
Revises: 202546be9351
Create Date: 2026-04-20 15:18:51.022594

"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "35bda083c99c"
down_revision: str | Sequence[str] | None = "202546be9351"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    conn = op.get_bind()

    for table in ("analisis_ley", "analisis_recuperacion"):
        if conn.dialect.name == "mssql":
            op.execute(f"ALTER TABLE {table} ADD eliminado BIT NOT NULL DEFAULT 0")
            op.execute(f"ALTER TABLE {table} ADD eliminado_en DATETIME NULL")
            op.execute(f"ALTER TABLE {table} ADD eliminado_por INT NULL")
            op.execute(
                f"ALTER TABLE {table} ADD CONSTRAINT fk_{table}_elim_usr "
                f"FOREIGN KEY (eliminado_por) REFERENCES usuarios(id)"
            )
        else:
            op.add_column(
                table,
                sa.Column("eliminado", sa.Boolean(), nullable=False, server_default="false"),
            )
            op.add_column(table, sa.Column("eliminado_en", sa.DateTime(), nullable=True))
            op.add_column(
                table,
                sa.Column(
                    "eliminado_por",
                    sa.Integer(),
                    sa.ForeignKey("usuarios.id"),
                    nullable=True,
                ),
            )

    op.create_index("idx_analisis_ley_eliminado", "analisis_ley", ["eliminado"])
    op.create_index("idx_analisis_rec_eliminado", "analisis_recuperacion", ["eliminado"])


def downgrade() -> None:
    op.drop_index("idx_analisis_ley_eliminado", table_name="analisis_ley")
    op.drop_index("idx_analisis_rec_eliminado", table_name="analisis_recuperacion")

    conn = op.get_bind()
    for table in ("analisis_ley", "analisis_recuperacion"):
        if conn.dialect.name == "mssql":
            op.execute(f"ALTER TABLE {table} DROP CONSTRAINT fk_{table}_elim_usr")
            op.execute(f"ALTER TABLE {table} DROP COLUMN eliminado_por")
            op.execute(f"ALTER TABLE {table} DROP COLUMN eliminado_en")
            op.execute(f"ALTER TABLE {table} DROP COLUMN eliminado")
        else:
            op.drop_column(table, "eliminado_por")
            op.drop_column(table, "eliminado_en")
            op.drop_column(table, "eliminado")
