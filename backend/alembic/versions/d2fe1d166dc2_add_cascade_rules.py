"""add cascade rules

Revision ID: d2fe1d166dc2
Revises: 88e8ea610813
Create Date: 2026-02-25 17:39:45.190129

"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d2fe1d166dc2"
down_revision: str | Sequence[str] | None = "88e8ea610813"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    conn = op.get_bind()
    insp = sa.inspect(conn)
    is_mssql = conn.dialect.name == "mssql"

    # Función mágica para borrar una FK sin importar su nombre (ideal para SQL Server)
    def drop_fk(table_name, column_name):
        for fk in insp.get_foreign_keys(table_name):
            if column_name in fk["constrained_columns"]:
                op.drop_constraint(fk["name"], table_name, type_="foreignkey")
                return

    # =========================================================================
    # CASCADE DELETE
    # =========================================================================
    drop_fk("lotes", "sesion_id")
    op.create_foreign_key(
        "fk_lotes_sesion", "lotes", "sesiones_descarga", ["sesion_id"], ["id"], ondelete="CASCADE"
    )

    drop_fk("pesajes", "lote_id")
    op.create_foreign_key(
        "fk_pesajes_lote", "pesajes", "lotes", ["lote_id"], ["id"], ondelete="CASCADE"
    )

    drop_fk("muestreos", "lote_id")
    op.create_foreign_key(
        "fk_muestreos_lote", "muestreos", "lotes", ["lote_id"], ["id"], ondelete="CASCADE"
    )

    drop_fk("mapeo_cip", "lote_id")
    op.create_foreign_key(
        "fk_mapeocip_lote", "mapeo_cip", "lotes", ["lote_id"], ["id"], ondelete="CASCADE"
    )

    drop_fk("analisis_ley", "lote_id")
    op.create_foreign_key(
        "fk_aley_lote", "analisis_ley", "lotes", ["lote_id"], ["id"], ondelete="CASCADE"
    )

    drop_fk("analisis_recuperacion", "lote_id")
    op.create_foreign_key(
        "fk_arec_lote", "analisis_recuperacion", "lotes", ["lote_id"], ["id"], ondelete="CASCADE"
    )

    drop_fk("analisis_detalle", "analisis_id")
    op.create_foreign_key(
        "fk_adetalle_aley",
        "analisis_detalle",
        "analisis_ley",
        ["analisis_id"],
        ["id"],
        ondelete="CASCADE",
    )

    # Evitar error de "Multiple cascade paths" en SQL Server
    if not is_mssql:
        drop_fk("analisis_detalle", "recuperacion_id")
        op.create_foreign_key(
            "fk_adetalle_arec",
            "analisis_detalle",
            "analisis_recuperacion",
            ["recuperacion_id"],
            ["id"],
            ondelete="CASCADE",
        )

    drop_fk("liquidaciones_lotes", "liquidacion_id")
    op.create_foreign_key(
        "fk_liqlotes_liq",
        "liquidaciones_lotes",
        "liquidaciones",
        ["liquidacion_id"],
        ["id"],
        ondelete="CASCADE",
    )

    drop_fk("rumas_campanas", "id_ruma")
    op.create_foreign_key(
        "fk_rumcamp_ruma", "rumas_campanas", "rumas", ["id_ruma"], ["id"], ondelete="CASCADE"
    )

    drop_fk("rumas_campanas", "id_campana")
    op.create_foreign_key(
        "fk_rumcamp_camp", "rumas_campanas", "campanas", ["id_campana"], ["id"], ondelete="CASCADE"
    )

    # =========================================================================
    # SET NULL
    # =========================================================================
    drop_fk("lotes", "ruma_id")
    op.create_foreign_key(
        "fk_lotes_ruma", "lotes", "rumas", ["ruma_id"], ["id"], ondelete="SET NULL"
    )

    drop_fk("mapeo_cip", "ruma_id")
    op.create_foreign_key(
        "fk_mapeocip_ruma", "mapeo_cip", "rumas", ["ruma_id"], ["id"], ondelete="SET NULL"
    )

    # Evitamos re-aplicar SET NULL a auditoría en MSSQL (causa error 1785 de múltiples rutas).
    if not is_mssql:
        _set_null_fk = [
            ("lotes", "habilitado_por"),
            ("lotes", "estado_modificado_por"),
            ("lotes", "eliminado_por"),
            ("analisis_ley", "descartado_por"),
            ("analisis_recuperacion", "descartado_por"),
            ("liquidaciones", "cerrado_por"),
            ("campanas", "gerencia_id"),
        ]
        for i, (table, column) in enumerate(_set_null_fk):
            drop_fk(table, column)
            op.create_foreign_key(
                f"fk_setnull_{i}", table, "usuarios", [column], ["id"], ondelete="SET NULL"
            )

        _audit_tables = [
            "analisis_ley",
            "analisis_recuperacion",
            "campanas",
            "configuraciones",
            "entidades",
            "entidades_roles",
            "liquidaciones",
            "liquidaciones_lotes",
            "lotes",
            "muestreos",
            "parametros_comerciales",
            "permisos",
            "pruebas_metalurgicas",
            "rumas",
            "sesiones_descarga",
        ]
        for i, table in enumerate(_audit_tables):
            drop_fk(table, "creado_por")
            op.create_foreign_key(
                f"fk_audit_c_{i}", table, "usuarios", ["creado_por"], ["id"], ondelete="SET NULL"
            )

            drop_fk(table, "modificado_por")
            op.create_foreign_key(
                f"fk_audit_m_{i}",
                table,
                "usuarios",
                ["modificado_por"],
                ["id"],
                ondelete="SET NULL",
            )

        drop_fk("usuarios", "creado_por")
        op.create_foreign_key(
            "fk_usr_crea", "usuarios", "usuarios", ["creado_por"], ["id"], ondelete="SET NULL"
        )

        drop_fk("usuarios", "modificado_por")
        op.create_foreign_key(
            "fk_usr_mod", "usuarios", "usuarios", ["modificado_por"], ["id"], ondelete="SET NULL"
        )


def downgrade() -> None:
    pass
