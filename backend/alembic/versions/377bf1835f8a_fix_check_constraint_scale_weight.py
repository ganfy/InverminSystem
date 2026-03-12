"""fix check constraint scale weight

Revision ID: 377bf1835f8a
Revises: 16b50b26e428
Create Date: 2026-03-11 08:19:13.405914

"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "377bf1835f8a"
down_revision: str | Sequence[str] | None = "16b50b26e428"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("ALTER TABLE pesajes DROP CONSTRAINT IF EXISTS ck_pesajes_peso_final_mayor_inicial")

    op.execute("ALTER TABLE pesajes DROP COLUMN IF EXISTS peso_neto")
    op.execute(
        """
        ALTER TABLE pesajes
        ADD COLUMN peso_neto DECIMAL(10,2)
            GENERATED ALWAYS AS (peso_inicial - peso_final) STORED
        """
    )

    op.execute(
        """
        ALTER TABLE pesajes
        ADD CONSTRAINT ck_pesajes_bruto_mayor_tara
            CHECK (peso_inicial > peso_final)
        """
    )


def downgrade() -> None:
    op.execute("ALTER TABLE pesajes DROP CONSTRAINT IF EXISTS ck_pesajes_bruto_mayor_tara")
    op.execute("ALTER TABLE pesajes DROP COLUMN IF EXISTS peso_neto")
    op.execute(
        """
        ALTER TABLE pesajes
        ADD COLUMN peso_neto DECIMAL(10,2)
            GENERATED ALWAYS AS (peso_final - peso_inicial) STORED
        """
    )
    op.execute(
        """
        ALTER TABLE pesajes
        ADD CONSTRAINT ck_pesajes_peso_final_mayor_inicial
            CHECK (peso_final > peso_inicial)
        """
    )
