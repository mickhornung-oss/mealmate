from __future__ import annotations

from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app import services as legacy_services
from app.models import Recipe, RecipeImage, RecipeIngredient, RecipeSubmission, SubmissionImage, SubmissionIngredient

normalize_raw_category = legacy_services.normalize_raw_category
guess_canonical_category = legacy_services.guess_canonical_category
get_enabled_category_mappings = legacy_services.get_enabled_category_mappings
sanitize_difficulty = legacy_services.sanitize_difficulty
get_or_create_ingredient = legacy_services.get_or_create_ingredient
normalize_ingredient_name = legacy_services.normalize_ingredient_name
parse_optional_int = legacy_services.parse_optional_int


def replace_submission_ingredients(
    db: Session,
    submission: RecipeSubmission,
    ingredient_entries: list[dict[str, Any]],
) -> None:
    submission.ingredients.clear()
    merged_entries: dict[str, dict[str, Any]] = {}
    for entry in ingredient_entries:
        name = str(entry.get("name") or "").strip()
        if not name:
            continue
        key = normalize_ingredient_name(name)
        quantity_text = str(entry.get("quantity_text") or "").strip()[:120]
        grams = parse_optional_int(entry.get("grams"))
        if key not in merged_entries:
            merged_entries[key] = {"name": name[:200], "quantity_text": quantity_text, "grams": grams}
            continue
        current = merged_entries[key]
        if quantity_text:
            if current["quantity_text"]:
                current["quantity_text"] = f"{current['quantity_text']} | {quantity_text}"[:120]
            else:
                current["quantity_text"] = quantity_text
        if current["grams"] is None and grams is not None:
            current["grams"] = grams
    for merged in merged_entries.values():
        db.add(
            SubmissionIngredient(
                submission=submission,
                ingredient_name=merged["name"],
                quantity_text=merged["quantity_text"],
                grams=merged["grams"],
                ingredient_name_normalized=normalize_ingredient_name(merged["name"]),
            )
        )


def build_submission_ingredients_text(ingredients: list[SubmissionIngredient]) -> str:
    lines: list[str] = []
    for ingredient in ingredients:
        name = ingredient.ingredient_name.strip()
        if not name:
            continue
        if ingredient.grams is not None:
            lines.append(f"{name}|{ingredient.quantity_text}|{ingredient.grams}")
            continue
        if ingredient.quantity_text:
            lines.append(f"{name}|{ingredient.quantity_text}")
            continue
        lines.append(name)
    return "\n".join(lines)


def get_submission_primary_image(submission: RecipeSubmission) -> SubmissionImage | None:
    for image in submission.images:
        if image.is_primary:
            return image
    return submission.images[0] if submission.images else None


def _build_submission_recipe_values(
    submission: RecipeSubmission,
    *,
    admin_id: int,
    normalized_raw_category: str,
    guessed_canonical: str,
    source_uuid: str,
) -> dict[str, Any]:
    return {
        "title": submission.title.strip()[:255],
        "description": submission.description.strip(),
        "instructions": submission.instructions.strip(),
        "category": normalized_raw_category,
        "canonical_category": guessed_canonical,
        "prep_time_minutes": max(int(submission.prep_time_minutes or 30), 1),
        "difficulty": sanitize_difficulty(submission.difficulty),
        "creator_id": admin_id,
        "source": "submission",
        "source_uuid": source_uuid,
        "source_url": None,
        "source_image_url": None,
        "title_image_url": None,
        "servings_text": (submission.servings_text or "").strip()[:120] or None,
        "total_time_minutes": None,
        "is_published": True,
    }


def _copy_submission_ingredients_to_recipe(db: Session, submission: RecipeSubmission, recipe: Recipe) -> None:
    for item in submission.ingredients:
        ingredient_name = item.ingredient_name.strip()
        if not ingredient_name:
            continue
        ingredient = get_or_create_ingredient(db, ingredient_name)
        db.add(
            RecipeIngredient(
                recipe_id=recipe.id,
                ingredient_id=ingredient.id,
                quantity_text=(item.quantity_text or "").strip()[:120],
                grams=item.grams,
            )
        )


def _copy_submission_images_to_recipe(db: Session, submission: RecipeSubmission, recipe: Recipe) -> None:
    any_primary = False
    for image in submission.images:
        db.add(
            RecipeImage(
                recipe_id=recipe.id,
                filename=image.filename,
                content_type=image.content_type,
                data=image.data,
                is_primary=image.is_primary,
            )
        )
        if image.is_primary:
            any_primary = True
    if submission.images and not any_primary:
        first_recipe_image = db.scalar(
            select(RecipeImage).where(RecipeImage.recipe_id == recipe.id).order_by(RecipeImage.id.asc())
        )
        if first_recipe_image:
            first_recipe_image.is_primary = True


def publish_submission_as_recipe(db: Session, submission: RecipeSubmission, admin_id: int) -> Recipe:
    source_uuid = f"submission:{submission.id}"
    existing = db.scalar(select(Recipe).where(Recipe.source_uuid == source_uuid))
    if existing:
        raise ValueError("Submission has already been published.")
    normalized_raw_category = normalize_raw_category(submission.category)
    guessed_canonical = guess_canonical_category(
        raw_category=normalized_raw_category,
        title=submission.title,
        description=submission.description,
        mappings=get_enabled_category_mappings(db),
    )
    recipe_values = _build_submission_recipe_values(
        submission,
        admin_id=admin_id,
        normalized_raw_category=normalized_raw_category,
        guessed_canonical=guessed_canonical,
        source_uuid=source_uuid,
    )
    recipe = Recipe(**recipe_values)
    db.add(recipe)
    db.flush()
    _copy_submission_ingredients_to_recipe(db, submission, recipe)
    _copy_submission_images_to_recipe(db, submission, recipe)
    return recipe


def get_submission_status_stats(db: Session) -> dict[str, int]:
    rows = db.execute(
        select(RecipeSubmission.status, func.count(RecipeSubmission.id)).group_by(RecipeSubmission.status)
    ).all()
    base = {"pending": 0, "approved": 0, "rejected": 0}
    for status, count in rows:
        base[str(status)] = int(count)
    return base
