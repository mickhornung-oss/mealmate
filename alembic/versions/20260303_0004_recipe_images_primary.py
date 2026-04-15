"""add recipe image primary flag

Revision ID: 20260303_0004
Revises: 20260303_0003
Create Date: 2026-03-03 16:10:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20260303_0004"
down_revision: Union[str, None] = "20260303_0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("recipe_images", sa.Column("is_primary", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.execute(
        """
        UPDATE recipe_images
        SET is_primary = 1
        WHERE id IN (
          SELECT MIN(id) FROM recipe_images GROUP BY recipe_id
        )
        """
    )


def downgrade() -> None:
    op.drop_column("recipe_images", "is_primary")
