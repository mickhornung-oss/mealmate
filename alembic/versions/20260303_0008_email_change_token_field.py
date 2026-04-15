"""add email change data to password reset tokens

Revision ID: 20260303_0008
Revises: 20260303_0007
Create Date: 2026-03-03 21:20:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20260303_0008"
down_revision: Union[str, None] = "20260303_0007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("password_reset_tokens") as batch:
        batch.add_column(sa.Column("new_email_normalized", sa.String(length=255), nullable=True))
        batch.create_index("ix_password_reset_tokens_new_email_normalized", ["new_email_normalized"], unique=False)


def downgrade() -> None:
    with op.batch_alter_table("password_reset_tokens") as batch:
        batch.drop_index("ix_password_reset_tokens_new_email_normalized")
        batch.drop_column("new_email_normalized")
