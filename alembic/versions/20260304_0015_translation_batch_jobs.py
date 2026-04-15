"""add translation batch jobs table

Revision ID: 20260304_0015
Revises: 20260304_0014
Create Date: 2026-03-04 19:10:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20260304_0015"
down_revision: Union[str, None] = "20260304_0014"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "translation_batch_jobs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("external_job_id", sa.String(length=120), nullable=False),
        sa.Column("mode", sa.String(length=20), nullable=False, server_default="missing"),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="queued"),
        sa.Column("requested_recipe_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_items", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("completed_items", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_items", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("updated_items", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("skipped_items", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("items_json", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("requested_by_admin_id", sa.Integer(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_polled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["requested_by_admin_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("external_job_id"),
    )
    op.create_index("ix_translation_batch_jobs_external_job_id", "translation_batch_jobs", ["external_job_id"], unique=True)
    op.create_index("ix_translation_batch_jobs_mode", "translation_batch_jobs", ["mode"], unique=False)
    op.create_index("ix_translation_batch_jobs_status", "translation_batch_jobs", ["status"], unique=False)
    op.create_index("ix_translation_batch_jobs_requested_by_admin_id", "translation_batch_jobs", ["requested_by_admin_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_translation_batch_jobs_requested_by_admin_id", table_name="translation_batch_jobs")
    op.drop_index("ix_translation_batch_jobs_status", table_name="translation_batch_jobs")
    op.drop_index("ix_translation_batch_jobs_mode", table_name="translation_batch_jobs")
    op.drop_index("ix_translation_batch_jobs_external_job_id", table_name="translation_batch_jobs")
    op.drop_table("translation_batch_jobs")
