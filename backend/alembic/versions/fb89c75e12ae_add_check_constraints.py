"""add check constraints

Revision ID: fb89c75e12ae
Revises: d2fe1d166dc2
Create Date: 2026-02-25 18:02:29.658437

"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
from alembic import op
from app.models.enums import (
    EstadoCampana,
    EstadoLiquidacion,
    EstadoLote,
    EstadoRuma,
    EstadoSesion,
    valores_enum,
)

# revision identifiers, used by Alembic.
revision: str = "fb89c75e12ae"
down_revision: str | Sequence[str] | None = "d2fe1d166dc2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ── Flujo operativo ───────────────────────────────────────────────────────
    op.create_check_constraint(
        "ck_lotes_estado_valido",
        "lotes",
        f"estado IN ({valores_enum(EstadoLote)})",
    )
    op.create_check_constraint(
        "ck_sesiones_estado_valido",
        "sesiones_descarga",
        f"estado IN ({valores_enum(EstadoSesion)})",
    )
    op.create_check_constraint(
        "ck_liquidaciones_estado_valido",
        "liquidaciones",
        f"estado IN ({valores_enum(EstadoLiquidacion)})",
    )
    op.create_check_constraint(
        "ck_campanas_estado_valido",
        "campanas",
        f"estado IN ({valores_enum(EstadoCampana)})",
    )
    op.create_check_constraint(
        "ck_rumas_estado_valido",
        "rumas",
        f"estado IN ({valores_enum(EstadoRuma)})",
    )

    # ── Integridad física de datos ────────────────────────────────────────────
    op.create_check_constraint(
        "ck_pesajes_peso_final_mayor_inicial",
        "pesajes",
        "peso_final > peso_inicial",
    )
    op.create_check_constraint(
        "ck_muestreos_peso_seco_menor_humedo",
        "muestreos",
        "peso_seco < peso_humedo",
    )

    # ── Valores positivos ─────────────────────────────────────────────────────
    op.create_check_constraint(
        "ck_campanas_meta_positiva",
        "campanas",
        "meta_oro_fino > 0",
    )


def downgrade() -> None:
    op.drop_constraint("ck_lotes_estado_valido", "lotes", type_="check")
    op.drop_constraint("ck_sesiones_estado_valido", "sesiones_descarga", type_="check")
    op.drop_constraint("ck_liquidaciones_estado_valido", "liquidaciones", type_="check")
    op.drop_constraint("ck_campanas_estado_valido", "campanas", type_="check")
    op.drop_constraint("ck_rumas_estado_valido", "rumas", type_="check")
    op.drop_constraint("ck_pesajes_peso_final_mayor_inicial", "pesajes", type_="check")
    op.drop_constraint("ck_muestreos_peso_seco_menor_humedo", "muestreos", type_="check")
    op.drop_constraint("ck_campanas_meta_positiva", "campanas", type_="check")
