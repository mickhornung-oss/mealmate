"""initial schema

Revision ID: 20260303_0001
Revises: 
Create Date: 2026-03-03 13:00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20260303_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_table(
        "recipes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("instructions", sa.Text(), nullable=False),
        sa.Column("category", sa.String(length=120), nullable=False),
        sa.Column("prep_time_minutes", sa.Integer(), nullable=False),
        sa.Column("difficulty", sa.String(length=30), nullable=False),
        sa.Column("creator_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_recipes_title", "recipes", ["title"], unique=False)
    op.create_index("ix_recipes_category", "recipes", ["category"], unique=False)
    op.create_index("ix_recipes_difficulty", "recipes", ["difficulty"], unique=False)
    op.create_index("ix_recipes_prep_time_minutes", "recipes", ["prep_time_minutes"], unique=False)
    op.create_index("ix_recipes_creator_id", "recipes", ["creator_id"], unique=False)
    op.create_index("ix_recipes_created_at", "recipes", ["created_at"], unique=False)
    op.create_table(
        "ingredients",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.UniqueConstraint("name", name="uq_ingredients_name"),
    )
    op.create_index("ix_ingredients_name", "ingredients", ["name"], unique=True)
    op.create_table(
        "recipe_ingredients",
        sa.Column("recipe_id", sa.Integer(), sa.ForeignKey("recipes.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("ingredient_id", sa.Integer(), sa.ForeignKey("ingredients.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("quantity_text", sa.String(length=120), nullable=False),
        sa.Column("grams", sa.Integer(), nullable=True),
    )
    op.create_table(
        "reviews",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("recipe_id", sa.Integer(), sa.ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column("comment", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("user_id", "recipe_id", name="uq_reviews_user_recipe"),
    )
    op.create_index("ix_reviews_recipe_id", "reviews", ["recipe_id"], unique=False)
    op.create_index("ix_reviews_user_id", "reviews", ["user_id"], unique=False)
    op.create_table(
        "favorites",
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("recipe_id", sa.Integer(), sa.ForeignKey("recipes.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("user_id", "recipe_id", name="uq_favorites_user_recipe"),
    )
    op.create_table(
        "recipe_images",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("recipe_id", sa.Integer(), sa.ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("content_type", sa.String(length=50), nullable=False),
        sa.Column("data", sa.LargeBinary(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_recipe_images_recipe_id", "recipe_images", ["recipe_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_recipe_images_recipe_id", table_name="recipe_images")
    op.drop_table("recipe_images")
    op.drop_table("favorites")
    op.drop_index("ix_reviews_user_id", table_name="reviews")
    op.drop_index("ix_reviews_recipe_id", table_name="reviews")
    op.drop_table("reviews")
    op.drop_table("recipe_ingredients")
    op.drop_index("ix_ingredients_name", table_name="ingredients")
    op.drop_table("ingredients")
    op.drop_index("ix_recipes_created_at", table_name="recipes")
    op.drop_index("ix_recipes_creator_id", table_name="recipes")
    op.drop_index("ix_recipes_prep_time_minutes", table_name="recipes")
    op.drop_index("ix_recipes_difficulty", table_name="recipes")
    op.drop_index("ix_recipes_category", table_name="recipes")
    op.drop_index("ix_recipes_title", table_name="recipes")
    op.drop_table("recipes")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
