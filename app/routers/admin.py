import logging
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, Request, Response, UploadFile, status
from fastapi.responses import Response as RawResponse
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.category_canonical import build_category_qa_rows, rebuild_canonical_categories, validate_mapping_pattern
from app.config import get_settings
from app.csv_import import build_csv_example_bytes, build_csv_template_bytes, import_admin_csv
from app.database import get_db
from app.dependencies import get_admin_user, template_context
from app.i18n import t
from app.models import CategoryMapping, Recipe, RecipeImage, RecipeImageChangeFile, RecipeImageChangeRequest, User
from app.rate_limit import key_by_user_or_ip, limiter
from app.services import (
    STANDARD_CANONICAL_CATEGORIES,
    get_category_stats,
    get_raw_category_overview,
    import_kochwiki_csv,
    is_meta_true,
    normalize_canonical_category,
    set_meta_value,
)
from app.translation_service import audit_german_translations
from app.views import redirect, templates

router = APIRouter(tags=["admin"])
settings = get_settings()
logger = logging.getLogger("mealmate.admin")
IMAGE_CHANGE_PAGE_SIZE = 20


def get_recipe_primary_image(recipe: Recipe) -> RecipeImage | None:
    for image in recipe.images:
        if image.is_primary:
            return image
    return recipe.images[0] if recipe.images else None


def get_recipe_external_image_url(recipe: Recipe) -> str | None:
    if recipe.source_image_url:
        return recipe.source_image_url
    if recipe.title_image_url:
        return recipe.title_image_url
    return None


def fetch_image_change_request_or_404(db: Session, request_id: int) -> RecipeImageChangeRequest:
    image_change_request = db.scalar(
        select(RecipeImageChangeRequest)
        .where(RecipeImageChangeRequest.id == request_id)
        .options(
            joinedload(RecipeImageChangeRequest.recipe).selectinload(Recipe.images),
            joinedload(RecipeImageChangeRequest.requester_user),
            joinedload(RecipeImageChangeRequest.reviewed_by_admin),
            selectinload(RecipeImageChangeRequest.files),
        )
    )
    if not image_change_request:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=t("error.image_change_request_not_found"))
    return image_change_request


def admin_dashboard_context(
    request: Request,
    db: Session,
    current_user: User,
    report=None,
    preview_report=None,
    error: str | None = None,
    message: str | None = None,
    import_mode: str = "insert_only",
    import_dry_run: bool = False,
    import_force_with_warnings: bool = False,
):
    users = db.scalars(select(User).order_by(User.created_at.desc())).all()
    recipes = db.scalars(
        select(Recipe).order_by(Recipe.created_at.desc()).options(selectinload(Recipe.creator))
    ).all()
    pending_image_change_requests = db.scalars(
        select(RecipeImageChangeRequest)
        .where(RecipeImageChangeRequest.status == "pending")
        .order_by(RecipeImageChangeRequest.created_at.desc())
        .limit(8)
        .options(
            joinedload(RecipeImageChangeRequest.recipe),
            joinedload(RecipeImageChangeRequest.requester_user),
        )
    ).all()
    pending_image_change_count = db.scalar(
        select(func.count()).select_from(RecipeImageChangeRequest).where(RecipeImageChangeRequest.status == "pending")
    )
    pending_image_change_count = int(pending_image_change_count or 0)
    de_audit = audit_german_translations(db, limit=5, persist_flags=False)
    distinct_category_count, top_categories = get_category_stats(db, limit=10)
    logger.info(
        "category_stats distinct=%s top=%s",
        distinct_category_count,
        top_categories,
    )
    return template_context(
        request,
        current_user,
        users=users,
        recipes=recipes,
        report=report,
        preview_report=preview_report,
        error=error,
        message=message,
        import_mode=import_mode,
        import_dry_run=import_dry_run,
        import_force_with_warnings=import_force_with_warnings,
        distinct_category_count=distinct_category_count,
        top_categories=top_categories,
        pending_image_change_count=pending_image_change_count,
        pending_image_change_requests=pending_image_change_requests,
        suspect_de_translation_count=de_audit.suspect_count,
    )


