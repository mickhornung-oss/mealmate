"""add recipe is_published flag for moderation-safe visibility

Revision ID: 20260303_0006
Revises: 20260303_0005
Create Date: 2026-03-03 19:05:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20260303_0006"
down_revision: Union[str, None] = "20260303_0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "recipes",
        sa.Column("is_published", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.create_index("ix_recipes_is_published", "recipes", ["is_published"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_recipes_is_published", table_name="recipes")
    op.drop_column("recipes", "is_published")
