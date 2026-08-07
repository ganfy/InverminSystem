"""add_llampo_trigger

Revision ID: aed9d27ddc35
Revises: 9da9d5c0e40f
Create Date: 2026-08-07 17:37:21.000000

"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "aed9d27ddc35"
down_revision: str | None = "b5f8e3c0d942"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    conn = op.get_bind()
    if conn.dialect.name == "postgresql":
        op.execute("""
        CREATE OR REPLACE FUNCTION trg_parametros_llampo_calc()
        RETURNS TRIGGER AS $$
        DECLARE
            acopiador_nombre VARCHAR;
        BEGIN
            SELECT e.razon_social INTO acopiador_nombre
            FROM proveedor_acopiador pa
            JOIN entidades e ON pa.acopiador_id = e.id
            WHERE pa.id = NEW.provacop_id;

            IF acopiador_nombre ILIKE '%RONALD MIRANDA%' THEN
                NEW.gasto_acopio_llampo := 50;
                NEW.gasto_consumo_llampo := 40;
            ELSE
                IF NEW.gasto_acopio IS NOT NULL THEN
                    NEW.gasto_acopio_llampo := NEW.gasto_acopio + 10;
                END IF;
                IF NEW.gasto_consumo IS NOT NULL THEN
                    NEW.gasto_consumo_llampo := NEW.gasto_consumo + 40;
                END IF;
            END IF;

            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """)
        op.execute("""
        DROP TRIGGER IF EXISTS trg_parametros_llampo ON parametros_comerciales;
        CREATE TRIGGER trg_parametros_llampo
        BEFORE INSERT OR UPDATE OF gasto_acopio, gasto_consumo, provacop_id
        ON parametros_comerciales
        FOR EACH ROW
        EXECUTE FUNCTION trg_parametros_llampo_calc();
        """)
    elif conn.dialect.name == "mssql":
        op.execute("""
        CREATE OR ALTER TRIGGER trg_parametros_llampo
        ON parametros_comerciales
        AFTER INSERT, UPDATE
        AS
        BEGIN
            SET NOCOUNT ON;

            IF UPDATE(gasto_acopio) OR UPDATE(gasto_consumo) OR UPDATE(provacop_id)
            BEGIN
                UPDATE pc
                SET 
                    gasto_acopio_llampo = CASE 
                        WHEN e.razon_social LIKE '%RONALD MIRANDA%' THEN 50
                        ELSE pc.gasto_acopio + 10
                    END,
                    gasto_consumo_llampo = CASE 
                        WHEN e.razon_social LIKE '%RONALD MIRANDA%' THEN 40
                        ELSE pc.gasto_consumo + 40
                    END
                FROM parametros_comerciales pc
                JOIN inserted i ON pc.id = i.id
                JOIN proveedor_acopiador pa ON i.provacop_id = pa.id
                JOIN entidades e ON pa.acopiador_id = e.id;
            END
        END;
        """)


def downgrade() -> None:
    conn = op.get_bind()
    if conn.dialect.name == "postgresql":
        op.execute("DROP TRIGGER IF EXISTS trg_parametros_llampo ON parametros_comerciales;")
        op.execute("DROP FUNCTION IF EXISTS trg_parametros_llampo_calc();")
    elif conn.dialect.name == "mssql":
        op.execute("DROP TRIGGER IF EXISTS trg_parametros_llampo;")
