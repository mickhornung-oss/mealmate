"""add recipe translations table

Revision ID: 20260304_0014
Revises: 20260304_0013
Create Date: 2026-03-04 18:35:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20260304_0014"
down_revision: Union[str, None] = "20260304_0013"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "recipe_translations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("recipe_id", sa.Integer(), nullable=False),
        sa.Column("language", sa.String(length=10), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("instructions", sa.Text(), nullable=False),
        sa.Column("ingredients_text", sa.Text(), nullable=False, server_default=""),
        sa.Column("source_hash", sa.String(length=64), nullable=False),
        sa.Column("stale", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["recipe_id"], ["recipes.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("recipe_id", "language", name="uq_recipe_translations_recipe_lang"),
    )
    op.create_index("ix_recipe_translations_recipe_id", "recipe_translations", ["recipe_id"], unique=False)
    op.create_index("ix_recipe_translations_language", "recipe_translations", ["language"], unique=False)
    op.create_index("ix_recipe_translations_source_hash", "recipe_translations", ["source_hash"], unique=False)
    op.create_index("ix_recipe_translations_stale", "recipe_translations", ["stale"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_recipe_translations_stale", table_name="recipe_translations")
    op.drop_index("ix_recipe_translations_source_hash", table_name="recipe_translations")
    op.drop_index("ix_recipe_translations_language", table_name="recipe_translations")
    op.drop_index("ix_recipe_translations_recipe_id", table_name="recipe_translations")
    op.drop_table("recipe_translations")
