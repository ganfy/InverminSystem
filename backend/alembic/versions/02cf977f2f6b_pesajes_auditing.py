"""Pesajes auditing

Revision ID: 02cf977f2f6b
Revises: 31534ef17722
Create Date: 2026-03-23 10:22:51.446948

"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "02cf977f2f6b"
down_revision: str | Sequence[str] | None = "31534ef17722"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Agregamos server_default="0" para evitar errores si la tabla ya tiene datos
    op.add_column(
        "pesajes", sa.Column("es_manual", sa.Boolean(), nullable=False, server_default="0")
    )
    op.add_column(
        "pesajes", sa.Column("justificacion_manual", sa.String(length=255), nullable=True)
    )

    # Usamos CURRENT_TIMESTAMP en lugar de now()
    op.add_column(
        "pesajes",
        sa.Column(
            "creado_en", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False
        ),
    )
    op.add_column("pesajes", sa.Column("modificado_en", sa.DateTime(), nullable=True))
    op.add_column("pesajes", sa.Column("creado_por", sa.Integer(), nullable=True))
    op.add_column("pesajes", sa.Column("modificado_por", sa.Integer(), nullable=True))

    # Nombres explícitos para las llaves foráneas
    op.create_foreign_key("fk_pesajes_aud_crea", "pesajes", "usuarios", ["creado_por"], ["id"])
    op.create_foreign_key("fk_pesajes_aud_mod", "pesajes", "usuarios", ["modificado_por"], ["id"])

    op.drop_index("ix_sesiones_descarga_offline_id", table_name="sesiones_descarga")


def downgrade() -> None:
    pass
