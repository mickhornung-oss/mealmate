"""add source and seed metadata fields

Revision ID: 20260303_0003
Revises: 20260303_0002
Create Date: 2026-03-03 15:20:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20260303_0003"
down_revision: Union[str, None] = "20260303_0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("recipes", sa.Column("source", sa.String(length=50), nullable=False, server_default="user"))
    op.add_column("recipes", sa.Column("source_uuid", sa.String(length=120), nullable=True))
    op.add_column("recipes", sa.Column("source_url", sa.String(length=1024), nullable=True))
    op.add_column("recipes", sa.Column("source_image_url", sa.String(length=1024), nullable=True))
    op.add_column("recipes", sa.Column("servings_text", sa.String(length=120), nullable=True))
    op.add_column("recipes", sa.Column("total_time_minutes", sa.Integer(), nullable=True))
    op.create_index("ix_recipes_source", "recipes", ["source"], unique=False)
    op.create_index("ix_recipes_source_uuid", "recipes", ["source_uuid"], unique=True)
    op.create_table(
        "app_meta",
        sa.Column("key", sa.String(length=120), primary_key=True),
        sa.Column("value", sa.Text(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("app_meta")
    op.drop_index("ix_recipes_source_uuid", table_name="recipes")
    op.drop_index("ix_recipes_source", table_name="recipes")
    op.drop_column("recipes", "total_time_minutes")
    op.drop_column("recipes", "servings_text")
    op.drop_column("recipes", "source_image_url")
    op.drop_column("recipes", "source_url")
    op.drop_column("recipes", "source_uuid")
    op.drop_column("recipes", "source")
