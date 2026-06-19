"""add_descarte_fields_to_pruebas_metalurgicas

Revision ID: a1b2c3d4e5f6
Revises: 3bd3e5785693
Create Date: 2026-06-18 01:53:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: str | Sequence[str] | None = "3bd3e5785693"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add descarte fields to pruebas_metalurgicas."""
    op.add_column(
        "pruebas_metalurgicas",
        sa.Column("descartado", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )
    op.add_column(
        "pruebas_metalurgicas",
        sa.Column("descartado_por", sa.Integer(), sa.ForeignKey("usuarios.id"), nullable=True),
    )
    op.add_column(
        "pruebas_metalurgicas",
        sa.Column("fecha_descarte", sa.DateTime(), nullable=True),
    )
    op.add_column(
        "pruebas_metalurgicas",
        sa.Column("motivo_descarte", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    """Remove descarte fields from pruebas_metalurgicas."""
    op.drop_column("pruebas_metalurgicas", "motivo_descarte")
    op.drop_column("pruebas_metalurgicas", "fecha_descarte")
    op.drop_column("pruebas_metalurgicas", "descartado_por")
    op.drop_column("pruebas_metalurgicas", "descartado")
