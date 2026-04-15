"""add quality flag for recipe translations

Revision ID: 20260304_0016
Revises: 20260304_0015
Create Date: 2026-03-04 23:35:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20260304_0016"
down_revision: Union[str, None] = "20260304_0015"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "recipe_translations",
        sa.Column("quality_flag", sa.String(length=32), nullable=False, server_default="ok"),
    )
    op.execute("UPDATE recipe_translations SET quality_flag = 'ok' WHERE quality_flag IS NULL")
    op.create_index("ix_recipe_translations_quality_flag", "recipe_translations", ["quality_flag"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_recipe_translations_quality_flag", table_name="recipe_translations")
    op.drop_column("recipe_translations", "quality_flag")
