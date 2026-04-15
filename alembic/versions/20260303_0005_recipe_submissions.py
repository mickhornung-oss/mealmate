"""add recipe submissions moderation workflow tables

Revision ID: 20260303_0005
Revises: 20260303_0004
Create Date: 2026-03-03 18:30:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20260303_0005"
down_revision: Union[str, None] = "20260303_0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

submission_status_enum = sa.Enum(
    "pending",
    "approved",
    "rejected",
    name="submission_status",
    native_enum=False,
)


def upgrade() -> None:
    op.create_table(
        "recipe_submissions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("submitter_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("submitter_email", sa.String(length=255), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("category", sa.String(length=120), nullable=True),
        sa.Column("difficulty", sa.String(length=30), nullable=False, server_default="medium"),
        sa.Column("prep_time_minutes", sa.Integer(), nullable=True),
        sa.Column("servings_text", sa.String(length=120), nullable=True),
        sa.Column("instructions", sa.Text(), nullable=False),
        sa.Column("status", submission_status_enum, nullable=False, server_default="pending"),
        sa.Column("admin_note", sa.Text(), nullable=True),
        sa.Column("reviewed_by_admin_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_recipe_submissions_title", "recipe_submissions", ["title"], unique=False)
    op.create_index("ix_recipe_submissions_status", "recipe_submissions", ["status"], unique=False)
    op.create_index("ix_recipe_submissions_category", "recipe_submissions", ["category"], unique=False)
    op.create_index("ix_recipe_submissions_difficulty", "recipe_submissions", ["difficulty"], unique=False)
    op.create_index("ix_recipe_submissions_created_at", "recipe_submissions", ["created_at"], unique=False)
    op.create_index("ix_recipe_submissions_submitter_user_id", "recipe_submissions", ["submitter_user_id"], unique=False)
    op.create_index("ix_recipe_submissions_reviewed_by_admin_id", "recipe_submissions", ["reviewed_by_admin_id"], unique=False)

    op.create_table(
        "submission_ingredients",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "submission_id",
            sa.Integer(),
            sa.ForeignKey("recipe_submissions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("ingredient_name", sa.String(length=200), nullable=False),
        sa.Column("quantity_text", sa.String(length=120), nullable=False, server_default=""),
        sa.Column("grams", sa.Integer(), nullable=True),
        sa.Column("ingredient_name_normalized", sa.String(length=200), nullable=True),
    )
    op.create_index("ix_submission_ingredients_submission_id", "submission_ingredients", ["submission_id"], unique=False)
    op.create_index(
        "ix_submission_ingredients_ingredient_name_normalized",
        "submission_ingredients",
        ["ingredient_name_normalized"],
        unique=False,
    )

    op.create_table(
        "submission_images",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "submission_id",
            sa.Integer(),
            sa.ForeignKey("recipe_submissions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("content_type", sa.String(length=50), nullable=False),
        sa.Column("data", sa.LargeBinary(), nullable=False),
        sa.Column("is_primary", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_submission_images_submission_id", "submission_images", ["submission_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_submission_images_submission_id", table_name="submission_images")
    op.drop_table("submission_images")

    op.drop_index("ix_submission_ingredients_ingredient_name_normalized", table_name="submission_ingredients")
    op.drop_index("ix_submission_ingredients_submission_id", table_name="submission_ingredients")
    op.drop_table("submission_ingredients")

    op.drop_index("ix_recipe_submissions_reviewed_by_admin_id", table_name="recipe_submissions")
    op.drop_index("ix_recipe_submissions_submitter_user_id", table_name="recipe_submissions")
    op.drop_index("ix_recipe_submissions_created_at", table_name="recipe_submissions")
    op.drop_index("ix_recipe_submissions_difficulty", table_name="recipe_submissions")
    op.drop_index("ix_recipe_submissions_category", table_name="recipe_submissions")
    op.drop_index("ix_recipe_submissions_status", table_name="recipe_submissions")
    op.drop_index("ix_recipe_submissions_title", table_name="recipe_submissions")
    op.drop_table("recipe_submissions")
