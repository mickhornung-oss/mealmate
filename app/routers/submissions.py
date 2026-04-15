from datetime import datetime, timezone

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, Response, UploadFile, status
from fastapi.responses import Response as RawResponse
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.database import get_db
from app.dependencies import get_admin_user, get_current_user, get_current_user_optional, template_context
from app.image_utils import ImageValidationError, safe_image_filename, validate_image_upload
from app.i18n import t
from app.models import RecipeSubmission, SubmissionImage, User
from app.rate_limit import key_by_user_or_ip, limiter
from app.services import (
    DEFAULT_CATEGORY,
    build_submission_ingredients_text,
    get_distinct_categories,
    get_submission_status_stats,
    normalize_category,
    parse_ingredient_text,
    publish_submission_as_recipe,
    replace_submission_ingredients,
    sanitize_difficulty,
)
from app.views import redirect, templates

router = APIRouter(tags=["submissions"])

SUBMISSION_PAGE_SIZE = 20


def parse_optional_positive_int(value: str, field_name: str) -> int | None:
    cleaned = value.strip()
    if not cleaned:
        return None
    try:
        parsed = int(cleaned)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=t("error.field_int", field=field_name)) from exc
    if parsed <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=t("error.field_positive", field=field_name))
    return parsed


def resolve_category_value(category_select: str, category_new: str, category_legacy: str = "") -> str:
    if category_select and category_select != "__new__":
        return normalize_category(category_select)
    if category_new.strip():
        return normalize_category(category_new)
    if category_legacy.strip():
        return normalize_category(category_legacy)
    return DEFAULT_CATEGORY


def submission_limit_value(key: str) -> str:
    actor = key or ""
    if actor.startswith("user:"):
        return "10/minute"
    return "3/minute"


def pagination_items(page: int, total_pages: int) -> list[int | None]:
    if total_pages <= 7:
        return list(range(1, total_pages + 1))
    if page <= 4:
        return [1, 2, 3, 4, 5, None, total_pages]
    if page >= total_pages - 3:
        return [1, None, total_pages - 4, total_pages - 3, total_pages - 2, total_pages - 1, total_pages]
    return [1, None, page - 1, page, page + 1, None, total_pages]


def submission_form_context(
    request: Request,
    db: Session,
    current_user: User | None,
    **overrides,
):
    category_options = get_distinct_categories(db)
    base_context = {
        "title_value": "",
        "description_value": "",
        "instructions_value": "",
        "ingredients_text": "",
        "prep_time_value": "",
        "servings_value": "",
        "difficulty_value": "medium",
        "selected_category": DEFAULT_CATEGORY,
        "category_new_value": "",
        "submitter_email_value": "",
        "error": None,
        "message": None,
        "category_options": category_options,
    }
    base_context.update(overrides)
    return template_context(request, current_user, **base_context)


def fetch_submission_or_404(db: Session, submission_id: int) -> RecipeSubmission:
    submission = db.scalar(
        select(RecipeSubmission)
        .where(RecipeSubmission.id == submission_id)
        .options(
            joinedload(RecipeSubmission.submitter_user),
            joinedload(RecipeSubmission.reviewed_by_admin),
            selectinload(RecipeSubmission.ingredients),
            selectinload(RecipeSubmission.images),
        )
    )
    if not submission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=t("error.submission_not_found"))
    return submission


def set_submission_primary(submission: RecipeSubmission, image_id: int) -> None:
    for image in submission.images:
        image.is_primary = image.id == image_id


def ensure_submission_primary(submission: RecipeSubmission) -> None:
    if not submission.images:
        return
    if any(image.is_primary for image in submission.images):
        return
    submission.images[0].is_primary = True


@router.get("/submit")
def submit_recipe_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    return templates.TemplateResponse(
        "submit_recipe.html",
        submission_form_context(request, db, current_user),
    )


