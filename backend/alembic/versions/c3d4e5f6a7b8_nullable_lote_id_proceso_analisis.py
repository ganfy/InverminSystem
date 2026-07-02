"""nullable_lote_id_proceso_analisis

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a1
Create Date: 2026-06-23 00:00:00.000000

Permite análisis de Proceso: muestras sin lote de origen en el sistema.
Cambios:
  - mapeo_cip.lote_id: NOT NULL → nullable
  - mapeo_cip.codigo_cip: varchar(20) → varchar(50) para códigos libres
  - analisis_ley.lote_id: NOT NULL → nullable
  - analisis_recuperacion.lote_id: NOT NULL → nullable
  - Actualiza check constraint tipo_muestra para incluir 'Proceso'
  - Actualiza check constraint cip en analisis_ley y analisis_recuperacion
    para aceptar hasta 50 chars
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c3d4e5f6a7b8"
down_revision: str | Sequence[str] | None = "b2c3d4e5f6a1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Make lote_id nullable to support Proceso analysis records."""

    # ── Drop dependent constraints dynamically (FKs and Unique) ──────────────
    op.execute("""
    DECLARE @sql NVARCHAR(MAX) = N'';
    
    -- Drop FKs referencing mapeo_cip
    SELECT @sql += N'ALTER TABLE ' + QUOTENAME(OBJECT_NAME(parent_object_id)) + N' DROP CONSTRAINT ' + QUOTENAME(name) + N'; '
    FROM sys.foreign_keys
    WHERE referenced_object_id = OBJECT_ID('mapeo_cip');
    
    -- Drop Unique Constraint on mapeo_cip.codigo_cip
    SELECT @sql += N'ALTER TABLE mapeo_cip DROP CONSTRAINT ' + QUOTENAME(name) + N'; '
    FROM sys.key_constraints
    WHERE parent_object_id = OBJECT_ID('mapeo_cip') AND type = 'UQ';
    
    -- Drop unique index if created as index instead of constraint
    SELECT @sql += N'DROP INDEX ' + QUOTENAME(name) + N' ON mapeo_cip; '
    FROM sys.indexes
    WHERE object_id = OBJECT_ID('mapeo_cip') AND is_unique = 1 AND is_primary_key = 0 AND is_unique_constraint = 0 AND name IS NOT NULL;

    IF @sql <> N'' EXEC sp_executesql @sql;
    """)

    # ── mapeo_cip: lote_id nullable + codigo_cip wider ───────────────────────
    op.alter_column(
        "mapeo_cip",
        "lote_id",
        existing_type=sa.Integer(),
        nullable=True,
        comment="nullable para tipo Proceso (sin lote de origen)",
    )
    op.alter_column(
        "mapeo_cip",
        "codigo_cip",
        existing_type=sa.String(20),
        type_=sa.String(50),
        existing_nullable=False,
        comment="hasta 50 chars para códigos libres de proceso",
    )

    # ── analisis_ley: lote_id nullable ───────────────────────────────────────
    op.alter_column(
        "analisis_ley",
        "lote_id",
        existing_type=sa.Integer(),
        nullable=True,
        comment="nullable para análisis de Proceso (sin lote)",
    )
    # cip FK también se amplía a String(50) para coincidir con mapeo_cip
    op.alter_column(
        "analisis_ley",
        "cip",
        existing_type=sa.String(20),
        type_=sa.String(50),
        existing_nullable=True,
    )

    # ── analisis_recuperacion: lote_id nullable ───────────────────────────────
    op.alter_column(
        "analisis_recuperacion",
        "lote_id",
        existing_type=sa.Integer(),
        nullable=True,
        comment="nullable para análisis de Proceso (sin lote)",
    )
    op.alter_column(
        "analisis_recuperacion",
        "cip",
        existing_type=sa.String(20),
        type_=sa.String(50),
        existing_nullable=True,
    )

    # ── pruebas_metalurgicas: cip ampliado a 50 ─────────────────────────────
    # Also need to alter 'cip' in 'pruebas_metalurgicas' to 50
    op.alter_column(
        "pruebas_metalurgicas",
        "cip",
        existing_type=sa.String(20),
        type_=sa.String(50),
        existing_nullable=True,
    )

    # ── Recreate Constraints ─────────────────────────────────────────────────
    op.create_unique_constraint("uq_mapeo_cip_codigo_cip", "mapeo_cip", ["codigo_cip"])
    op.create_foreign_key(
        "fk_analisis_ley_cip", "analisis_ley", "mapeo_cip", ["cip"], ["codigo_cip"]
    )
    op.create_foreign_key(
        "fk_analisis_recuperacion_cip",
        "analisis_recuperacion",
        "mapeo_cip",
        ["cip"],
        ["codigo_cip"],
    )
    op.create_foreign_key(
        "fk_pruebas_metalurgicas_cip", "pruebas_metalurgicas", "mapeo_cip", ["cip"], ["codigo_cip"]
    )

    # ── Actualizar check constraint tipo_muestra en mapeo_cip ────────────────
    # Eliminar constraint anterior e insertar uno nuevo que incluye 'Proceso'
    try:
        op.drop_constraint("ck_mapeo_cip_tipo_muestra", "mapeo_cip", type_="check")
    except Exception:
        pass  # puede no existir en algunos entornos

    op.create_check_constraint(
        "ck_mapeo_cip_tipo_muestra",
        "mapeo_cip",
        "tipo_muestra IN ('Laboratorio', 'RecuperacionInterno', 'RecuperacionExterno', 'Proceso')",
    )


def downgrade() -> None:
    """Revert nullable changes (only if no Proceso records exist)."""
    op.drop_constraint("ck_mapeo_cip_tipo_muestra", "mapeo_cip", type_="check")
    op.create_check_constraint(
        "ck_mapeo_cip_tipo_muestra",
        "mapeo_cip",
        "tipo_muestra IN ('Laboratorio', 'RecuperacionInterno', 'RecuperacionExterno')",
    )

    op.alter_column(
        "analisis_recuperacion",
        "cip",
        existing_type=sa.String(50),
        type_=sa.String(20),
        existing_nullable=True,
    )
    op.alter_column("analisis_recuperacion", "lote_id", existing_type=sa.Integer(), nullable=False)
    op.alter_column(
        "analisis_ley",
        "cip",
        existing_type=sa.String(50),
        type_=sa.String(20),
        existing_nullable=True,
    )
    op.alter_column("analisis_ley", "lote_id", existing_type=sa.Integer(), nullable=False)
    op.alter_column(
        "mapeo_cip",
        "codigo_cip",
        existing_type=sa.String(50),
        type_=sa.String(20),
        existing_nullable=False,
    )
    op.alter_column("mapeo_cip", "lote_id", existing_type=sa.Integer(), nullable=False)
