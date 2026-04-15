"""add scope to category mappings

Revision ID: 20260304_0013
Revises: 20260304_0012
Create Date: 2026-03-04 13:58:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20260304_0013"
down_revision: Union[str, None] = "20260304_0012"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "category_mappings",
        sa.Column("scope", sa.String(length=20), nullable=False, server_default="raw"),
    )
    op.execute(sa.text("UPDATE category_mappings SET scope = 'raw' WHERE scope IS NULL OR scope = ''"))
    op.create_index("ix_category_mappings_scope", "category_mappings", ["scope"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_category_mappings_scope", table_name="category_mappings")
    op.drop_column("category_mappings", "scope")