@router.post("/submit")
@limiter.limit(submission_limit_value, key_func=key_by_user_or_ip)
async def submit_recipe(
    request: Request,
    response: Response,
    submitter_email: str = Form(""),
    title: str = Form(...),
    description: str = Form(""),
    instructions: str = Form(...),
    category_select: str = Form(DEFAULT_CATEGORY),
    category_new: str = Form(""),
    category: str = Form(""),
    difficulty: str = Form("medium"),
    prep_time_minutes: str = Form(""),
    servings_text: str = Form(""),
    ingredients_text: str = Form(""),
    image: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    _ = response
    normalized_title = title.strip()
    normalized_instructions = instructions.strip()
    if not normalized_title or not normalized_instructions:
        return templates.TemplateResponse(
            "submit_recipe.html",
            submission_form_context(
                request,
                db,
                current_user,
                title_value=title,
                description_value=description,
                instructions_value=instructions,
                ingredients_text=ingredients_text,
                prep_time_value=prep_time_minutes,
                servings_value=servings_text,
                difficulty_value=sanitize_difficulty(difficulty),
                selected_category=resolve_category_value(category_select, category_new, category),
                category_new_value=category_new,
                submitter_email_value=submitter_email,
                error=t("error.title_instructions_required"),
            ),
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    try:
        prep_time_value = parse_optional_positive_int(prep_time_minutes, "prep_time_minutes")
    except HTTPException as exc:
        return templates.TemplateResponse(
            "submit_recipe.html",
            submission_form_context(
                request,
                db,
                current_user,
                title_value=title,
                description_value=description,
                instructions_value=instructions,
                ingredients_text=ingredients_text,
                prep_time_value=prep_time_minutes,
                servings_value=servings_text,
                difficulty_value=sanitize_difficulty(difficulty),
                selected_category=resolve_category_value(category_select, category_new, category),
                category_new_value=category_new,
                submitter_email_value=submitter_email,
                error=str(exc.detail),
            ),
            status_code=exc.status_code,
        )
    resolved_category = resolve_category_value(category_select, category_new, category)
    submission = RecipeSubmission(
        submitter_user_id=current_user.id if current_user else None,
        submitter_email=(submitter_email.strip().lower()[:255] or None) if not current_user else None,
        title=normalized_title[:255],
        description=description.strip() or t("submission.default_description"),
        category=resolved_category,
        difficulty=sanitize_difficulty(difficulty),
        prep_time_minutes=prep_time_value,
        servings_text=servings_text.strip()[:120] or None,
        instructions=normalized_instructions,
        status="pending",
    )
    db.add(submission)
    db.flush()
    replace_submission_ingredients(db, submission, parse_ingredient_text(ingredients_text))
    if image and image.filename:
        data = await image.read()
        content_type = (image.content_type or "").lower()
        try:
            validate_image_upload(content_type, data)
        except ImageValidationError as exc:
            raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc
        db.add(
            SubmissionImage(
                submission_id=submission.id,
                filename=safe_image_filename(image.filename or "", content_type),
                content_type=content_type,
                data=data,
                is_primary=True,
            )
        )
    db.commit()
    if current_user:
        return redirect("/my-submissions?submitted=1")
    return templates.TemplateResponse(
        "submit_recipe.html",
        submission_form_context(request, db, current_user, message=t("submission.thank_you")),
        status_code=status.HTTP_201_CREATED,
    )


@router.get("/my-submissions")
def my_submissions_page(
    request: Request,
    page: int = 1,
    submitted: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    page = max(page, 1)
    stmt = (
        select(RecipeSubmission)
        .where(RecipeSubmission.submitter_user_id == current_user.id)
        .order_by(RecipeSubmission.created_at.desc())
        .options(selectinload(RecipeSubmission.images), joinedload(RecipeSubmission.reviewed_by_admin))
    )
    total_count = db.scalar(
        select(func.count()).select_from(RecipeSubmission).where(RecipeSubmission.submitter_user_id == current_user.id)
    )
    total_count = int(total_count or 0)
    total_pages = max((total_count + SUBMISSION_PAGE_SIZE - 1) // SUBMISSION_PAGE_SIZE, 1)
    page = min(page, total_pages)
    submissions = db.scalars(stmt.offset((page - 1) * SUBMISSION_PAGE_SIZE).limit(SUBMISSION_PAGE_SIZE)).all()
    return templates.TemplateResponse(
        "my_submissions.html",
        template_context(
            request,
            current_user,
            submissions=submissions,
            page=page,
            total_pages=total_pages,
            total_count=total_count,
            pagination_items=pagination_items(page, total_pages),
            submitted=bool(submitted),
        ),
    )


@router.get("/admin/submissions")
def admin_submissions_queue(
    request: Request,
    status_filter: str = "pending",
    page: int = 1,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    page = max(page, 1)
    valid_statuses = {"pending", "approved", "rejected", "all"}
    if status_filter not in valid_statuses:
        status_filter = "pending"
    stmt = (
        select(RecipeSubmission)
        .order_by(RecipeSubmission.created_at.desc())
        .options(joinedload(RecipeSubmission.submitter_user), joinedload(RecipeSubmission.reviewed_by_admin))
    )
    count_stmt = select(func.count()).select_from(RecipeSubmission)
    if status_filter != "all":
        stmt = stmt.where(RecipeSubmission.status == status_filter)
        count_stmt = count_stmt.where(RecipeSubmission.status == status_filter)
    total_count = db.scalar(count_stmt)
    total_count = int(total_count or 0)
    total_pages = max((total_count + SUBMISSION_PAGE_SIZE - 1) // SUBMISSION_PAGE_SIZE, 1)
    page = min(page, total_pages)
    submissions = db.scalars(stmt.offset((page - 1) * SUBMISSION_PAGE_SIZE).limit(SUBMISSION_PAGE_SIZE)).all()
    return templates.TemplateResponse(
        "admin_submissions.html",
        template_context(
            request,
            current_user,
            submissions=submissions,
            status_filter=status_filter,
            page=page,
            total_pages=total_pages,
            total_count=total_count,
            pagination_items=pagination_items(page, total_pages),
            status_stats=get_submission_status_stats(db),
        ),
    )


@router.get("/admin/submissions/{submission_id}")
def admin_submission_detail(
    request: Request,
    submission_id: int,
    message: str = "",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    submission = fetch_submission_or_404(db, submission_id)
    category_options = get_distinct_categories(db)
    selected_category = normalize_category(submission.category)
    if selected_category not in category_options:
        category_options = sorted([*category_options, selected_category], key=str.casefold)
    message_map = {
        "updated": t("submission.updated"),
        "approved": t("submission.approved"),
        "rejected": t("submission.rejected"),
        "image_deleted": t("submission.image_deleted"),
        "image_primary": t("submission.image_primary"),
    }
    return templates.TemplateResponse(
        "admin_submission_detail.html",
        template_context(
            request,
            current_user,
            submission=submission,
            category_options=category_options,
            selected_category=selected_category,
            ingredients_text=build_submission_ingredients_text(submission.ingredients),
            message=message_map.get(message, ""),
        ),
    )


@router.post("/admin/submissions/{submission_id}/edit")
@limiter.limit("30/minute", key_func=key_by_user_or_ip)
async def admin_submission_edit(
    request: Request,
    submission_id: int,
    title: str = Form(...),
    description: str = Form(""),
    instructions: str = Form(...),
    category_select: str = Form(DEFAULT_CATEGORY),
    category_new: str = Form(""),
    category: str = Form(""),
    difficulty: str = Form("medium"),
    prep_time_minutes: str = Form(""),
    servings_text: str = Form(""),
    ingredients_text: str = Form(""),
    set_primary_new_image: bool = Form(False),
    image: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    submission = fetch_submission_or_404(db, submission_id)
    if submission.status == "approved":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=t("error.submission_already_published"))
    normalized_title = title.strip()
    normalized_instructions = instructions.strip()
    if not normalized_title or not normalized_instructions:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=t("error.title_instructions_required"))
    prep_time_value = parse_optional_positive_int(prep_time_minutes, "prep_time_minutes")
    submission.title = normalized_title[:255]
    submission.description = description.strip() or t("submission.default_description")
    submission.instructions = normalized_instructions
    submission.category = resolve_category_value(category_select, category_new, category)
    submission.difficulty = sanitize_difficulty(difficulty)
    submission.prep_time_minutes = prep_time_value
    submission.servings_text = servings_text.strip()[:120] or None
    replace_submission_ingredients(db, submission, parse_ingredient_text(ingredients_text))
    if image and image.filename:
        data = await image.read()
        content_type = (image.content_type or "").lower()
        try:
            validate_image_upload(content_type, data)
        except ImageValidationError as exc:
            raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc
        make_primary = set_primary_new_image or not submission.images
        submission_image = SubmissionImage(
            submission_id=submission.id,
            filename=safe_image_filename(image.filename or "", content_type),
            content_type=content_type,
            data=data,
            is_primary=make_primary,
        )
        db.add(submission_image)
        db.flush()
        if make_primary:
            set_submission_primary(submission, submission_image.id)
    ensure_submission_primary(submission)
    db.commit()
    _ = request
    _ = current_user
    return redirect(f"/admin/submissions/{submission_id}?message=updated")


@router.post("/admin/submissions/{submission_id}/approve")
@limiter.limit("30/minute", key_func=key_by_user_or_ip)
def admin_submission_approve(
    request: Request,
    submission_id: int,
    admin_note: str = Form(""),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    submission = fetch_submission_or_404(db, submission_id)
    if submission.status == "approved":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=t("error.submission_already_published"))
    recipe = publish_submission_as_recipe(db, submission, current_user.id)
    submission.status = "approved"
    submission.admin_note = admin_note.strip() or None
    submission.reviewed_by_admin_id = current_user.id
    submission.reviewed_at = datetime.now(timezone.utc)
    db.commit()
    _ = request
    return redirect(f"/admin/submissions/{submission_id}?message=approved&recipe_id={recipe.id}")


@router.post("/admin/submissions/{submission_id}/reject")
@limiter.limit("30/minute", key_func=key_by_user_or_ip)
def admin_submission_reject(
    request: Request,
    submission_id: int,
    admin_note: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    submission = fetch_submission_or_404(db, submission_id)
    if submission.status == "approved":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=t("error.submission_already_published"))
    if not admin_note.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=t("error.submission_reject_reason_required"))
    submission.status = "rejected"
    submission.admin_note = admin_note.strip()
    submission.reviewed_by_admin_id = current_user.id
    submission.reviewed_at = datetime.now(timezone.utc)
    db.commit()
    _ = request
    return redirect(f"/admin/submissions/{submission_id}?message=rejected")


@router.post("/admin/submissions/images/{image_id}/set-primary")
@limiter.limit("30/minute", key_func=key_by_user_or_ip)
def admin_submission_image_set_primary(
    request: Request,
    image_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    image = db.scalar(
        select(SubmissionImage)
        .where(SubmissionImage.id == image_id)
        .options(joinedload(SubmissionImage.submission).selectinload(RecipeSubmission.images))
    )
    if not image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=t("error.image_not_found"))
    submission = image.submission
    set_submission_primary(submission, image.id)
    db.commit()
    _ = request
    _ = current_user
    return redirect(f"/admin/submissions/{submission.id}?message=image_primary")


@router.post("/admin/submissions/images/{image_id}/delete")
@limiter.limit("30/minute", key_func=key_by_user_or_ip)
def admin_submission_image_delete(
    request: Request,
    image_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    image = db.scalar(
        select(SubmissionImage)
        .where(SubmissionImage.id == image_id)
        .options(joinedload(SubmissionImage.submission).selectinload(RecipeSubmission.images))
    )
    if not image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=t("error.image_not_found"))
    submission = image.submission
    submission_id = submission.id
    db.delete(image)
    db.flush()
    ensure_submission_primary(submission)
    db.commit()
    _ = request
    _ = current_user
    return redirect(f"/admin/submissions/{submission_id}?message=image_deleted")


@router.get("/submission-images/{image_id}")
def get_submission_image(
    image_id: int,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    image = db.scalar(select(SubmissionImage).where(SubmissionImage.id == image_id).options(joinedload(SubmissionImage.submission)))
    if not image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=t("error.image_not_found"))
    submission = image.submission
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=t("error.auth_required"))
    if current_user.role != "admin" and submission.submitter_user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=t("error.submission_permission"))
    return RawResponse(content=image.data, media_type=image.content_type)
