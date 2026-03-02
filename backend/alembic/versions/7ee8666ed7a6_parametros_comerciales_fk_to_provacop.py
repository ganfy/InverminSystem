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
    # Limpiar datos de prueba primero
    op.execute("DELETE FROM parametros_comerciales")

    # Quitar FK y columna actual
    op.drop_constraint(
        "parametros_comerciales_acopiador_id_fkey", "parametros_comerciales", type_="foreignkey"
    )
    op.drop_constraint(
        "parametros_comerciales_acopiador_id_key", "parametros_comerciales", type_="unique"
    )
    op.drop_column("parametros_comerciales", "acopiador_id")

    # Agregar nueva columna y FK
    op.add_column("parametros_comerciales", sa.Column("provacop_id", sa.Integer, nullable=False))
    op.create_foreign_key(
        "parametros_comerciales_provacop_id_fkey",
        "parametros_comerciales",
        "proveedor_acopiador",
        ["provacop_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_unique_constraint(
        "parametros_comerciales_provacop_id_key", "parametros_comerciales", ["provacop_id"]
    )


def downgrade() -> None:
    op.drop_constraint(
        "parametros_comerciales_provacop_id_key", "parametros_comerciales", type_="unique"
    )
    op.drop_constraint(
        "parametros_comerciales_provacop_id_fkey", "parametros_comerciales", type_="foreignkey"
    )
    op.drop_column("parametros_comerciales", "provacop_id")

    op.add_column("parametros_comerciales", sa.Column("acopiador_id", sa.Integer, nullable=False))
    op.create_foreign_key(
        "parametros_comerciales_acopiador_id_fkey",
        "parametros_comerciales",
        "entidades",
        ["acopiador_id"],
        ["id"],
        ondelete="NO ACTION",
    )
    op.create_unique_constraint(
        "parametros_comerciales_acopiador_id_key", "parametros_comerciales", ["acopiador_id"]
    )
