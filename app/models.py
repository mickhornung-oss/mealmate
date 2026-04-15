from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, LargeBinary, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


SUBMISSION_STATUS_ENUM = Enum(
    "pending",
    "approved",
    "rejected",
    name="submission_status",
    native_enum=False,
)

IMAGE_CHANGE_STATUS_ENUM = Enum(
    "pending",
    "approved",
    "rejected",
    name="image_change_status",
    native_enum=False,
)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_uid: Mapped[str] = mapped_column(String(36), unique=True, nullable=False, default=lambda: str(uuid4()), index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    username: Mapped[str | None] = mapped_column(String(30), unique=True, nullable=True, index=True)
    username_normalized: Mapped[str | None] = mapped_column(String(30), unique=True, nullable=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), default="user", nullable=False)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_login_ip: Mapped[str | None] = mapped_column(String(64), nullable=True)
    last_login_user_agent: Mapped[str | None] = mapped_column(String(200), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    recipes: Mapped[list["Recipe"]] = relationship(back_populates="creator", cascade="all, delete-orphan")
    reviews: Mapped[list["Review"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    favorites: Mapped[list["Favorite"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    submissions: Mapped[list["RecipeSubmission"]] = relationship(
        back_populates="submitter_user",
        cascade="all, delete-orphan",
        foreign_keys="RecipeSubmission.submitter_user_id",
    )
    reviewed_submissions: Mapped[list["RecipeSubmission"]] = relationship(
        back_populates="reviewed_by_admin",
        foreign_keys="RecipeSubmission.reviewed_by_admin_id",
    )
    password_reset_tokens: Mapped[list["PasswordResetToken"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    security_events: Mapped[list["SecurityEvent"]] = relationship(
        back_populates="user",
    )
    image_change_requests: Mapped[list["RecipeImageChangeRequest"]] = relationship(
        back_populates="requester_user",
        foreign_keys="RecipeImageChangeRequest.requester_user_id",
    )
    reviewed_image_change_requests: Mapped[list["RecipeImageChangeRequest"]] = relationship(
        back_populates="reviewed_by_admin",
        foreign_keys="RecipeImageChangeRequest.reviewed_by_admin_id",
    )


class Recipe(Base):
    __tablename__ = "recipes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    title_image_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    source: Mapped[str] = mapped_column(String(50), nullable=False, default="user", index=True)
    source_uuid: Mapped[str | None] = mapped_column(String(120), nullable=True, unique=True, index=True)
    source_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    source_image_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    servings_text: Mapped[str | None] = mapped_column(String(120), nullable=True)
    total_time_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_published: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    instructions: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    canonical_category: Mapped[str | None] = mapped_column(String(60), nullable=True, index=True)
    prep_time_minutes: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    difficulty: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    creator_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)

    creator: Mapped["User"] = relationship(back_populates="recipes")
    recipe_ingredients: Mapped[list["RecipeIngredient"]] = relationship(
        back_populates="recipe",
        cascade="all, delete-orphan",
    )
    reviews: Mapped[list["Review"]] = relationship(back_populates="recipe", cascade="all, delete-orphan")
    favorites: Mapped[list["Favorite"]] = relationship(back_populates="recipe", cascade="all, delete-orphan")
    images: Mapped[list["RecipeImage"]] = relationship(
        back_populates="recipe",
        cascade="all, delete-orphan",
        order_by="RecipeImage.created_at",
    )
    image_change_requests: Mapped[list["RecipeImageChangeRequest"]] = relationship(
        back_populates="recipe",
        cascade="all, delete-orphan",
        order_by="RecipeImageChangeRequest.created_at",
    )


class CategoryMapping(Base):
    __tablename__ = "category_mappings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    pattern: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    canonical_category: Mapped[str] = mapped_column(String(60), nullable=False, index=True)
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=100, server_default="100", index=True)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="1", index=True)
    scope: Mapped[str] = mapped_column(String(20), nullable=False, default="raw", server_default="raw", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)


class Ingredient(Base):
    __tablename__ = "ingredients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), unique=True, nullable=False, index=True)

    recipe_links: Mapped[list["RecipeIngredient"]] = relationship(
        back_populates="ingredient",
        cascade="all, delete-orphan",
    )


class RecipeIngredient(Base):
    __tablename__ = "recipe_ingredients"

    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id", ondelete="CASCADE"), primary_key=True)
    ingredient_id: Mapped[int] = mapped_column(ForeignKey("ingredients.id", ondelete="CASCADE"), primary_key=True)
    quantity_text: Mapped[str] = mapped_column(String(120), default="", nullable=False)
    grams: Mapped[int | None] = mapped_column(Integer, nullable=True)

    recipe: Mapped["Recipe"] = relationship(back_populates="recipe_ingredients")
    ingredient: Mapped["Ingredient"] = relationship(back_populates="recipe_links")


class Review(Base):
    __tablename__ = "reviews"
    __table_args__ = (UniqueConstraint("user_id", "recipe_id", name="uq_reviews_user_recipe"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    comment: Mapped[str] = mapped_column(Text, default="", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    recipe: Mapped["Recipe"] = relationship(back_populates="reviews")
    user: Mapped["User"] = relationship(back_populates="reviews")


class Favorite(Base):
    __tablename__ = "favorites"
    __table_args__ = (UniqueConstraint("user_id", "recipe_id", name="uq_favorites_user_recipe"),)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id", ondelete="CASCADE"), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    user: Mapped["User"] = relationship(back_populates="favorites")
    recipe: Mapped["Recipe"] = relationship(back_populates="favorites")


class RecipeImage(Base):
    __tablename__ = "recipe_images"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False, index=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str] = mapped_column(String(50), nullable=False)
    data: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    recipe: Mapped["Recipe"] = relationship(back_populates="images")


class RecipeImageChangeRequest(Base):
    __tablename__ = "recipe_image_change_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False, index=True)
    requester_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    status: Mapped[str] = mapped_column(
        IMAGE_CHANGE_STATUS_ENUM,
        nullable=False,
        default="pending",
        server_default="pending",
        index=True,
    )
    admin_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    reviewed_by_admin_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    recipe: Mapped["Recipe"] = relationship(back_populates="image_change_requests")
    requester_user: Mapped["User"] = relationship(
        back_populates="image_change_requests",
        foreign_keys=[requester_user_id],
    )
    reviewed_by_admin: Mapped["User"] = relationship(
        back_populates="reviewed_image_change_requests",
        foreign_keys=[reviewed_by_admin_id],
    )
    files: Mapped[list["RecipeImageChangeFile"]] = relationship(
        back_populates="request",
        cascade="all, delete-orphan",
        order_by="RecipeImageChangeFile.created_at",
    )


class RecipeImageChangeFile(Base):
    __tablename__ = "recipe_image_change_files"
    __table_args__ = (UniqueConstraint("request_id", name="uq_recipe_image_change_files_request"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    request_id: Mapped[int] = mapped_column(
        ForeignKey("recipe_image_change_requests.id", ondelete="CASCADE"), nullable=False, index=True
    )
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str] = mapped_column(String(50), nullable=False)
    data: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    request: Mapped["RecipeImageChangeRequest"] = relationship(back_populates="files")


class RecipeSubmission(Base):
    __tablename__ = "recipe_submissions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    submitter_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    submitter_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    difficulty: Mapped[str] = mapped_column(String(30), nullable=False, default="medium", index=True)
    prep_time_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    servings_text: Mapped[str | None] = mapped_column(String(120), nullable=True)
    instructions: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(SUBMISSION_STATUS_ENUM, nullable=False, default="pending", server_default="pending", index=True)
    admin_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    reviewed_by_admin_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)

    submitter_user: Mapped["User"] = relationship(
        back_populates="submissions",
        foreign_keys=[submitter_user_id],
    )
    reviewed_by_admin: Mapped["User"] = relationship(
        back_populates="reviewed_submissions",
        foreign_keys=[reviewed_by_admin_id],
    )
    ingredients: Mapped[list["SubmissionIngredient"]] = relationship(
        back_populates="submission",
        cascade="all, delete-orphan",
        order_by="SubmissionIngredient.id",
    )
    images: Mapped[list["SubmissionImage"]] = relationship(
        back_populates="submission",
        cascade="all, delete-orphan",
        order_by="SubmissionImage.created_at",
    )


class SubmissionIngredient(Base):
    __tablename__ = "submission_ingredients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    submission_id: Mapped[int] = mapped_column(ForeignKey("recipe_submissions.id", ondelete="CASCADE"), nullable=False, index=True)
    ingredient_name: Mapped[str] = mapped_column(String(200), nullable=False)
    quantity_text: Mapped[str] = mapped_column(String(120), nullable=False, default="")
    grams: Mapped[int | None] = mapped_column(Integer, nullable=True)
    ingredient_name_normalized: Mapped[str | None] = mapped_column(String(200), nullable=True, index=True)

    submission: Mapped["RecipeSubmission"] = relationship(back_populates="ingredients")


class SubmissionImage(Base):
    __tablename__ = "submission_images"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    submission_id: Mapped[int] = mapped_column(ForeignKey("recipe_submissions.id", ondelete="CASCADE"), nullable=False, index=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str] = mapped_column(String(50), nullable=False)
    data: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    submission: Mapped["RecipeSubmission"] = relationship(back_populates="images")


class AppMeta(Base):
    __tablename__ = "app_meta"

    key: Mapped[str] = mapped_column(String(120), primary_key=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)


class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    new_email_normalized: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    token_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    created_ip: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_user_agent: Mapped[str | None] = mapped_column(String(200), nullable=True)
    purpose: Mapped[str] = mapped_column(String(50), nullable=False, default="password_reset", index=True)

    user: Mapped["User"] = relationship(back_populates="password_reset_tokens")


class SecurityEvent(Base):
    __tablename__ = "security_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    event_type: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)
    ip: Mapped[str | None] = mapped_column(String(64), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(200), nullable=True)
    details: Mapped[str | None] = mapped_column(String(300), nullable=True)

    user: Mapped["User"] = relationship(back_populates="security_events")
