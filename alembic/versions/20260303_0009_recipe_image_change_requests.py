"""add moderation tables for recipe image change requests

Revision ID: 20260303_0009
Revises: 20260303_0008
Create Date: 2026-03-03 21:05:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20260303_0009"
down_revision: Union[str, None] = "20260303_0008"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

image_change_status_enum = sa.Enum(
    "pending",
    "approved",
    "rejected",
    name="image_change_status",
    native_enum=False,
)


def upgrade() -> None:
    op.create_table(
        "recipe_image_change_requests",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("recipe_id", sa.Integer(), sa.ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("requester_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("status", image_change_status_enum, nullable=False, server_default="pending"),
        sa.Column("admin_note", sa.Text(), nullable=True),
        sa.Column("reviewed_by_admin_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(
        "ix_recipe_image_change_requests_recipe_id",
        "recipe_image_change_requests",
        ["recipe_id"],
        unique=False,
    )
    op.create_index(
        "ix_recipe_image_change_requests_requester_user_id",
        "recipe_image_change_requests",
        ["requester_user_id"],
        unique=False,
    )
    op.create_index(
        "ix_recipe_image_change_requests_status",
        "recipe_image_change_requests",
        ["status"],
        unique=False,
    )
    op.create_index(
        "ix_recipe_image_change_requests_reviewed_by_admin_id",
        "recipe_image_change_requests",
        ["reviewed_by_admin_id"],
        unique=False,
    )
    op.create_index(
        "ix_recipe_image_change_requests_created_at",
        "recipe_image_change_requests",
        ["created_at"],
        unique=False,
    )

    op.create_table(
        "recipe_image_change_files",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "request_id",
            sa.Integer(),
            sa.ForeignKey("recipe_image_change_requests.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("content_type", sa.String(length=50), nullable=False),
        sa.Column("data", sa.LargeBinary(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("request_id", name="uq_recipe_image_change_files_request"),
    )
    op.create_index("ix_recipe_image_change_files_request_id", "recipe_image_change_files", ["request_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_recipe_image_change_files_request_id", table_name="recipe_image_change_files")
    op.drop_table("recipe_image_change_files")

    op.drop_index("ix_recipe_image_change_requests_created_at", table_name="recipe_image_change_requests")
    op.drop_index("ix_recipe_image_change_requests_reviewed_by_admin_id", table_name="recipe_image_change_requests")
    op.drop_index("ix_recipe_image_change_requests_status", table_name="recipe_image_change_requests")
    op.drop_index("ix_recipe_image_change_requests_requester_user_id", table_name="recipe_image_change_requests")
    op.drop_index("ix_recipe_image_change_requests_recipe_id", table_name="recipe_image_change_requests")
    op.drop_table("recipe_image_change_requests")
