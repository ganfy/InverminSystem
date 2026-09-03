"""add lotes hermanos

Revision ID: e3f1a2b4c5d6
Revises: a887c3ee16c0
Create Date: 2026-09-01
"""

import sqlalchemy as sa
from alembic import op

revision = "e3f1a2b4c5d6"
down_revision = "a887c3ee16c0"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "grupos_hermanos",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("notas", sa.Text, nullable=True),
        sa.Column("creado_por", sa.Integer, sa.ForeignKey("usuarios.id"), nullable=False),
        sa.Column("creado_en", sa.DateTime, nullable=False),
    )
    op.create_table(
        "lotes_hermanos",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column(
            "grupo_id",
            sa.Integer,
            sa.ForeignKey("grupos_hermanos.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "lote_id",
            sa.Integer,
            sa.ForeignKey("lotes.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("creado_por", sa.Integer, sa.ForeignKey("usuarios.id"), nullable=False),
        sa.Column("creado_en", sa.DateTime, nullable=False),
        sa.UniqueConstraint("lote_id", name="uq_lote_un_solo_grupo"),
    )
    op.create_index("idx_lotes_hermanos_grupo_id", "lotes_hermanos", ["grupo_id"])
    op.create_index("idx_lotes_hermanos_lote_id", "lotes_hermanos", ["lote_id"])


def downgrade():
    op.drop_index("idx_lotes_hermanos_lote_id", table_name="lotes_hermanos")
    op.drop_index("idx_lotes_hermanos_grupo_id", table_name="lotes_hermanos")
    op.drop_table("lotes_hermanos")
    op.drop_table("grupos_hermanos")
