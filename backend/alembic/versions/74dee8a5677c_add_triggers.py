"""add triggers

Revision ID: 74dee8a5677c
Revises: 12dfbf9348b0
Create Date: 2026-02-25 15:13:52.181435

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "74dee8a5677c"
down_revision: str | Sequence[str] | None = "12dfbf9348b0"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ── Trigger 1: Dirimencia ─────────────────────────────────────────────────
    op.execute("""
        CREATE OR REPLACE FUNCTION fn_dirimencia_flag()
        RETURNS TRIGGER AS $$
        BEGIN
            IF NEW.tipo_analisis = 'dirimencia' THEN
                UPDATE lotes SET dirimencia = TRUE WHERE id = NEW.lote_id;
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;

        CREATE TRIGGER trg_dirimencia_flag
        AFTER INSERT ON analisis_ley
        FOR EACH ROW
        EXECUTE FUNCTION fn_dirimencia_flag();
    """)

    # ── Trigger 2: Una sola campaña ACTIVA ───────────────────────────────────
    op.execute("""
        CREATE OR REPLACE FUNCTION fn_validar_campana_activa()
        RETURNS TRIGGER AS $$
        BEGIN
            IF NEW.estado = 'ACTIVA' THEN
                IF EXISTS (
                    SELECT 1 FROM campanas
                    WHERE estado = 'ACTIVA'
                      AND id != COALESCE(NEW.id, -1)
                ) THEN
                    RAISE EXCEPTION 'Ya existe una campaña ACTIVA. Ciérrala antes de crear una nueva.';
                END IF;
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;

        CREATE TRIGGER trg_validar_campana_activa
        BEFORE INSERT OR UPDATE ON campanas
        FOR EACH ROW
        EXECUTE FUNCTION fn_validar_campana_activa();
    """)

    # ── Trigger 3: Bloquear eliminación de lotes PAGADOS ─────────────────────
    op.execute("""
        CREATE OR REPLACE FUNCTION fn_bloquear_eliminacion_pagado()
        RETURNS TRIGGER AS $$
        BEGIN
            IF NEW.eliminado = TRUE AND OLD.estado = 'PAGADO' THEN
                RAISE EXCEPTION 'No se puede eliminar un lote en estado PAGADO (IP: %)', OLD.ip;
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;

        CREATE TRIGGER trg_bloquear_eliminacion_pagado
        BEFORE UPDATE ON lotes
        FOR EACH ROW
        EXECUTE FUNCTION fn_bloquear_eliminacion_pagado();
    """)

    # ── Trigger 4: Habilitación automática para ruma ──────────────────────────
    op.execute("""
        CREATE OR REPLACE FUNCTION fn_habilitar_lote_para_ruma()
        RETURNS TRIGGER AS $$
        BEGIN
            IF NEW.estado IN ('FACTURADO', 'PAGADO') AND NOT NEW.habilitado_ruma THEN
                NEW.habilitado_ruma := TRUE;
                NEW.fecha_habilitacion := NOW();
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;

        CREATE TRIGGER trg_habilitar_lote_para_ruma
        BEFORE UPDATE ON lotes
        FOR EACH ROW
        EXECUTE FUNCTION fn_habilitar_lote_para_ruma();
    """)


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_dirimencia_descarta_otros ON analisis_ley")
    op.execute("DROP FUNCTION IF EXISTS fn_dirimencia_descarta_otros")
    op.execute("DROP TRIGGER IF EXISTS trg_validar_campana_activa ON campanas")
    op.execute("DROP FUNCTION IF EXISTS fn_validar_campana_activa")
    op.execute("DROP TRIGGER IF EXISTS trg_bloquear_eliminacion_pagado ON lotes")
    op.execute("DROP FUNCTION IF EXISTS fn_bloquear_eliminacion_pagado")
    op.execute("DROP TRIGGER IF EXISTS trg_habilitar_lote_para_ruma ON lotes")
    op.execute("DROP FUNCTION IF EXISTS fn_habilitar_lote_para_ruma")
