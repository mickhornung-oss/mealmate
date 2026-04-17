from __future__ import annotations

import re
from urllib.parse import quote

from fastapi import HTTPException, Request, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.dependencies import template_context
from app.i18n import t
from app.models import (
    Recipe,
    RecipeImage,
    RecipeImageChangeRequest,
    RecipeIngredient,
    Review,
    User,
    Favorite,
)
from app.services import DEFAULT_CATEGORY, can_manage_recipe, normalize_category
from app.translation_models import RecipeTranslation
from app.views import templates

def parse_positive_int(value: str, field_name: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{field_name} must be an integer.") from exc
    if parsed <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{field_name} must be greater than zero.")
    return parsed


def normalize_image_url(value: str) -> str | None:
    cleaned = value.strip()
    if not cleaned:
        return None
    if not (cleaned.startswith("http://") or cleaned.startswith("https://")):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="title_image_url must start with http:// or https://")
    return cleaned


def build_pagination_items(page: int, total_pages: int) -> list[int | None]:
    if total_pages <= 7:
        return list(range(1, total_pages + 1))
    if page <= 4:
        return [1, 2, 3, 4, 5, None, total_pages]
    if page >= total_pages - 3:
        return [1, None, total_pages - 4, total_pages - 3, total_pages - 2, total_pages - 1, total_pages]
    return [1, None, page - 1, page, page + 1, None, total_pages]


def sanitize_dom_id(value: str, fallback: str = "favorite-box") -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9_-]", "", str(value or ""))
    return cleaned or fallback


def get_request_language(request: Request) -> str:
    raw = getattr(getattr(request, "state", None), "lang", "de")
    token = str(raw or "de").strip().lower().replace("_", "-")
    return token.split("-", 1)[0] if token else "de"


def load_recipe_translations(
    db: Session,
    recipe_ids: list[int],
    language: str,
) -> dict[int, RecipeTranslation]:
    if not recipe_ids:
        return {}
    rows = db.scalars(
        select(RecipeTranslation).where(
            RecipeTranslation.recipe_id.in_(recipe_ids),
            RecipeTranslation.language == language,
            RecipeTranslation.stale.is_(False),
        )
    ).all()
    return {int(row.recipe_id): row for row in rows}


def get_recipe_display_fields(recipe: Recipe, translation: RecipeTranslation | None) -> dict[str, str]:
    if not translation:
        return {
            "title": recipe.title or "",
            "description": recipe.description or "",
            "instructions": recipe.instructions or "",
            "ingredients_text": "",
        }
    return {
        "title": translation.title or recipe.title or "",
        "description": translation.description or recipe.description or "",
        "instructions": translation.instructions or recipe.instructions or "",
        "ingredients_text": translation.ingredients_text or "",
    }


def resolve_category_value(category_select: str, category_new: str, category_legacy: str = "") -> str:
    if category_select and category_select != "__new__":
        return normalize_category(category_select)
    if category_new.strip():
        return normalize_category(category_new)
    if category_legacy.strip():
        return normalize_category(category_legacy)
    return DEFAULT_CATEGORY


def fetch_recipe_or_404(db: Session, recipe_id: int) -> Recipe:
    recipe = db.scalar(
        select(Recipe)
        .where(Recipe.id == recipe_id)
        .options(
            joinedload(Recipe.creator),
            selectinload(Recipe.recipe_ingredients).joinedload(RecipeIngredient.ingredient),
            selectinload(Recipe.reviews).joinedload(Review.user),
            selectinload(Recipe.images),
        )
    )
    if not recipe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found.")
    return recipe


def ensure_recipe_visible(recipe: Recipe, current_user: User | None) -> None:
    if recipe.is_published:
        return
    if current_user and (current_user.role == "admin" or current_user.id == recipe.creator_id):
        return
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found.")


def ensure_recipe_access(user: User, recipe: Recipe) -> None:
    if not can_manage_recipe(user, recipe):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions for this recipe.")


def get_primary_image(recipe: Recipe) -> RecipeImage | None:
    for image in recipe.images:
        if image.is_primary:
            return image
    return recipe.images[0] if recipe.images else None


