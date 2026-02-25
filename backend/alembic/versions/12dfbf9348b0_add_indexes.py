"""add indexes

Revision ID: 12dfbf9348b0
Revises: 78d0c0266868
Create Date: 2026-02-25 15:12:51.439898

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "12dfbf9348b0"
down_revision: str | Sequence[str] | None = "78d0c0266868"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Lotes
    op.create_index("idx_lotes_ip", "lotes", ["ip"])
    op.create_index("idx_lotes_estado", "lotes", ["estado"])
    op.create_index("idx_lotes_ruma", "lotes", ["ruma_id"])
    op.create_index("idx_lotes_eliminado", "lotes", ["eliminado"])
    op.create_index("idx_lotes_volado", "lotes", ["volado"])

    # Análisis
    op.create_index("idx_analisis_ley_lote", "analisis_ley", ["lote_id"])
    op.create_index("idx_analisis_ley_tipo", "analisis_ley", ["tipo_analisis"])
    op.create_index("idx_analisis_ley_vigente", "analisis_ley", ["vigente"])
    op.create_index("idx_analisis_rec_lote", "analisis_recuperacion", ["lote_id"])
    op.create_index("idx_analisis_rec_vigente", "analisis_recuperacion", ["vigente"])

    # Muestreos
    op.create_index("idx_muestreos_lote", "muestreos", ["lote_id"])

    # Sesiones y relaciones comerciales
    op.create_index("idx_sesiones_provacop", "sesiones_descarga", ["provacop_id"])
    op.create_index("idx_sesiones_estado", "sesiones_descarga", ["estado"])
    op.create_index("idx_liquidaciones_provacop", "liquidaciones", ["provacop_id"])
    op.create_index("idx_liquidaciones_estado", "liquidaciones", ["estado"])
    op.create_index("idx_params_acopiador", "parametros_comerciales", ["acopiador_id"])

    # Campañas y rumas
    op.create_index("idx_campanas_estado", "campanas", ["estado"])
    op.create_index("idx_rumas_estado", "rumas", ["estado"])

    # Tokens revocados
    op.create_index("idx_tokens_jti", "tokens_revocados", ["jti"])
    op.create_index("idx_tokens_expira", "tokens_revocados", ["expira_en"])


def downgrade() -> None:
    op.drop_index("idx_lotes_ip")
    op.drop_index("idx_lotes_estado")
    op.drop_index("idx_lotes_ruma")
    op.drop_index("idx_lotes_eliminado")
    op.drop_index("idx_lotes_volado")
    op.drop_index("idx_analisis_ley_lote")
    op.drop_index("idx_analisis_ley_tipo")
    op.drop_index("idx_analisis_ley_vigente")
    op.drop_index("idx_analisis_rec_lote")
    op.drop_index("idx_analisis_rec_vigente")
    op.drop_index("idx_muestreos_lote")
    op.drop_index("idx_sesiones_provacop")
    op.drop_index("idx_sesiones_estado")
    op.drop_index("idx_liquidaciones_provacop")
    op.drop_index("idx_liquidaciones_estado")
    op.drop_index("idx_params_acopiador")
    op.drop_index("idx_campanas_estado")
    op.drop_index("idx_rumas_estado")
    op.drop_index("idx_tokens_jti")
    op.drop_index("idx_tokens_expira")