@router.get("/admin")
def admin_panel(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    return templates.TemplateResponse("admin.html", admin_dashboard_context(request, db, current_user))


@router.get("/admin/categories")
def admin_categories_page(
    request: Request,
    updated: int = 0,
    skipped: int = 0,
    suspicious_count: int = 0,
    mode: str = "full",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    mappings = db.scalars(
        select(CategoryMapping).order_by(CategoryMapping.priority.asc(), CategoryMapping.id.asc())
    ).all()
    raw_overview = get_raw_category_overview(db, limit=40)
    rebuild_mode = mode if mode in {"full", "suspicious"} else "full"
    rebuild_report = {
        "updated": int(updated or 0),
        "skipped": int(skipped or 0),
        "mode": rebuild_mode,
        "suspicious_count": int(suspicious_count or 0),
    }
    return templates.TemplateResponse(
        "admin_categories.html",
        template_context(
            request,
            current_user,
            category_mappings=mappings,
            raw_category_overview=raw_overview,
            standard_canonical_categories=STANDARD_CANONICAL_CATEGORIES,
            rebuild_mode=rebuild_mode,
            rebuild_report=rebuild_report if (updated or skipped) else None,
        ),
    )


@router.get("/admin/categories/qa")
def admin_categories_qa_page(
    request: Request,
    limit: int = Query(200, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    qa_rows = build_category_qa_rows(db, limit=limit)
    return templates.TemplateResponse(
        "admin_categories_qa.html",
        template_context(
            request,
            current_user,
            qa_rows=qa_rows,
            limit=limit,
        ),
    )


@router.post("/admin/categories/mappings")
def admin_create_category_mapping(
    pattern: str = Form(...),
    canonical_category: str = Form(...),
    priority: int = Form(100),
    scope: str = Form("raw"),
    enabled: str | None = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    _ = current_user
    try:
        pattern_clean = validate_mapping_pattern(pattern)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    canonical_raw = " ".join(canonical_category.strip().split())
    upper = canonical_raw.upper()
    if upper in {"IGNORE", "__IGNORE__", "(IGNORE)"} or "IGNORE" in upper:
        canonical_clean = "__IGNORE__"
    else:
        canonical_clean = normalize_canonical_category(canonical_raw)
    priority_value = int(priority)
    if priority_value < 0:
        priority_value = 0
    scope_clean = scope.strip().lower()
    if scope_clean not in {"raw", "fulltext"}:
        scope_clean = "raw"
    mapping = CategoryMapping(
        pattern=pattern_clean[:120],
        canonical_category=canonical_clean,
        priority=priority_value,
        enabled=bool(enabled),
        scope=scope_clean,
    )
    db.add(mapping)
    db.commit()
    return redirect("/admin/categories")


@router.post("/admin/categories/mappings/{mapping_id}/toggle")
def admin_toggle_category_mapping(
    mapping_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    _ = current_user
    mapping = db.scalar(select(CategoryMapping).where(CategoryMapping.id == mapping_id))
    if not mapping:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mapping nicht gefunden.")
    mapping.enabled = not mapping.enabled
    db.commit()
    return redirect("/admin/categories")


@router.post("/admin/categories/rebuild")
def admin_rebuild_categories(
    mode: str = Query("full"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    _ = current_user
    rebuild_mode = mode if mode in {"full", "suspicious"} else "full"
    report = rebuild_canonical_categories(db, mode=rebuild_mode, batch_size=200)
    db.commit()
    return redirect(
        "/admin/categories"
        f"?updated={int(report['updated'])}"
        f"&skipped={int(report['skipped'])}"
        f"&mode={rebuild_mode}"
        f"&suspicious_count={int(report['suspicious_count'])}"
    )


@router.post("/admin/users/{user_id}/role")
def change_user_role(
    user_id: int,
    role: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    if role not in {"user", "admin"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=t("error.role_invalid"))
    user = db.scalar(select(User).where(User.id == user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=t("error.user_not_found"))
    user.role = role
    db.commit()
    return redirect("/admin")


@router.post("/admin/recipes/{recipe_id}/delete")
def delete_recipe_admin(
    recipe_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    recipe = db.scalar(select(Recipe).where(Recipe.id == recipe_id))
    if not recipe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=t("error.recipe_not_found"))
    db.delete(recipe)
    db.commit()
    return redirect("/admin")


@router.post("/admin/run-kochwiki-seed")
def run_kochwiki_seed(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    if not settings.enable_kochwiki_seed:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=t("error.not_found"))
    if is_meta_true(db, "kochwiki_seed_done"):
        return templates.TemplateResponse(
            "admin.html",
            admin_dashboard_context(request, db, current_user, error=t("error.seed_already_done")),
            status_code=status.HTTP_409_CONFLICT,
        )
    recipes_count = db.scalar(select(func.count()).select_from(Recipe)) or 0
    if recipes_count > 0:
        return templates.TemplateResponse(
            "admin.html",
            admin_dashboard_context(
                request,
                db,
                current_user,
                error=t("error.seed_not_empty"),
            ),
            status_code=status.HTTP_409_CONFLICT,
        )
    seed_path = Path(settings.kochwiki_csv_path)
    if not seed_path.exists():
        return templates.TemplateResponse(
            "admin.html",
            admin_dashboard_context(
                request,
                db,
                current_user,
                error=f"{t('error.csv_not_found_prefix')}: {seed_path}",
            ),
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    report = import_kochwiki_csv(db, seed_path, current_user.id, mode="insert_only")
    if report.errors:
        return templates.TemplateResponse(
            "admin.html",
            admin_dashboard_context(
                request,
                db,
                current_user,
                report=report,
                error=t("error.seed_finished_errors"),
            ),
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    set_meta_value(db, "kochwiki_seed_done", "1")
    db.commit()
    return templates.TemplateResponse(
        "admin.html",
        admin_dashboard_context(
            request,
            db,
            current_user,
            report=report,
            message=t("error.seed_success"),
        ),
    )


@router.post("/admin/import-recipes")
@limiter.limit("2/minute", key_func=key_by_user_or_ip)
async def import_recipes_admin(
    request: Request,
    response: Response,
    file: UploadFile | None = File(None),
    insert_only: str | None = Form("on"),
    update_existing: str | None = Form(None),
    dry_run: str | None = Form(None),
    force_with_warnings: str | None = Form(None),
    action: str = Form("preview"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    _ = response
    max_bytes = settings.max_csv_upload_mb * 1024 * 1024
    mode = "update_existing" if update_existing else "insert_only"
    dry_run_flag = bool(dry_run)
    force_warnings_flag = bool(force_with_warnings)
    if insert_only and mode != "update_existing":
        mode = "insert_only"
    try:
        if not file or not file.filename:
            raise ValueError(t("error.csv_upload_required"))
        if not file.filename.lower().endswith(".csv"):
            raise ValueError(t("error.csv_only"))
        raw_bytes = await file.read(max_bytes + 1)
        if len(raw_bytes) > max_bytes:
            raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail=t("error.csv_too_large"))
        if not raw_bytes:
            raise ValueError(t("error.csv_empty"))
        preview_report = import_admin_csv(
            db,
            raw_bytes,
            current_user.id,
            mode=mode,
            dry_run=True,
            autocommit=False,
        )
        if action == "preview":
            return templates.TemplateResponse(
                "admin.html",
                admin_dashboard_context(
                    request,
                    db,
                    current_user,
                    preview_report=preview_report,
                    message=t("admin.preview_done"),
                    import_mode=mode,
                    import_dry_run=dry_run_flag,
                    import_force_with_warnings=force_warnings_flag,
                ),
            )
        if preview_report.fatal_error_rows > 0:
            return templates.TemplateResponse(
                "admin.html",
                admin_dashboard_context(
                    request,
                    db,
                    current_user,
                    preview_report=preview_report,
                    error=t("admin.import_blocked_errors"),
                    import_mode=mode,
                    import_dry_run=dry_run_flag,
                    import_force_with_warnings=force_warnings_flag,
                ),
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        if dry_run_flag:
            return templates.TemplateResponse(
                "admin.html",
                admin_dashboard_context(
                    request,
                    db,
                    current_user,
                    preview_report=preview_report,
                    message=t("admin.dry_run_done"),
                    import_mode=mode,
                    import_dry_run=dry_run_flag,
                    import_force_with_warnings=force_warnings_flag,
                ),
            )
        if preview_report.warnings and not force_warnings_flag:
            return templates.TemplateResponse(
                "admin.html",
                admin_dashboard_context(
                    request,
                    db,
                    current_user,
                    preview_report=preview_report,
                    error=t("admin.confirm_warnings_required"),
                    import_mode=mode,
                    import_dry_run=dry_run_flag,
                    import_force_with_warnings=force_warnings_flag,
                ),
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        report = import_admin_csv(
            db,
            raw_bytes,
            current_user.id,
            mode=mode,
            dry_run=False,
            autocommit=False,
        )
        db.commit()
        message = t("error.import_finished_insert") if mode == "insert_only" else t("error.import_finished_update")
        return templates.TemplateResponse(
            "admin.html",
            admin_dashboard_context(
                request,
                db,
                current_user,
                report=report,
                preview_report=report,
                message=message,
                import_mode=mode,
                import_dry_run=dry_run_flag,
                import_force_with_warnings=force_warnings_flag,
            ),
        )
    except (FileNotFoundError, ValueError) as exc:
        db.rollback()
        return templates.TemplateResponse(
            "admin.html",
            admin_dashboard_context(
                request,
                db,
                current_user,
                error=str(exc),
                import_mode=mode,
                import_dry_run=dry_run_flag,
                import_force_with_warnings=force_warnings_flag,
            ),
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    except Exception:
        db.rollback()
        raise


@router.get("/admin/import-template.csv")
def admin_import_template_csv(current_user: User = Depends(get_admin_user)):
    _ = current_user
    content = build_csv_template_bytes()
    headers = {"Content-Disposition": 'attachment; filename="mealmate_import_template.csv"'}
    return RawResponse(content=content, media_type="text/csv; charset=utf-8", headers=headers)


@router.get("/admin/import-example.csv")
def admin_import_example_csv(current_user: User = Depends(get_admin_user)):
    _ = current_user
    content = build_csv_example_bytes()
    headers = {"Content-Disposition": 'attachment; filename="mealmate_import_beispiel.csv"'}
    return RawResponse(content=content, media_type="text/csv; charset=utf-8", headers=headers)


@router.get("/admin/image-change-requests")
def admin_image_change_requests(
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
        select(RecipeImageChangeRequest)
        .order_by(RecipeImageChangeRequest.created_at.desc())
        .options(
            joinedload(RecipeImageChangeRequest.recipe),
            joinedload(RecipeImageChangeRequest.requester_user),
            joinedload(RecipeImageChangeRequest.reviewed_by_admin),
            selectinload(RecipeImageChangeRequest.files),
        )
    )
    count_stmt = select(func.count()).select_from(RecipeImageChangeRequest)
    if status_filter != "all":
        stmt = stmt.where(RecipeImageChangeRequest.status == status_filter)
        count_stmt = count_stmt.where(RecipeImageChangeRequest.status == status_filter)
    total_count = int(db.scalar(count_stmt) or 0)
    total_pages = max((total_count + IMAGE_CHANGE_PAGE_SIZE - 1) // IMAGE_CHANGE_PAGE_SIZE, 1)
    page = min(page, total_pages)
    requests = db.scalars(stmt.offset((page - 1) * IMAGE_CHANGE_PAGE_SIZE).limit(IMAGE_CHANGE_PAGE_SIZE)).all()
    status_rows = db.execute(
        select(RecipeImageChangeRequest.status, func.count(RecipeImageChangeRequest.id)).group_by(
            RecipeImageChangeRequest.status
        )
    ).all()
    status_stats = {"pending": 0, "approved": 0, "rejected": 0}
    for row_status, count in status_rows:
        status_stats[str(row_status)] = int(count)
    return templates.TemplateResponse(
        "admin_image_change_requests.html",
        template_context(
            request,
            current_user,
            image_change_requests=requests,
            status_filter=status_filter,
            page=page,
            total_pages=total_pages,
            total_count=total_count,
            status_stats=status_stats,
        ),
    )


@router.get("/admin/image-change-requests/{request_id}")
def admin_image_change_request_detail(
    request: Request,
    request_id: int,
    message: str = "",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    image_change_request = fetch_image_change_request_or_404(db, request_id)
    recipe = image_change_request.recipe
    recipe_primary_image = get_recipe_primary_image(recipe)
    current_image_url = f"/images/{recipe_primary_image.id}" if recipe_primary_image else get_recipe_external_image_url(recipe)
    current_image_kind = "db" if recipe_primary_image else ("external" if current_image_url else "placeholder")
    proposed_file = image_change_request.files[0] if image_change_request.files else None
    message_map = {
        "approved": t("image_change.approved", request=request),
        "rejected": t("image_change.rejected", request=request),
    }
    return templates.TemplateResponse(
        "admin_image_change_request_detail.html",
        template_context(
            request,
            current_user,
            image_change_request=image_change_request,
            recipe=recipe,
            current_image_url=current_image_url,
            current_image_kind=current_image_kind,
            proposed_file=proposed_file,
            message=message_map.get(message, ""),
        ),
    )


@router.post("/admin/image-change-requests/{request_id}/approve")
@limiter.limit("30/minute", key_func=key_by_user_or_ip)
def admin_image_change_request_approve(
    request: Request,
    request_id: int,
    admin_note: str = Form(""),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    image_change_request = fetch_image_change_request_or_404(db, request_id)
    if image_change_request.status != "pending":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=t("error.image_change_request_not_pending"))
    proposed_file = image_change_request.files[0] if image_change_request.files else None
    if not proposed_file:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=t("error.image_change_file_missing"))
    recipe = image_change_request.recipe
    for image in recipe.images:
        image.is_primary = False
    db.add(
        RecipeImage(
            recipe_id=recipe.id,
            filename=proposed_file.filename,
            content_type=proposed_file.content_type,
            data=proposed_file.data,
            is_primary=True,
        )
    )
    image_change_request.status = "approved"
    image_change_request.admin_note = admin_note.strip() or None
    image_change_request.reviewed_by_admin_id = current_user.id
    image_change_request.reviewed_at = datetime.now(timezone.utc)
    db.commit()
    _ = request
    return redirect(f"/admin/image-change-requests/{request_id}?message=approved")


@router.post("/admin/image-change-requests/{request_id}/reject")
@limiter.limit("30/minute", key_func=key_by_user_or_ip)
def admin_image_change_request_reject(
    request: Request,
    request_id: int,
    admin_note: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    image_change_request = fetch_image_change_request_or_404(db, request_id)
    if image_change_request.status != "pending":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=t("error.image_change_request_not_pending"))
    if not admin_note.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=t("error.submission_reject_reason_required"))
    image_change_request.status = "rejected"
    image_change_request.admin_note = admin_note.strip()
    image_change_request.reviewed_by_admin_id = current_user.id
    image_change_request.reviewed_at = datetime.now(timezone.utc)
    db.commit()
    _ = request
    return redirect(f"/admin/image-change-requests/{request_id}?message=rejected")


@router.get("/admin/image-change-files/{file_id}")
def admin_image_change_file_get(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    _ = current_user
    image_change_file = db.scalar(
        select(RecipeImageChangeFile)
        .where(RecipeImageChangeFile.id == file_id)
        .options(joinedload(RecipeImageChangeFile.request))
    )
    if not image_change_file:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=t("error.image_not_found"))
    return RawResponse(content=image_change_file.data, media_type=image_change_file.content_type)
