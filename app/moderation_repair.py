from dataclasses import dataclass, field

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models import Recipe, RecipeIngredient, RecipeSubmission, SubmissionImage, User
from app.services import DEFAULT_CATEGORY, normalize_category, replace_submission_ingredients, sanitize_difficulty


@dataclass
class ModerationRepairReport:
    dry_run: bool
    scanned_count: int = 0
    affected_count: int = 0
    moved_to_pending_count: int = 0
    skipped_count: int = 0
    details: list[str] = field(default_factory=list)


def _suspicious_recipes_query():
    return (
        select(Recipe)
        .join(User, User.id == Recipe.creator_id)
        .where(
            Recipe.is_published.is_(True),
            User.role != "admin",
            Recipe.source != "kochwiki",
        )
        .options(
            joinedload(Recipe.creator),
            selectinload(Recipe.recipe_ingredients).joinedload(RecipeIngredient.ingredient),
            selectinload(Recipe.images),
        )
        .order_by(Recipe.id.asc())
    )


def _copy_recipe_to_pending_submission(db: Session, recipe: Recipe) -> RecipeSubmission:
    submission = RecipeSubmission(
        submitter_user_id=recipe.creator_id,
        submitter_email=None,
        title=recipe.title.strip()[:255],
        description=recipe.description.strip() or "Aus veroeffentlichtem Rezept zur Moderation uebernommen.",
        category=normalize_category(recipe.category or DEFAULT_CATEGORY),
        difficulty=sanitize_difficulty(recipe.difficulty or "medium"),
        prep_time_minutes=recipe.prep_time_minutes,
        servings_text=(recipe.servings_text or "").strip()[:120] or None,
        instructions=recipe.instructions.strip(),
        status="pending",
        admin_note=f"Auto-Reparatur: Rezept {recipe.id} wurde zur Moderation verschoben.",
    )
    db.add(submission)
    db.flush()

    ingredient_entries: list[dict[str, object]] = []
    for link in recipe.recipe_ingredients:
        ingredient_entries.append(
            {
                "name": link.ingredient.name if link.ingredient else "",
                "quantity_text": link.quantity_text,
                "grams": link.grams,
            }
        )
    replace_submission_ingredients(db, submission, ingredient_entries)

    any_primary = False
    first_copy: SubmissionImage | None = None
    for image in recipe.images:
        copied = SubmissionImage(
            submission_id=submission.id,
            filename=image.filename,
            content_type=image.content_type,
            data=image.data,
            is_primary=image.is_primary,
        )
        db.add(copied)
        if first_copy is None:
            first_copy = copied
        any_primary = any_primary or image.is_primary
    if first_copy and not any_primary:
        first_copy.is_primary = True

    return submission


def run_moderation_repair(db: Session, dry_run: bool = True) -> ModerationRepairReport:
    report = ModerationRepairReport(dry_run=dry_run)
    recipes = db.scalars(_suspicious_recipes_query()).all()
    report.scanned_count = len(recipes)
    for recipe in recipes:
        report.affected_count += 1
        report.details.append(
            f"recipe_id={recipe.id} title={recipe.title!r} creator={recipe.creator.email if recipe.creator else recipe.creator_id}"
        )
        if dry_run:
            continue
        _copy_recipe_to_pending_submission(db, recipe)
        recipe.is_published = False
        db.add(recipe)
        report.moved_to_pending_count += 1
    report.skipped_count = report.scanned_count - report.affected_count
    return report
