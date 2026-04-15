from io import BytesIO
import re
from urllib.parse import quote

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, Request, UploadFile, status
from fastapi.responses import RedirectResponse, Response, StreamingResponse
from sqlalchemy import and_, desc, func, or_, select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.database import get_db
from app.dependencies import get_admin_user, get_current_user, get_current_user_optional, template_context
from app.image_utils import ImageValidationError, safe_image_filename, validate_image_upload
from app.i18n import t
from app.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeImage,
    RecipeImageChangeFile,
    RecipeImageChangeRequest,
    RecipeIngredient,
    Review,
    User,
)
from app.pdf_service import build_recipe_pdf
from app.rate_limit import key_by_ip, key_by_user_or_ip, limiter
from app.services import (
    DEFAULT_CATEGORY,
    build_category_index,
    can_manage_recipe,
    get_distinct_categories,
    normalize_category,
    parse_ingredient_text,
    replace_recipe_ingredients,
    resolve_title_image_url,
    sanitize_difficulty,
)
from app.translation_models import RecipeTranslation
from app.views import redirect, templates

router = APIRouter(tags=["recipes"])

PAGE_SIZE_DEFAULT = 20
PAGE_SIZE_OPTIONS = (10, 20, 40, 80)


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


@router.get("/")
def home_page(
    request: Request,
    page: int = Query(1, ge=1),
    per_page: int = Query(PAGE_SIZE_DEFAULT, ge=1, le=max(PAGE_SIZE_OPTIONS)),
    sort: str = Query("date", pattern="^(date|prep_time|avg_rating)$"),
    title: str = Query("", max_length=512),
    category: str = Query("", max_length=120),
    difficulty: str = Query("", max_length=20),
    ingredient: str = Query("", max_length=512),
    image_filter: str = "",
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    if per_page not in PAGE_SIZE_OPTIONS:
        per_page = PAGE_SIZE_DEFAULT
    category_index = build_category_index(db, only_published=True)
    category_options = sorted(category_index.keys(), key=str.casefold)
    selected_category = normalize_category(category, allow_empty=True)
    if selected_category and selected_category not in category_index:
        category_index[selected_category] = [selected_category]
        category_options = sorted(category_index.keys(), key=str.casefold)
    review_stats = (
        select(
            Review.recipe_id.label("recipe_id"),
            func.avg(Review.rating).label("avg_rating"),
            func.count(Review.id).label("review_count"),
        )
        .group_by(Review.recipe_id)
        .subquery()
    )
    stmt = (
        select(
            Recipe,
            func.coalesce(review_stats.c.avg_rating, 0).label("avg_rating"),
            func.coalesce(review_stats.c.review_count, 0).label("review_count"),
        )
        .outerjoin(review_stats, Recipe.id == review_stats.c.recipe_id)
        .where(Recipe.is_published.is_(True))
        .options(selectinload(Recipe.images))
    )
    if title.strip():
        like = f"%{title.strip()}%"
        stmt = stmt.where(Recipe.title.ilike(like))
    if selected_category:
        stmt = stmt.where(Recipe.category.in_(category_index.get(selected_category, [selected_category])))
    if difficulty.strip():
        stmt = stmt.where(Recipe.difficulty == sanitize_difficulty(difficulty))
    if ingredient.strip():
        like = f"%{ingredient.strip().lower()}%"
        ingredient_recipe_ids = (
            select(RecipeIngredient.recipe_id)
            .join(Ingredient, Ingredient.id == RecipeIngredient.ingredient_id)
            .where(Ingredient.name.ilike(like))
            .subquery()
        )
        stmt = stmt.where(Recipe.id.in_(select(ingredient_recipe_ids.c.recipe_id)))
    selected_image_filter = image_filter if image_filter in {"with_image"} else ""
    if selected_image_filter == "with_image":
        has_db_image = select(RecipeImage.id).where(RecipeImage.recipe_id == Recipe.id).exists()
        has_external_image = and_(
            Recipe.source_image_url.is_not(None),
            Recipe.source_image_url != "",
            func.lower(Recipe.source_image_url).not_like("%kein_bild%"),
        )
        has_title_image = and_(
            Recipe.title_image_url.is_not(None),
            Recipe.title_image_url != "",
            func.lower(Recipe.title_image_url).not_like("%kein_bild%"),
        )
        stmt = stmt.where(or_(has_db_image, has_external_image, has_title_image))
    if sort == "prep_time":
        stmt = stmt.order_by(Recipe.prep_time_minutes.asc(), Recipe.created_at.desc())
    elif sort == "avg_rating":
        stmt = stmt.order_by(desc("avg_rating"), Recipe.created_at.desc())
    else:
        stmt = stmt.order_by(Recipe.created_at.desc())
    total = db.scalar(select(func.count()).select_from(stmt.subquery()))
    pages = max((total + per_page - 1) // per_page, 1)
    page = min(page, pages)
    rows = db.execute(stmt.offset((page - 1) * per_page).limit(per_page)).all()
    featured_stmt = (
        select(
            Recipe,
            func.coalesce(review_stats.c.avg_rating, 0).label("avg_rating"),
            func.coalesce(review_stats.c.review_count, 0).label("review_count"),
        )
        .outerjoin(review_stats, Recipe.id == review_stats.c.recipe_id)
        .where(Recipe.is_published.is_(True))
        .where(
            or_(
                select(RecipeImage.id).where(RecipeImage.recipe_id == Recipe.id).exists(),
                and_(
                    Recipe.source_image_url.is_not(None),
                    Recipe.source_image_url != "",
                    func.lower(Recipe.source_image_url).not_like("%kein_bild%"),
                ),
                and_(
                    Recipe.title_image_url.is_not(None),
                    Recipe.title_image_url != "",
                    func.lower(Recipe.title_image_url).not_like("%kein_bild%"),
                ),
            )
        )
        .options(selectinload(Recipe.images))
        .order_by(desc("avg_rating"), desc("review_count"), Recipe.created_at.desc())
        .limit(8)
    )
    featured_rows = db.execute(featured_stmt).all()
    requested_language = get_request_language(request)
    all_recipe_ids = list({int(row[0].id) for row in rows} | {int(row[0].id) for row in featured_rows})
    translations_by_recipe = load_recipe_translations(db, all_recipe_ids, requested_language)
    recipe_ids = [int(row[0].id) for row in rows]
    favorite_recipe_ids: set[int] = set()
    if current_user and recipe_ids:
        favorite_rows = db.scalars(
            select(Favorite.recipe_id).where(
                Favorite.user_id == current_user.id,
                Favorite.recipe_id.in_(recipe_ids),
            )
        ).all()
        favorite_recipe_ids = {int(item) for item in favorite_rows}
    pending_recipe_ids: set[int] = set()
    if current_user and current_user.role != "admin" and recipe_ids:
        pending_rows = db.scalars(
            select(RecipeImageChangeRequest.recipe_id).where(
                RecipeImageChangeRequest.recipe_id.in_(recipe_ids),
                RecipeImageChangeRequest.requester_user_id == current_user.id,
                RecipeImageChangeRequest.status == "pending",
            )
        ).all()
        pending_recipe_ids = {int(item) for item in pending_rows}
    recipes_data = []
    for row in rows:
        recipe = row[0]
        translation = translations_by_recipe.get(int(recipe.id))
        display_fields = get_recipe_display_fields(recipe, translation)
        primary_image = get_primary_image(recipe)
        display_image_url, display_image_kind = resolve_recipe_display_image(recipe, primary_image)
        recipes_data.append(
            {
                "recipe": recipe,
                "display_title": display_fields["title"],
                "avg_rating": float(row[1] or 0),
                "review_count": int(row[2] or 0),
                "primary_image": primary_image,
                "display_image_url": display_image_url,
                "display_image_kind": display_image_kind,
                "has_pending_change_request": recipe.id in pending_recipe_ids,
                "is_favorite": recipe.id in favorite_recipe_ids,
                "favorite_box_id": f"favorite-box-card-{recipe.id}",
            }
        )
    featured_recipes = []
    for row in featured_rows:
        recipe = row[0]
        translation = translations_by_recipe.get(int(recipe.id))
        display_fields = get_recipe_display_fields(recipe, translation)
        primary_image = get_primary_image(recipe)
        display_image_url, display_image_kind = resolve_recipe_display_image(recipe, primary_image)
        featured_recipes.append(
            {
                "recipe": recipe,
                "display_title": display_fields["title"],
                "avg_rating": float(row[1] or 0),
                "review_count": int(row[2] or 0),
                "display_image_url": display_image_url,
                "display_image_kind": display_image_kind,
            }
        )
    quick_categories = category_options[:8]
    start_item = ((page - 1) * per_page + 1) if total > 0 else 0
    end_item = min(page * per_page, total)
    pagination_items = build_pagination_items(page, pages)
    context = template_context(
        request,
        current_user,
        recipes_data=recipes_data,
        page=page,
        pages=pages,
        total_pages=pages,
        per_page=per_page,
        per_page_options=PAGE_SIZE_OPTIONS,
        category_options=category_options,
        total=total,
        total_count=total,
        start_item=start_item,
        end_item=end_item,
        pagination_items=pagination_items,
        sort=sort,
        title=title,
        category=selected_category,
        difficulty=difficulty,
        ingredient=ingredient,
        image_filter=selected_image_filter,
        featured_recipes=featured_recipes,
        quick_categories=quick_categories,
    )
    if request.headers.get("HX-Request") == "true":
        return templates.TemplateResponse("partials/recipe_list.html", context)
    return templates.TemplateResponse("home.html", context)


@router.get("/recipes/new")
def create_recipe_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    return templates.TemplateResponse(
        "recipe_form.html",
        template_context(
            request,
            current_user,
            recipe=None,
            error=None,
            form_mode="create",
            category_options=get_distinct_categories(db, only_published=False),
            selected_category=DEFAULT_CATEGORY,
            category_new_value="",
        ),
    )


@router.post("/recipes")
@router.post("/recipes/new")
async def create_recipe_submit(
    request: Request,
    title: str = Form(...),
    description: str = Form(...),
    instructions: str = Form(...),
    category_select: str = Form(DEFAULT_CATEGORY),
    category_new: str = Form(""),
    category: str = Form(""),
    title_image_url: str = Form(""),
    prep_time_minutes: str = Form(...),
    difficulty: str = Form(...),
    ingredients_text: str = Form(""),
    image: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    prep_time = parse_positive_int(prep_time_minutes, "prep_time_minutes")
    normalized_difficulty = sanitize_difficulty(difficulty)
    if not title.strip() or not instructions.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Title and instructions are required.")
    recipe = Recipe(
        title=title.strip(),
        title_image_url=normalize_image_url(title_image_url),
        source="admin_manual",
        description=description.strip(),
        instructions=instructions.strip(),
        category=resolve_category_value(category_select, category_new, category),
        prep_time_minutes=prep_time,
        difficulty=normalized_difficulty,
        creator_id=current_user.id,
        is_published=True,
    )
    db.add(recipe)
    db.flush()
    ingredient_entries = parse_ingredient_text(ingredients_text)
    replace_recipe_ingredients(db, recipe, ingredient_entries)
    if image and image.filename:
        data = await image.read()
        try:
            validate_image_upload((image.content_type or "").lower(), data)
        except ImageValidationError as exc:
            raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc
        image_content_type = (image.content_type or "application/octet-stream").lower()
        db.add(
            RecipeImage(
                recipe_id=recipe.id,
                filename=safe_image_filename(image.filename or "", image_content_type),
                content_type=image_content_type,
                data=data,
                is_primary=True,
            )
        )
    db.commit()
    return redirect(f"/recipes/{recipe.id}")


@router.get("/recipes/{recipe_id}")
def recipe_detail(
    request: Request,
    recipe_id: int,
    message: str = "",
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    recipe = fetch_recipe_or_404(db, recipe_id)
    ensure_recipe_visible(recipe, current_user)
    avg_rating = db.scalar(select(func.coalesce(func.avg(Review.rating), 0)).where(Review.recipe_id == recipe_id)) or 0
    review_count = db.scalar(select(func.count(Review.id)).where(Review.recipe_id == recipe_id)) or 0
    requested_language = get_request_language(request)
    translation = load_recipe_translations(db, [int(recipe.id)], requested_language).get(int(recipe.id))
    display_fields = get_recipe_display_fields(recipe, translation)
    display_ingredients_lines = [
        line.strip()
        for line in str(display_fields["ingredients_text"] or "").splitlines()
        if line.strip()
    ]
    primary_image = get_primary_image(recipe)
    display_image_url, display_image_kind = resolve_recipe_display_image(recipe, primary_image)
    is_favorite = False
    if current_user:
        is_favorite = db.scalar(
            select(Favorite).where(and_(Favorite.user_id == current_user.id, Favorite.recipe_id == recipe_id))
        ) is not None
    message_map = {
        "image_change_submitted": t("images.request_submitted", request=request),
        "image_upload_done": t("images.uploaded", request=request),
    }
    return templates.TemplateResponse(
        "recipe_detail.html",
        template_context(
            request,
            current_user,
            recipe=recipe,
            display_title=display_fields["title"],
            display_description=display_fields["description"],
            display_instructions=display_fields["instructions"],
            display_ingredients_lines=display_ingredients_lines,
            avg_rating=float(avg_rating),
            review_count=int(review_count),
            is_favorite=is_favorite,
            primary_image=primary_image,
            display_image_url=display_image_url,
            display_image_kind=display_image_kind,
            can_upload_direct=can_direct_upload(current_user),
            can_request_change=can_request_image_change(current_user),
            has_pending_change_request=user_has_pending_image_request(db, recipe_id, current_user),
            image_feedback_message=message_map.get(message, ""),
            image_feedback_error="",
        ),
    )


@router.get("/recipes/{recipe_id}/edit")
def edit_recipe_page(
    request: Request,
    recipe_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    recipe = fetch_recipe_or_404(db, recipe_id)
    ensure_recipe_access(current_user, recipe)
    selected_category = normalize_category(recipe.category)
    category_options = get_distinct_categories(db)
    if selected_category not in category_options:
        category_options = sorted([*category_options, selected_category], key=str.casefold)
    ingredients_text = "\n".join(
        f"{link.ingredient.name}|{link.quantity_text}|{link.grams or ''}".rstrip("|")
        for link in recipe.recipe_ingredients
    )
    return templates.TemplateResponse(
        "recipe_form.html",
        template_context(
            request,
            current_user,
            recipe=recipe,
            ingredients_text=ingredients_text,
            error=None,
            form_mode="edit",
            category_options=category_options,
            selected_category=selected_category,
            category_new_value="",
        ),
    )


@router.post("/recipes/{recipe_id}/edit")
async def edit_recipe_submit(
    recipe_id: int,
    title: str = Form(...),
    description: str = Form(...),
    instructions: str = Form(...),
    category_select: str = Form(DEFAULT_CATEGORY),
    category_new: str = Form(""),
    category: str = Form(""),
    title_image_url: str = Form(""),
    prep_time_minutes: str = Form(...),
    difficulty: str = Form(...),
    ingredients_text: str = Form(""),
    image: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    recipe = fetch_recipe_or_404(db, recipe_id)
    ensure_recipe_access(current_user, recipe)
    recipe.title = title.strip()
    recipe.title_image_url = normalize_image_url(title_image_url)
    recipe.description = description.strip()
    recipe.instructions = instructions.strip()
    recipe.category = resolve_category_value(category_select, category_new, category)
    recipe.prep_time_minutes = parse_positive_int(prep_time_minutes, "prep_time_minutes")
    recipe.difficulty = sanitize_difficulty(difficulty)
    replace_recipe_ingredients(db, recipe, parse_ingredient_text(ingredients_text))
    if image and image.filename:
        data = await image.read()
        try:
            validate_image_upload((image.content_type or "").lower(), data)
        except ImageValidationError as exc:
            raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc
        image_content_type = (image.content_type or "application/octet-stream").lower()
        has_images = db.scalar(select(func.count()).select_from(RecipeImage).where(RecipeImage.recipe_id == recipe.id)) or 0
        db.add(
            RecipeImage(
                recipe_id=recipe.id,
                filename=safe_image_filename(image.filename or "", image_content_type),
                content_type=image_content_type,
                data=data,
                is_primary=has_images == 0,
            )
        )
    db.commit()
    return redirect(f"/recipes/{recipe.id}")


@router.post("/recipes/{recipe_id}/delete")
def delete_recipe(
    recipe_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    recipe = fetch_recipe_or_404(db, recipe_id)
    ensure_recipe_access(current_user, recipe)
    db.delete(recipe)
    db.commit()
    return redirect("/my-recipes")


@router.post("/recipes/{recipe_id}/reviews")
def upsert_review(
    recipe_id: int,
    rating: int = Form(...),
    comment: str = Form(""),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    recipe = db.scalar(select(Recipe).where(Recipe.id == recipe_id))
    if not recipe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found.")
    if not recipe.is_published:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found.")
    if rating < 1 or rating > 5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Rating must be between 1 and 5.")
    review = db.scalar(select(Review).where(and_(Review.recipe_id == recipe_id, Review.user_id == current_user.id)))
    if review:
        review.rating = rating
        review.comment = comment.strip()
    else:
        db.add(Review(recipe_id=recipe_id, user_id=current_user.id, rating=rating, comment=comment.strip()))
    db.commit()
    return redirect(f"/recipes/{recipe_id}")


@router.post("/reviews/{review_id}/delete")
def delete_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    review = db.scalar(select(Review).where(Review.id == review_id).options(joinedload(Review.recipe)))
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found.")
    if current_user.role != "admin" and review.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions for this review.")
    recipe_id = review.recipe_id
    db.delete(review)
    db.commit()
    return redirect(f"/recipes/{recipe_id}")


@router.post("/recipes/{recipe_id}/favorite")
def toggle_favorite(
    request: Request,
    recipe_id: int,
    favorite_box_id: str = Form("favorite-box"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    recipe = db.scalar(select(Recipe).where(Recipe.id == recipe_id))
    if not recipe or not recipe.is_published:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found.")
    favorite = db.scalar(
        select(Favorite).where(and_(Favorite.user_id == current_user.id, Favorite.recipe_id == recipe_id))
    )
    is_favorite = True
    if favorite:
        db.delete(favorite)
        is_favorite = False
    else:
        db.add(Favorite(user_id=current_user.id, recipe_id=recipe_id))
        is_favorite = True
    db.commit()
    if request.headers.get("HX-Request") == "true":
        safe_box_id = sanitize_dom_id(favorite_box_id, fallback=f"favorite-box-card-{recipe_id}")
        return templates.TemplateResponse(
            "partials/favorite_button.html",
            template_context(
                request,
                current_user,
                recipe=recipe,
                is_favorite=is_favorite,
                favorite_box_id=safe_box_id,
            ),
        )
    return redirect(f"/recipes/{recipe_id}")


@router.get("/favorites")
def favorites_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    favorite_recipes = db.scalars(
        select(Recipe)
        .join(Favorite, Favorite.recipe_id == Recipe.id)
        .where(Favorite.user_id == current_user.id, Recipe.is_published.is_(True))
        .order_by(Recipe.created_at.desc())
        .options(selectinload(Recipe.images))
    ).all()
    return templates.TemplateResponse(
        "favorites.html",
        template_context(request, current_user, favorite_recipes=favorite_recipes),
    )


@router.get("/my-recipes")
def my_recipes_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = select(Recipe).order_by(Recipe.created_at.desc()).options(selectinload(Recipe.images))
    if current_user.role != "admin":
        stmt = stmt.where(Recipe.creator_id == current_user.id)
    recipes = db.scalars(stmt).all()
    return templates.TemplateResponse(
        "my_recipes.html",
        template_context(request, current_user, recipes=recipes),
    )


@router.post("/recipes/{recipe_id}/images")
@limiter.limit("10/minute", key_func=key_by_user_or_ip)
async def upload_recipe_image(
    request: Request,
    response: Response,
    recipe_id: int,
    set_primary: bool = Form(False),
    response_mode: str = Form("detail"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _ = response
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=t("error.admin_required", request=request))
    recipe = fetch_recipe_or_404(db, recipe_id)
    data = await file.read()
    content_type = (file.content_type or "").lower()
    try:
        validate_image_upload(content_type, data)
    except ImageValidationError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc
    has_images = db.scalar(select(func.count()).select_from(RecipeImage).where(RecipeImage.recipe_id == recipe_id)) or 0
    query_value = request.query_params.get("set_primary")
    if query_value is not None:
        set_primary = query_value.strip().lower() in {"1", "true", "yes", "on"}
    new_is_primary = set_primary or has_images == 0
    recipe_image = RecipeImage(
        recipe_id=recipe_id,
        filename=safe_image_filename(file.filename or "", content_type),
        content_type=content_type,
        data=data,
        is_primary=new_is_primary,
    )
    db.add(recipe_image)
    db.flush()
    if new_is_primary:
        set_recipe_primary_image(db, recipe, recipe_image.id)
    db.commit()
    if request.headers.get("HX-Request") == "true":
        if response_mode == "card":
            return render_recipe_card_image(
                request,
                db,
                recipe_id,
                current_user,
                feedback_message=t("images.uploaded", request=request),
            )
        return render_image_section(
            request,
            db,
            recipe_id,
            current_user,
            feedback_message=t("images.uploaded", request=request),
        )
    return redirect(f"/recipes/{recipe_id}?message=image_upload_done")


@router.post("/recipes/{recipe_id}/image-change-request")
@limiter.limit("10/minute", key_func=key_by_ip)
@limiter.limit("5/minute", key_func=key_by_user_or_ip)
async def request_recipe_image_change(
    request: Request,
    response: Response,
    recipe_id: int,
    response_mode: str = Form("detail"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _ = response
    if current_user.role == "admin":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=t("images.admin_use_direct_upload", request=request),
        )
    recipe = fetch_recipe_or_404(db, recipe_id)
    if not recipe.is_published:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=t("error.recipe_not_found", request=request))
    data = await file.read()
    content_type = (file.content_type or "").lower()
    try:
        validate_image_upload(content_type, data)
    except ImageValidationError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc
    change_request = RecipeImageChangeRequest(
        recipe_id=recipe_id,
        requester_user_id=current_user.id,
        status="pending",
    )
    db.add(change_request)
    db.flush()
    db.add(
        RecipeImageChangeFile(
            request_id=change_request.id,
            filename=safe_image_filename(file.filename or "", content_type),
            content_type=content_type,
            data=data,
        )
    )
    db.commit()
    if request.headers.get("HX-Request") == "true":
        if response_mode == "card":
            return render_recipe_card_image(
                request,
                db,
                recipe_id,
                current_user,
                feedback_message=t("images.request_submitted", request=request),
            )
        return render_image_section(
            request,
            db,
            recipe_id,
            current_user,
            feedback_message=t("images.request_submitted", request=request),
        )
    return redirect(f"/recipes/{recipe_id}?message=image_change_submitted")


@router.get("/images/{image_id}")
def get_image(image_id: int, db: Session = Depends(get_db)):
    image = db.scalar(select(RecipeImage).where(RecipeImage.id == image_id))
    if not image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=t("error.image_not_found"))
    return Response(
        content=image.data,
        media_type=image.content_type,
        headers={"Cache-Control": "public, max-age=86400"},
    )


@router.get("/external-image")
def external_image(url: str):
    try:
        resolved_url = resolve_title_image_url(url)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Could not resolve image URL: {exc}") from exc
    if not resolved_url:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No image URL available.")
    return RedirectResponse(url=resolved_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)


@router.delete("/images/{image_id}")
def delete_image_api(
    image_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    image = db.scalar(select(RecipeImage).where(RecipeImage.id == image_id).options(joinedload(RecipeImage.recipe)))
    if not image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=t("error.image_not_found"))
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=t("error.admin_required"))
    recipe = image.recipe
    db.delete(image)
    db.flush()
    maybe_promote_primary_after_delete(db, recipe)
    db.commit()
    return {"status": "deleted"}


@router.post("/images/{image_id}/delete")
def delete_image_form(
    request: Request,
    image_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    image = db.scalar(select(RecipeImage).where(RecipeImage.id == image_id).options(joinedload(RecipeImage.recipe)))
    if not image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=t("error.image_not_found"))
    recipe = image.recipe
    recipe_id = image.recipe_id
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=t("error.admin_required"))
    db.delete(image)
    db.flush()
    maybe_promote_primary_after_delete(db, recipe)
    db.commit()
    if request.headers.get("HX-Request") == "true":
        return render_image_section(request, db, recipe_id, current_user)
    return redirect(f"/recipes/{recipe_id}")


@router.post("/images/{image_id}/set-primary")
def set_primary_image(
    request: Request,
    image_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    image = db.scalar(select(RecipeImage).where(RecipeImage.id == image_id).options(joinedload(RecipeImage.recipe)))
    if not image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=t("error.image_not_found"))
    recipe = image.recipe
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=t("error.admin_required"))
    set_recipe_primary_image(db, recipe, image.id)
    db.commit()
    if request.headers.get("HX-Request") == "true":
        return render_image_section(request, db, recipe.id, current_user)
    return redirect(f"/recipes/{recipe.id}")


@router.get("/recipes/{recipe_id}/pdf")
@limiter.limit("20/minute", key_func=key_by_user_or_ip)
def recipe_pdf(
    request: Request,
    recipe_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _ = request
    recipe = fetch_recipe_or_404(db, recipe_id)
    ensure_recipe_visible(recipe, current_user)
    avg_rating = db.scalar(select(func.coalesce(func.avg(Review.rating), 0)).where(Review.recipe_id == recipe_id)) or 0
    review_count = db.scalar(select(func.count(Review.id)).where(Review.recipe_id == recipe_id)) or 0
    pdf_bytes = build_recipe_pdf(recipe, float(avg_rating), int(review_count))
    filename = f"mealmate_recipe_{recipe_id}.pdf"
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return StreamingResponse(BytesIO(pdf_bytes), media_type="application/pdf", headers=headers)


@router.get("/categories")
def categories_api(db: Session = Depends(get_db)):
    return {"categories": get_distinct_categories(db, only_published=True)}
