"""add_ag_reconocimiento_fields

Revision ID: 2f6d163ec46b
Revises: 90540774830c
Create Date: 2026-05-21 16:22:44.960931

"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2f6d163ec46b"
down_revision: str | Sequence[str] | None = "90540774830c"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ── analisis_detalle ─────────────────────────────────────────────────────
    # mineral_mg: señal cruda en mg.
    # Para Newmont: Au (mg) de cada muestra.
    # Para Reconocimiento: Au1 (mg) en fila RECO origen=AU1,
    #                      Au2 (mg) en fila RECO origen=AU2,
    #                      Au+Ag (mg) en fila RECO origen=AU_AG.
    op.add_column(
        "analisis_detalle",
        sa.Column("mineral_mg", sa.Numeric(precision=10, scale=4), nullable=True),
    )

    # ── analisis_recuperacion ────────────────────────────────────────────────
    # ley_cola_ag_gr_tm: promedio de leyes Ag de las muestras AU_AG del reconocimiento.
    op.add_column(
        "analisis_recuperacion",
        sa.Column("ley_cola_ag_gr_tm", sa.Numeric(precision=10, scale=4), nullable=True),
    )
    # solucion_ag_g_m3: concentración Ag en solución (g/m³).
    # NOTA: ley_liquido (ya existente) = solución Au (g/m³ o Oz/TC según lab).
    op.add_column(
        "analisis_recuperacion",
        sa.Column("solucion_ag_g_m3", sa.Numeric(precision=10, scale=4), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("analisis_recuperacion", "solucion_ag_g_m3")
    op.drop_column("analisis_recuperacion", "ley_cola_ag_gr_tm")
    op.drop_column("analisis_detalle", "mineral_mg")