def get_external_fallback_image_url(recipe: Recipe) -> str | None:
    for candidate in (recipe.source_image_url, recipe.title_image_url):
        cleaned = str(candidate or "").strip()
        if not cleaned:
            continue
        if "kein_bild" in cleaned.casefold():
            continue
        return cleaned
    return None


def to_external_image_proxy_url(url: str) -> str:
    return f"/external-image?url={quote(url, safe='')}"


def resolve_recipe_display_image(recipe: Recipe, primary_image: RecipeImage | None) -> tuple[str | None, str]:
    if primary_image:
        return f"/images/{primary_image.id}", "db"
    external_url = get_external_fallback_image_url(recipe)
    if external_url:
        return to_external_image_proxy_url(external_url), "external"
    return None, "placeholder"


def can_direct_upload(user: User | None) -> bool:
    return bool(user and user.role == "admin")


def can_request_image_change(user: User | None) -> bool:
    return bool(user and user.role != "admin")


def user_has_pending_image_request(db: Session, recipe_id: int, current_user: User | None) -> bool:
    if not current_user or current_user.role == "admin":
        return False
    pending = db.scalar(
        select(func.count())
        .select_from(RecipeImageChangeRequest)
        .where(
            RecipeImageChangeRequest.recipe_id == recipe_id,
            RecipeImageChangeRequest.requester_user_id == current_user.id,
            RecipeImageChangeRequest.status == "pending",
        )
    )
    return bool(int(pending or 0))


def set_recipe_primary_image(db: Session, recipe: Recipe, image_id: int) -> None:
    for image in recipe.images:
        image.is_primary = image.id == image_id
    db.flush()


def maybe_promote_primary_after_delete(db: Session, recipe: Recipe) -> None:
    remaining = list(recipe.images)
    if not remaining:
        return
    if any(image.is_primary for image in remaining):
        return
    remaining[0].is_primary = True
    db.flush()


def render_image_section(
    request: Request,
    db: Session,
    recipe_id: int,
    current_user: User | None,
    *,
    feedback_message: str = "",
    feedback_error: str = "",
    status_code: int = status.HTTP_200_OK,
):
    recipe = fetch_recipe_or_404(db, recipe_id)
    primary_image = get_primary_image(recipe)
    display_image_url, display_image_kind = resolve_recipe_display_image(recipe, primary_image)
    return templates.TemplateResponse(
        "partials/recipe_images.html",
        template_context(
            request,
            current_user,
            recipe=recipe,
            primary_image=primary_image,
            display_image_url=display_image_url,
            display_image_kind=display_image_kind,
            can_upload_direct=can_direct_upload(current_user),
            can_request_change=can_request_image_change(current_user),
            has_pending_change_request=user_has_pending_image_request(db, recipe_id, current_user),
            image_feedback_message=feedback_message,
            image_feedback_error=feedback_error,
        ),
        status_code=status_code,
    )


def render_recipe_card_image(
    request: Request,
    db: Session,
    recipe_id: int,
    current_user: User | None,
    *,
    feedback_message: str = "",
    feedback_error: str = "",
    status_code: int = status.HTTP_200_OK,
):
    recipe = db.scalar(select(Recipe).where(Recipe.id == recipe_id).options(selectinload(Recipe.images)))
    if not recipe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=t("error.recipe_not_found", request=request))
    primary_image = get_primary_image(recipe)
    display_image_url, display_image_kind = resolve_recipe_display_image(recipe, primary_image)
    return templates.TemplateResponse(
        "partials/recipe_card_image.html",
        template_context(
            request,
            current_user,
            recipe=recipe,
            primary_image=primary_image,
            display_image_url=display_image_url,
            display_image_kind=display_image_kind,
            can_upload_direct=can_direct_upload(current_user),
            can_request_change=can_request_image_change(current_user),
            has_pending_change_request=user_has_pending_image_request(db, recipe_id, current_user),
            image_feedback_message=feedback_message,
            image_feedback_error=feedback_error,
        ),
        status_code=status_code,
    )

