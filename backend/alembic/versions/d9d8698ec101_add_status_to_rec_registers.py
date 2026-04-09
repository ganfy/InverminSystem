"""add status to rec registers

Revision ID: d9d8698ec101
Revises: 019e6b1b01da
Create Date: 2026-04-09 11:52:16.250542

"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d9d8698ec101"
down_revision: str | Sequence[str] | None = "019e6b1b01da"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. Migrar valor legado en mapeo_cip antes del constraint
    op.execute(
        "UPDATE mapeo_cip SET tipo_muestra = 'RecuperacionInterno' "
        "WHERE tipo_muestra = 'RECUPERACION'"
    )

    # 2. Agregar columna estado a analisis_recuperacion con default COMPLETADO
    #    (todos los registros existentes ya tienen datos completos)
    op.add_column(
        "analisis_recuperacion",
        sa.Column(
            "estado",
            sa.String(20),
            nullable=False,
            server_default="COMPLETADO",
        ),
    )

    # 3. Índice para consultas de pendientes por laboratorista
    op.create_index(
        "idx_analisis_rec_estado",
        "analisis_recuperacion",
        ["estado"],
    )

    # 4. Check constraint tipo_muestra en mapeo_cip
    op.create_check_constraint(
        "ck_mapeo_cip_tipo_muestra",
        "mapeo_cip",
        "tipo_muestra IN ('Laboratorio', 'RecuperacionInterno', 'RecuperacionExterno')",
    )

    # 5. Check constraint estado en analisis_recuperacion
    op.create_check_constraint(
        "ck_analisis_rec_estado",
        "analisis_recuperacion",
        "estado IN ('PENDIENTE', 'COMPLETADO')",
    )


def downgrade() -> None:
    op.drop_constraint("ck_analisis_rec_estado", "analisis_recuperacion", type_="check")
    op.drop_constraint("ck_mapeo_cip_tipo_muestra", "mapeo_cip", type_="check")
    op.drop_index("idx_analisis_rec_estado", table_name="analisis_recuperacion")
    op.drop_column("analisis_recuperacion", "estado")
