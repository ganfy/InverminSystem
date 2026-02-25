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
    # =========================================================================
    # CASCADE DELETE
    # =========================================================================

    # lotes → sesiones_descarga
    op.drop_constraint("lotes_sesion_id_fkey", "lotes", type_="foreignkey")
    op.create_foreign_key(
        "lotes_sesion_id_fkey",
        "lotes",
        "sesiones_descarga",
        ["sesion_id"],
        ["id"],
        ondelete="CASCADE",
    )

    # pesajes → lotes
    op.drop_constraint("pesajes_lote_id_fkey", "pesajes", type_="foreignkey")
    op.create_foreign_key(
        "pesajes_lote_id_fkey",
        "pesajes",
        "lotes",
        ["lote_id"],
        ["id"],
        ondelete="CASCADE",
    )

    # muestreos → lotes
    op.drop_constraint("muestreos_lote_id_fkey", "muestreos", type_="foreignkey")
    op.create_foreign_key(
        "muestreos_lote_id_fkey",
        "muestreos",
        "lotes",
        ["lote_id"],
        ["id"],
        ondelete="CASCADE",
    )

    # mapeo_cip → lotes
    op.drop_constraint("mapeo_cip_lote_id_fkey", "mapeo_cip", type_="foreignkey")
    op.create_foreign_key(
        "mapeo_cip_lote_id_fkey",
        "mapeo_cip",
        "lotes",
        ["lote_id"],
        ["id"],
        ondelete="CASCADE",
    )

    # analisis_ley → lotes
    op.drop_constraint("analisis_ley_lote_id_fkey", "analisis_ley", type_="foreignkey")
    op.create_foreign_key(
        "analisis_ley_lote_id_fkey",
        "analisis_ley",
        "lotes",
        ["lote_id"],
        ["id"],
        ondelete="CASCADE",
    )

    # analisis_recuperacion → lotes
    op.drop_constraint(
        "analisis_recuperacion_lote_id_fkey", "analisis_recuperacion", type_="foreignkey"
    )
    op.create_foreign_key(
        "analisis_recuperacion_lote_id_fkey",
        "analisis_recuperacion",
        "lotes",
        ["lote_id"],
        ["id"],
        ondelete="CASCADE",
    )

    # analisis_detalle → analisis_ley
    op.drop_constraint("analisis_detalle_analisis_id_fkey", "analisis_detalle", type_="foreignkey")
    op.create_foreign_key(
        "analisis_detalle_analisis_id_fkey",
        "analisis_detalle",
        "analisis_ley",
        ["analisis_id"],
        ["id"],
        ondelete="CASCADE",
    )

    # analisis_detalle → analisis_recuperacion
    op.drop_constraint(
        "analisis_detalle_recuperacion_id_fkey", "analisis_detalle", type_="foreignkey"
    )
    op.create_foreign_key(
        "analisis_detalle_recuperacion_id_fkey",
        "analisis_detalle",
        "analisis_recuperacion",
        ["recuperacion_id"],
        ["id"],
        ondelete="CASCADE",
    )

    # liquidaciones_lotes → liquidaciones
    op.drop_constraint(
        "liquidaciones_lotes_liquidacion_id_fkey", "liquidaciones_lotes", type_="foreignkey"
    )
    op.create_foreign_key(
        "liquidaciones_lotes_liquidacion_id_fkey",
        "liquidaciones_lotes",
        "liquidaciones",
        ["liquidacion_id"],
        ["id"],
        ondelete="CASCADE",
    )

    # rumas_campanas → rumas (tabla asociativa)
    op.drop_constraint("rumas_campanas_id_ruma_fkey", "rumas_campanas", type_="foreignkey")
    op.create_foreign_key(
        "rumas_campanas_id_ruma_fkey",
        "rumas_campanas",
        "rumas",
        ["id_ruma"],
        ["id"],
        ondelete="CASCADE",
    )

    # rumas_campanas → campanas (tabla asociativa)
    op.drop_constraint("rumas_campanas_id_campana_fkey", "rumas_campanas", type_="foreignkey")
    op.create_foreign_key(
        "rumas_campanas_id_campana_fkey",
        "rumas_campanas",
        "campanas",
        ["id_campana"],
        ["id"],
        ondelete="CASCADE",
    )

    # =========================================================================
    # SET NULL — el hijo sobrevive sin el padre
    # =========================================================================

    # lotes.ruma_id → rumas (lote puede existir sin ruma asignada)
    op.drop_constraint("lotes_ruma_id_fkey", "lotes", type_="foreignkey")
    op.create_foreign_key(
        "lotes_ruma_id_fkey",
        "lotes",
        "rumas",
        ["ruma_id"],
        ["id"],
        ondelete="SET NULL",
    )

    # mapeo_cip.ruma_id → rumas
    op.drop_constraint("mapeo_cip_ruma_id_fkey", "mapeo_cip", type_="foreignkey")
    op.create_foreign_key(
        "mapeo_cip_ruma_id_fkey",
        "mapeo_cip",
        "rumas",
        ["ruma_id"],
        ["id"],
        ondelete="SET NULL",
    )

    # ── FKs a usuarios: estados y decisiones de negocio opcionales ────────────
    # El lote/análisis/liquidación sobrevive si el usuario se desactiva
    _set_null_fk = [
        # (tabla, columna, constraint_name)
        ("lotes", "habilitado_por", "lotes_habilitado_por_fkey"),
        ("lotes", "estado_modificado_por", "lotes_estado_modificado_por_fkey"),
        ("lotes", "eliminado_por", "lotes_eliminado_por_fkey"),
        ("analisis_ley", "descartado_por", "analisis_ley_descartado_por_fkey"),
        ("analisis_recuperacion", "descartado_por", "analisis_recuperacion_descartado_por_fkey"),
        ("liquidaciones", "cerrado_por", "liquidaciones_cerrado_por_fkey"),
        ("campanas", "gerencia_id", "campanas_gerencia_id_fkey"),
    ]
    for table, column, constraint in _set_null_fk:
        op.drop_constraint(constraint, table, type_="foreignkey")
        op.create_foreign_key(
            constraint,
            table,
            "usuarios",
            [column],
            ["id"],
            ondelete="SET NULL",
        )

    # ── AuditMixin: creado_por / modificado_por en todas las tablas ───────────
    # Si el usuario que creó un registro se desactiva, el registro sigue existiendo
    _audit_tables = [
        ("analisis_ley", "analisis_ley_creado_por_fkey", "analisis_ley_modificado_por_fkey"),
        (
            "analisis_recuperacion",
            "analisis_recuperacion_creado_por_fkey",
            "analisis_recuperacion_modificado_por_fkey",
        ),
        ("campanas", "campanas_creado_por_fkey", "campanas_modificado_por_fkey"),
        (
            "configuraciones",
            "configuraciones_creado_por_fkey",
            "configuraciones_modificado_por_fkey",
        ),
        ("entidades", "entidades_creado_por_fkey", "entidades_modificado_por_fkey"),
        (
            "entidades_roles",
            "entidades_roles_creado_por_fkey",
            "entidades_roles_modificado_por_fkey",
        ),
        ("liquidaciones", "liquidaciones_creado_por_fkey", "liquidaciones_modificado_por_fkey"),
        (
            "liquidaciones_lotes",
            "liquidaciones_lotes_creado_por_fkey",
            "liquidaciones_lotes_modificado_por_fkey",
        ),
        ("lotes", "lotes_creado_por_fkey", "lotes_modificado_por_fkey"),
        ("muestreos", "muestreos_creado_por_fkey", "muestreos_modificado_por_fkey"),
        (
            "parametros_comerciales",
            "parametros_comerciales_creado_por_fkey",
            "parametros_comerciales_modificado_por_fkey",
        ),
        ("permisos", "permisos_creado_por_fkey", "permisos_modificado_por_fkey"),
        (
            "pruebas_metalurgicas",
            "pruebas_metalurgicas_creado_por_fkey",
            "pruebas_metalurgicas_modificado_por_fkey",
        ),
        ("rumas", "rumas_creado_por_fkey", "rumas_modificado_por_fkey"),
        (
            "sesiones_descarga",
            "sesiones_descarga_creado_por_fkey",
            "sesiones_descarga_modificado_por_fkey",
        ),
    ]
    for table, fk_creado, fk_modificado in _audit_tables:
        op.drop_constraint(fk_creado, table, type_="foreignkey")
        op.create_foreign_key(
            fk_creado,
            table,
            "usuarios",
            ["creado_por"],
            ["id"],
            ondelete="SET NULL",
        )
        op.drop_constraint(fk_modificado, table, type_="foreignkey")
        op.create_foreign_key(
            fk_modificado,
            table,
            "usuarios",
            ["modificado_por"],
            ["id"],
            ondelete="SET NULL",
        )

    # ── usuarios.creado_por / modificado_por → auto-referencia ───────────────
    op.drop_constraint("usuarios_creado_por_fkey", "usuarios", type_="foreignkey")
    op.create_foreign_key(
        "usuarios_creado_por_fkey",
        "usuarios",
        "usuarios",
        ["creado_por"],
        ["id"],
        ondelete="SET NULL",
    )
    op.drop_constraint("usuarios_modificado_por_fkey", "usuarios", type_="foreignkey")
    op.create_foreign_key(
        "usuarios_modificado_por_fkey",
        "usuarios",
        "usuarios",
        ["modificado_por"],
        ["id"],
        ondelete="SET NULL",
    )

    # =========================================================================
    # NO ACTION (dejar como está) — tablas de catálogo que nunca se borran
    # =========================================================================
    # permisos → modulos, operaciones, roles         → NO ACTION
    # entidades_roles → entidades, roles             → NO ACTION
    # proveedor_acopiador → entidades                → NO ACTION
    # sesiones_descarga → proveedor_acopiador        → NO ACTION
    # liquidaciones → proveedor_acopiador            → NO ACTION
    # parametros_comerciales → entidades             → NO ACTION
    # analisis_ley → mapeo_cip                       → NO ACTION
    # analisis_recuperacion → mapeo_cip              → NO ACTION
    # pruebas_metalurgicas → mapeo_cip               → NO ACTION
    # usuarios → roles                               → NO ACTION
    # lotes_eliminados → usuarios                    → NO ACTION
    #   (registro de auditoría forense, no debe perder el FK aunque se active SET NULL)


def downgrade() -> None:
    # Revertir a NO ACTION en todas las FKs modificadas
    # En producción no se hace downgrade de reglas de integridad,
    # pero se documenta para consistencia del historial de migraciones.
    pass
