"""add recipe title image url

Revision ID: 20260303_0002
Revises: 20260303_0001
Create Date: 2026-03-03 14:10:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20260303_0002"
down_revision: Union[str, None] = "20260303_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("recipes", sa.Column("title_image_url", sa.String(length=1024), nullable=True))


def downgrade() -> None:
    op.drop_column("recipes", "title_image_url")
