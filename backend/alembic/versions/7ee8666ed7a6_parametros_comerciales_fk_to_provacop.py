"""parametros_comerciales_fk_to_provacop

Revision ID: 7ee8666ed7a6
Revises: fb89c75e12ae
Create Date: 2026-02-27 12:53:22.192567

"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "7ee8666ed7a6"
down_revision: str | Sequence[str] | None = "fb89c75e12ae"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    conn = op.get_bind()
    insp = sa.inspect(conn)

    def drop_fk(table_name, column_name):
        for fk in insp.get_foreign_keys(table_name):
            if column_name in fk["constrained_columns"]:
                op.drop_constraint(fk["name"], table_name, type_="foreignkey")
                return

    def drop_uq(table_name, column_name):
        # 1. Intentamos el método tradicional (Funciona en Postgres)
        try:
            for uq in insp.get_unique_constraints(table_name):
                if column_name in uq["column_names"]:
                    op.drop_constraint(uq["name"], table_name, type_="unique")
                    return
        except NotImplementedError:
            pass  # SQL Server no lo soporta, pasamos al Plan B

        # 2. Plan B: Buscarlo entre los índices (Funciona en SQL Server)
        for ix in insp.get_indexes(table_name):
            if column_name in ix["column_names"] and ix["unique"]:
                try:
                    op.drop_constraint(ix["name"], table_name, type_="unique")
                except Exception:
                    op.drop_index(ix["name"], table_name)
                return

    op.execute("DELETE FROM parametros_comerciales")

    # Eliminación dinámica
    drop_fk("parametros_comerciales", "acopiador_id")
    drop_uq("parametros_comerciales", "acopiador_id")

    op.drop_column("parametros_comerciales", "acopiador_id")

    op.add_column("parametros_comerciales", sa.Column("provacop_id", sa.Integer, nullable=False))

    op.create_foreign_key(
        "fk_paramcomerciales_provacop",
        "parametros_comerciales",
        "proveedor_acopiador",
        ["provacop_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_unique_constraint(
        "uq_paramcomerciales_provacop", "parametros_comerciales", ["provacop_id"]
    )


def downgrade() -> None:
    pass
