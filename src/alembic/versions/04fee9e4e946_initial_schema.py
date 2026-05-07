# pylint: skip-file
"""Initial schema

Revision ID: 04fee9e4e946
Revises: 
Create Date: 2026-05-01 15:48:17.560963

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '04fee9e4e946'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
               CREATE TABLE IF NOT EXISTS penguin_records
               (
                   id                INTEGER PRIMARY KEY AUTOINCREMENT,
                   created_at        TEXT NOT NULL,
                   algorithm         TEXT NOT NULL,
                   prediction        TEXT NOT NULL,
                   confidence        REAL NOT NULL,
                   island            TEXT NOT NULL,
                   sex               TEXT NOT NULL,
                   culmen_length_mm  REAL NOT NULL,
                   culmen_depth_mm   REAL NOT NULL,
                   flipper_length_mm REAL NOT NULL,
                   body_mass_g       REAL NOT NULL
               )
               """)
    op.execute("CREATE TABLE IF NOT EXISTS custom_species (name TEXT PRIMARY KEY)")
    op.execute("CREATE TABLE IF NOT EXISTS custom_islands (name TEXT PRIMARY KEY)")


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("penguin_records")
    op.drop_table("custom_species")
    op.drop_table("custom_islands")
