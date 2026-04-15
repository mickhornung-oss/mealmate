"""add canonical recipe categories and mapping table

Revision ID: 20260304_0010
Revises: 20260303_0009
Create Date: 2026-03-04 09:30:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20260304_0010"
down_revision: Union[str, None] = "20260303_0009"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("recipes", sa.Column("canonical_category", sa.String(length=60), nullable=True))
    op.create_index("ix_recipes_canonical_category", "recipes", ["canonical_category"], unique=False)

    op.create_table(
        "category_mappings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("pattern", sa.String(length=120), nullable=False),
        sa.Column("canonical_category", sa.String(length=60), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False, server_default="100"),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_category_mappings_pattern", "category_mappings", ["pattern"], unique=False)
    op.create_index("ix_category_mappings_canonical_category", "category_mappings", ["canonical_category"], unique=False)
    op.create_index("ix_category_mappings_priority", "category_mappings", ["priority"], unique=False)
    op.create_index("ix_category_mappings_enabled", "category_mappings", ["enabled"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_category_mappings_enabled", table_name="category_mappings")
    op.drop_index("ix_category_mappings_priority", table_name="category_mappings")
    op.drop_index("ix_category_mappings_canonical_category", table_name="category_mappings")
    op.drop_index("ix_category_mappings_pattern", table_name="category_mappings")
    op.drop_table("category_mappings")

    op.drop_index("ix_recipes_canonical_category", table_name="recipes")
    op.drop_column("recipes", "canonical_category")
