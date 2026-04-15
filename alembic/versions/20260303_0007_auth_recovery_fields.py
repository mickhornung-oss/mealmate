"""add auth recovery and user uid fields

Revision ID: 20260303_0007
Revises: 20260303_0006
Create Date: 2026-03-03 20:35:00
"""

from typing import Sequence, Union
from uuid import uuid4

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20260303_0007"
down_revision: Union[str, None] = "20260303_0006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _backfill_user_uid() -> None:
    bind = op.get_bind()
    users_table = sa.table(
        "users",
        sa.column("id", sa.Integer()),
        sa.column("user_uid", sa.String(length=36)),
    )
    rows = bind.execute(sa.select(users_table.c.id).where(users_table.c.user_uid.is_(None))).fetchall()
    for row in rows:
        bind.execute(
            users_table.update().where(users_table.c.id == row.id).values(user_uid=str(uuid4())),
        )


def upgrade() -> None:
    with op.batch_alter_table("users") as batch:
        batch.add_column(sa.Column("user_uid", sa.String(length=36), nullable=True))
        batch.add_column(sa.Column("username", sa.String(length=30), nullable=True))
        batch.add_column(sa.Column("username_normalized", sa.String(length=30), nullable=True))
        batch.add_column(sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True))
        batch.add_column(sa.Column("last_login_ip", sa.String(length=64), nullable=True))
        batch.add_column(sa.Column("last_login_user_agent", sa.String(length=200), nullable=True))

    _backfill_user_uid()

    with op.batch_alter_table("users") as batch:
        batch.alter_column("user_uid", existing_type=sa.String(length=36), nullable=False)
        batch.create_index("ix_users_user_uid", ["user_uid"], unique=True)
        batch.create_index("ix_users_username", ["username"], unique=True)
        batch.create_index("ix_users_username_normalized", ["username_normalized"], unique=True)

    op.create_table(
        "password_reset_tokens",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_ip", sa.String(length=64), nullable=True),
        sa.Column("created_user_agent", sa.String(length=200), nullable=True),
        sa.Column("purpose", sa.String(length=50), nullable=False, server_default="password_reset"),
    )
    op.create_index("ix_password_reset_tokens_user_id", "password_reset_tokens", ["user_id"], unique=False)
    op.create_index("ix_password_reset_tokens_token_hash", "password_reset_tokens", ["token_hash"], unique=False)
    op.create_index("ix_password_reset_tokens_expires_at", "password_reset_tokens", ["expires_at"], unique=False)
    op.create_index("ix_password_reset_tokens_used_at", "password_reset_tokens", ["used_at"], unique=False)
    op.create_index("ix_password_reset_tokens_purpose", "password_reset_tokens", ["purpose"], unique=False)

    op.create_table(
        "security_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("event_type", sa.String(length=80), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ip", sa.String(length=64), nullable=True),
        sa.Column("user_agent", sa.String(length=200), nullable=True),
        sa.Column("details", sa.String(length=300), nullable=True),
    )
    op.create_index("ix_security_events_user_id", "security_events", ["user_id"], unique=False)
    op.create_index("ix_security_events_event_type", "security_events", ["event_type"], unique=False)
    op.create_index("ix_security_events_created_at", "security_events", ["created_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_security_events_created_at", table_name="security_events")
    op.drop_index("ix_security_events_event_type", table_name="security_events")
    op.drop_index("ix_security_events_user_id", table_name="security_events")
    op.drop_table("security_events")

    op.drop_index("ix_password_reset_tokens_purpose", table_name="password_reset_tokens")
    op.drop_index("ix_password_reset_tokens_used_at", table_name="password_reset_tokens")
    op.drop_index("ix_password_reset_tokens_expires_at", table_name="password_reset_tokens")
    op.drop_index("ix_password_reset_tokens_token_hash", table_name="password_reset_tokens")
    op.drop_index("ix_password_reset_tokens_user_id", table_name="password_reset_tokens")
    op.drop_table("password_reset_tokens")

    with op.batch_alter_table("users") as batch:
        batch.drop_index("ix_users_username_normalized")
        batch.drop_index("ix_users_username")
        batch.drop_index("ix_users_user_uid")
        batch.drop_column("last_login_user_agent")
        batch.drop_column("last_login_ip")
        batch.drop_column("last_login_at")
        batch.drop_column("username_normalized")
        batch.drop_column("username")
        batch.drop_column("user_uid")
