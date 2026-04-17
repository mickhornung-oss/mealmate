import logging

from fastapi import APIRouter, Depends, Form, Query, Request, status
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.dependencies import get_admin_user, template_context
from app.models import User
from app.rate_limit import key_by_user_or_ip, limiter
from app.translation_provider import TranslationProviderError
from app.translation_service import (
    TranslationBatchConflictError,
    audit_german_translations,
    compute_translation_stats,
    get_translation_queue,
    get_source_language,
    get_translation_provider,
    get_recent_translation_jobs,
    repair_suspect_german_translations,
    run_translation_batch,
    run_translation_for_recipe_ids,
    start_translation_batch_job,
)
from app.views import redirect, templates

router = APIRouter(tags=["translations"])
logger = logging.getLogger("mealmate.translations")
TEST_TRANSLATION_TEXT = "Hello from MealMate"
ENV_SNIPPET = "\n".join(
    [
        "TRANSLATEAPI_ENABLED=1",
        "TRANSLATEAPI_API_KEY=...",
        "TRANSLATE_TARGET_LANGS=de,en,fr",
    ]
)


def _load_translations_admin_snapshot(
    db: Session,
    *,
    queue_limit: int = 100,
    jobs_limit: int = 15,
    de_audit_limit: int = 50,
):
    stats = compute_translation_stats(db)
    jobs = get_recent_translation_jobs(db, limit=jobs_limit)
    queue_items = get_translation_queue(db, limit=queue_limit)
    de_audit = audit_german_translations(db, limit=de_audit_limit, persist_flags=False)
    return {
        "stats": stats,
        "jobs": jobs,
        "queue_items": queue_items,
        "queue_count": len(queue_items),
        "de_audit": de_audit,
    }


def _normalize_mode(value: str) -> str:
    return "stale" if str(value).strip().lower() == "stale" else "missing"


def _translation_config_status() -> dict:
    runtime_settings = get_settings()
    provider_name = str(runtime_settings.translation_provider or "translateapi").strip().lower()
    target_langs = [
        lang
        for lang in [str(item).strip().lower().split("-", 1)[0] for item in runtime_settings.translate_target_langs]
        if lang
    ]
    unique_targets: list[str] = []
    for lang in target_langs:
        if lang not in unique_targets:
            unique_targets.append(lang)
    key_required = provider_name == "translateapi"
    key_set = bool((runtime_settings.translateapi_api_key or "").strip())
    enabled = bool(runtime_settings.translateapi_enabled)
    ready = enabled and bool(unique_targets) and (not key_required or key_set)
    return {
        "provider": provider_name,
        "enabled": enabled,
        "key_required": key_required,
        "key_set": key_set,
        "source_lang": get_source_language(),
        "target_langs": unique_targets,
        "auto_on_publish": bool(runtime_settings.translate_auto_on_publish),
        "lazy_on_view": bool(runtime_settings.translate_lazy_on_view),
        "ready": ready,
    }


def _build_translations_context(
    request: Request,
    current_user: User,
    db: Session,
    *,
    mode: str = "missing",
    report=None,
    error: str | None = None,
    message: str | None = None,
    last_error: str | None = None,
    test_result: dict | None = None,
    config_status: dict | None = None,
    de_audit_report=None,
    de_repair_report=None,
):
    runtime_settings = get_settings()
    snapshot = _load_translations_admin_snapshot(db, queue_limit=100, jobs_limit=15, de_audit_limit=50)
    effective_last_error = (last_error or "").strip() or (error or "").strip() or None
    effective_config_status = config_status or _translation_config_status()
    effective_de_audit_report = de_audit_report or snapshot["de_audit"]
    return template_context(
        request,
        current_user,
        mode=_normalize_mode(mode),
        report=report,
        error=error,
        message=message,
        last_error=effective_last_error,
        test_result=test_result,
        stats=snapshot["stats"],
        jobs=snapshot["jobs"],
        queue_items=snapshot["queue_items"],
        queue_count=snapshot["queue_count"],
        de_audit=effective_de_audit_report,
        de_repair_report=de_repair_report,
        config_status=effective_config_status,
        test_text=TEST_TRANSLATION_TEXT,
        env_snippet=ENV_SNIPPET,
        default_limit=int(runtime_settings.translate_max_recipes_per_run or 20),
        translateapi_enabled=bool(runtime_settings.translateapi_enabled),
        translate_auto_on_publish=bool(runtime_settings.translate_auto_on_publish),
        translateapi_poll_interval_seconds=int(runtime_settings.translateapi_poll_interval_seconds or 3),
        translateapi_max_polls=int(runtime_settings.translateapi_max_polls or 200),
    )


def _render_translations_page(
    request: Request,
    current_user: User,
    db: Session,
    *,
    status_code: int = status.HTTP_200_OK,
    mode: str = "missing",
    report=None,
    error: str | None = None,
    message: str | None = None,
    last_error: str | None = None,
    test_result: dict | None = None,
    config_status: dict | None = None,
    de_audit_report=None,
    de_repair_report=None,
):
    return templates.TemplateResponse(
        "admin_translations.html",
        _build_translations_context(
            request,
            current_user,
            db,
            mode=mode,
            report=report,
            error=error,
            message=message,
            last_error=last_error,
            test_result=test_result,
            config_status=config_status,
            de_audit_report=de_audit_report,
            de_repair_report=de_repair_report,
        ),
        status_code=status_code,
    )


def _commit_or_render_error(
    request: Request,
    current_user: User,
    db: Session,
    *,
    mode: str,
):
    try:
        db.commit()
        return None
    except OperationalError as exc:
        db.rollback()
        error_text = str(exc).lower()
        if "database is locked" in error_text:
            friendly = "Datenbank ist gerade gesperrt. Bitte SQLite Viewer schlieÃŸen und erneut versuchen."
        else:
            friendly = f"Datenbankfehler beim Speichern der Ãœbersetzungen: {exc}"
        return _render_translations_page(
            request,
            current_user,
            db,
            mode=mode,
            error=friendly,
            last_error=friendly,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
    except Exception as exc:
        db.rollback()
        friendly = f"Unerwarteter Fehler beim Speichern: {exc}"
        return _render_translations_page(
            request,
            current_user,
            db,
            mode=mode,
            error=friendly,
            last_error=friendly,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


def _render_translation_runtime_error(
    request: Request,
    current_user: User,
    db: Session,
    *,
    mode: str,
    exception: Exception,
    context: str,
    generic_status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
):
    if isinstance(exception, OperationalError):
        db.rollback()
        error_text = str(exception).lower()
        if "database is locked" in error_text:
            friendly = "Datenbank ist gerade gesperrt. Bitte SQLite Viewer schließen und in 10 Sekunden erneut versuchen."
        else:
            friendly = f"Datenbankfehler beim {context}: {exception}"
        return _render_translations_page(
            request,
            current_user,
            db,
            mode=mode,
            error=friendly,
            last_error=friendly,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
    db.rollback()
    friendly = f"{context.capitalize()} fehlgeschlagen: {exception}"
    return _render_translations_page(
        request,
        current_user,
        db,
        mode=mode,
        error=friendly,
        last_error=friendly,
        status_code=generic_status_code,
    )


def _is_translation_report_fatal(report) -> bool:
    return bool(report.errors and report.processed_recipes == 0 and report.created == 0 and report.updated == 0)


def _render_translation_report_error(
    request: Request,
    current_user: User,
    db: Session,
    *,
    mode: str,
    error_text: str,
):
    return _render_translations_page(
        request,
        current_user,
        db,
        mode=mode,
        error=error_text,
        status_code=status.HTTP_400_BAD_REQUEST,
    )


def _redirect_translation_report(mode: str, report) -> str:
    error_count = len(report.errors)
    return (
        "/admin/translations"
        f"?mode={mode}"
        f"&processed={report.processed_recipes}"
        f"&created={report.created}"
        f"&updated={report.updated}"
        f"&skipped={report.skipped}"
        f"&errors={error_count}"
    )


def _build_translation_run_report(
    *,
    mode: str,
    processed: int,
    created: int,
    updated: int,
    skipped: int,
    errors: int,
):
    if not any(value > 0 for value in [processed, created, updated, skipped, errors]):
        return None
    return {
        "processed_recipes": processed,
        "created": created,
        "updated": updated,
        "skipped": skipped,
        "errors_count": errors,
        "mode": _normalize_mode(mode),
    }


def _build_batch_started_message(*, batch_started: int, batch_job: str) -> str | None:
    if not batch_started:
        return None
    if batch_job.strip():
        return f"Batch-Job gestartet (ID: {batch_job.strip()})."
    return "Batch-Job gestartet."


@router.get("/admin/translations")
def admin_translations_page(
    request: Request,
    mode: str = Query("missing"),
    processed: int = Query(0, ge=0),
    created: int = Query(0, ge=0),
    updated: int = Query(0, ge=0),
    skipped: int = Query(0, ge=0),
    errors: int = Query(0, ge=0),
    batch_started: int = Query(0, ge=0),
    batch_job: str = Query(""),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    run_report = _build_translation_run_report(
        mode=mode,
        processed=processed,
        created=created,
        updated=updated,
        skipped=skipped,
        errors=errors,
    )
    message = _build_batch_started_message(
        batch_started=batch_started,
        batch_job=batch_job,
    )
    return _render_translations_page(request, current_user, db, mode=mode, report=run_report, message=message)


@router.get("/admin/translations/run")
def admin_translations_run_page(
    request: Request,
    mode: str = Query("missing"),
    processed: int = Query(0, ge=0),
    created: int = Query(0, ge=0),
    updated: int = Query(0, ge=0),
    skipped: int = Query(0, ge=0),
    errors: int = Query(0, ge=0),
    batch_started: int = Query(0, ge=0),
    batch_job: str = Query(""),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    return admin_translations_page(
        request=request,
        mode=mode,
        processed=processed,
        created=created,
        updated=updated,
        skipped=skipped,
        errors=errors,
        batch_started=batch_started,
        batch_job=batch_job,
        db=db,
        current_user=current_user,
    )


@router.get("/admin/translations/audit-de")
def admin_audit_de_translations(
    request: Request,
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    audit_report = audit_german_translations(db, limit=limit, persist_flags=False)
    message = f"Audit abgeschlossen: {audit_report.suspect_count} verdÃ¤chtige de-Ãœbersetzungen."
    return _render_translations_page(request, current_user, db, message=message, de_audit_report=audit_report)


@router.post("/admin/translations/repair-de")
@limiter.limit("5/minute", key_func=key_by_user_or_ip)
def admin_repair_de_translations(
    request: Request,
    limit: int = Form(50),
    dry_run: str | None = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    safe_limit = max(1, min(int(limit or 50), 500))
    dry_run_flag = bool(dry_run)
    report = repair_suspect_german_translations(db, limit=safe_limit, dry_run=dry_run_flag)
    status_code = status.HTTP_200_OK
    error_text: str | None = None
    message_text: str | None = None
    if dry_run_flag:
        db.rollback()
        message_text = (
            f"Dry-Run: {report.candidate_count} suspect de-Ãœbersetzungen "
            "wÃ¤ren fÃ¼r Force-Refresh vorgemerkt."
        )
    else:
        if report.error_count and report.updated_count == 0:
            db.rollback()
            status_code = status.HTTP_400_BAD_REQUEST
            error_text = report.errors[0]
        else:
            commit_response = _commit_or_render_error(
                request,
                current_user,
                db,
                mode="missing",
            )
            if commit_response is not None:
                return commit_response
            message_text = (
                f"Repair abgeschlossen: {report.updated_count} de-Ãœbersetzungen aktualisiert, "
                f"{report.skipped_count} Ã¼bersprungen."
            )
    audit_report = audit_german_translations(db, limit=safe_limit, persist_flags=False)
    return _render_translations_page(
        request,
        current_user,
        db,
        error=error_text,
        message=message_text,
        de_audit_report=audit_report,
        de_repair_report=report,
        status_code=status_code,
    )


@router.post("/admin/translations/run")
@limiter.limit("10/minute", key_func=key_by_user_or_ip)
def admin_run_translations(
    request: Request,
    mode: str = Form("missing"),
    limit: int = Form(0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    query_mode = request.query_params.get("mode", "").strip()
    normalized_mode = _normalize_mode(query_mode or mode)
    explicit_limit = limit if limit and limit > 0 else None
    try:
        report = run_translation_batch(db, mode=normalized_mode, limit=explicit_limit)
    except Exception as exc:
        return _render_translation_runtime_error(
            request,
            current_user,
            db,
            mode=normalized_mode,
            exception=exc,
            context="übersetzen",
        )
    if _is_translation_report_fatal(report):
        db.rollback()
        return _render_translation_report_error(
            request,
            current_user,
            db,
            mode=normalized_mode,
            error_text=report.errors[0],
        )
    commit_response = _commit_or_render_error(
        request,
        current_user,
        db,
        mode=normalized_mode,
    )
    if commit_response is not None:
        return commit_response
    return redirect(_redirect_translation_report(normalized_mode, report))
@router.post("/admin/translations/batch/start")
@limiter.limit("5/minute", key_func=key_by_user_or_ip)
def admin_start_translations_batch(
    request: Request,
    mode: str = Form("missing"),
    limit: int = Form(0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    normalized_mode = _normalize_mode(mode)
    explicit_limit = limit if limit and limit > 0 else None
    request_id = getattr(getattr(request, "state", None), "request_id", "-")
    try:
        job = start_translation_batch_job(
            db,
            mode=normalized_mode,
            limit=explicit_limit,
            admin_id=current_user.id,
        )
        logger.info(
            "translation_batch_started request_id=%s admin_id=%s mode=%s limit=%s external_job_id=%s",
            request_id,
            current_user.id,
            normalized_mode,
            explicit_limit if explicit_limit is not None else "default",
            job.external_job_id,
        )
    except TranslationBatchConflictError as exc:
        db.rollback()
        logger.warning(
            "translation_batch_start_conflict request_id=%s admin_id=%s mode=%s limit=%s detail=%s",
            request_id,
            current_user.id,
            normalized_mode,
            explicit_limit if explicit_limit is not None else "default",
            str(exc),
        )
        return _render_translations_page(
            request,
            current_user,
            db,
            mode=normalized_mode,
            error=str(exc),
            status_code=status.HTTP_409_CONFLICT,
        )
    except ValueError as exc:
        db.rollback()
        return _render_translations_page(
            request,
            current_user,
            db,
            mode=normalized_mode,
            error=str(exc),
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    except Exception as exc:
        return _render_translation_runtime_error(
            request,
            current_user,
            db,
            mode=normalized_mode,
            exception=exc,
            context="batch-start",
            generic_status_code=status.HTTP_502_BAD_GATEWAY,
        )

    commit_response = _commit_or_render_error(
        request,
        current_user,
        db,
        mode=normalized_mode,
    )
    if commit_response is not None:
        return commit_response
    return redirect(
        "/admin/translations"
        f"?mode={normalized_mode}"
        f"&batch_started=1"
        f"&batch_job={job.external_job_id}"
    )
@router.post("/admin/translations/queue/run")
@limiter.limit("10/minute", key_func=key_by_user_or_ip)
def admin_run_translation_queue(
    request: Request,
    mode: str = Form("missing"),
    limit: int = Form(10),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    normalized_mode = _normalize_mode(mode)
    explicit_limit = limit if limit and limit > 0 else 10
    queue_items = get_translation_queue(db, limit=max(explicit_limit, 1))
    recipe_ids = [item.recipe_id for item in queue_items]
    if not recipe_ids:
        return _render_translations_page(
            request,
            current_user,
            db,
            mode=normalized_mode,
            message="Keine neuen/fehlenden Rezepte in der Übersetzungs-Warteschlange.",
            status_code=status.HTTP_200_OK,
        )
    report = run_translation_for_recipe_ids(
        db,
        recipe_ids,
        mode=normalized_mode,
        limit=explicit_limit,
    )
    if _is_translation_report_fatal(report):
        db.rollback()
        return _render_translation_report_error(
            request,
            current_user,
            db,
            mode=normalized_mode,
            error_text=report.errors[0],
        )
    commit_response = _commit_or_render_error(
        request,
        current_user,
        db,
        mode=normalized_mode,
    )
    if commit_response is not None:
        return commit_response
    return redirect(_redirect_translation_report(normalized_mode, report))
@router.post("/admin/translations/recipes/{recipe_id}/run")
@limiter.limit("20/minute", key_func=key_by_user_or_ip)
def admin_run_translation_for_recipe(
    request: Request,
    recipe_id: int,
    mode: str = Form("missing"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    normalized_mode = _normalize_mode(mode)
    report = run_translation_for_recipe_ids(
        db,
        [recipe_id],
        mode=normalized_mode,
        limit=1,
    )
    if _is_translation_report_fatal(report):
        db.rollback()
        return _render_translation_report_error(
            request,
            current_user,
            db,
            mode=normalized_mode,
            error_text=report.errors[0],
        )
    commit_response = _commit_or_render_error(
        request,
        current_user,
        db,
        mode=normalized_mode,
    )
    if commit_response is not None:
        return commit_response
    return redirect(_redirect_translation_report(normalized_mode, report))


def _friendly_translation_test_error(error: Exception) -> str:
    message = str(error).strip()
    if "401" in message:
        return "Authentifizierung fehlgeschlagen (401). PrÃ¼fe TRANSLATEAPI_API_KEY."
    if "402" in message:
        return "Abrechnung/Limit erreicht (402). PrÃ¼fe dein TranslateAPI-Konto."
    if "429" in message:
        return "Rate-Limit erreicht (429). Bitte spÃ¤ter erneut versuchen."
    if message:
        return f"TestÃ¼bersetzung fehlgeschlagen: {message}"
    return "TestÃ¼bersetzung fehlgeschlagen: Unbekannter Fehler."


@router.post("/admin/translations/test")
@limiter.limit("5/minute", key_func=key_by_user_or_ip)
def admin_test_translation(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    config_status = _translation_config_status()
    if not config_status["enabled"]:
        guidance = "Setze TRANSLATEAPI_ENABLED=1 und TRANSLATEAPI_API_KEY in .env."
        return _render_translations_page(
            request,
            current_user,
            db,
            error=guidance,
            last_error=guidance,
            config_status=config_status,
            status_code=status.HTTP_200_OK,
        )
    if config_status["key_required"] and not config_status["key_set"]:
        guidance = "Setze TRANSLATEAPI_API_KEY in .env und starte die App neu."
        return _render_translations_page(
            request,
            current_user,
            db,
            error=guidance,
            last_error=guidance,
            config_status=config_status,
            status_code=status.HTTP_200_OK,
        )
    target_langs = list(config_status.get("target_langs", []))
    if not target_langs:
        guidance = "Keine Zielsprachen konfiguriert. Setze TRANSLATE_TARGET_LANGS."
        return _render_translations_page(
            request,
            current_user,
            db,
            error=guidance,
            last_error=guidance,
            config_status=config_status,
            status_code=status.HTTP_200_OK,
        )
    provider = get_translation_provider()
    try:
        translated = provider.translate(
            TEST_TRANSLATION_TEXT,
            target_langs,
            source_lang=get_source_language(),
        )
    except TranslationProviderError as exc:
        friendly = _friendly_translation_test_error(exc)
        return _render_translations_page(
            request,
            current_user,
            db,
            error=friendly,
            last_error=friendly,
            config_status=config_status,
            status_code=status.HTTP_200_OK,
        )
    except Exception as exc:  # pragma: no cover - defensive runtime guard
        friendly = _friendly_translation_test_error(exc)
        return _render_translations_page(
            request,
            current_user,
            db,
            error=friendly,
            last_error=friendly,
            config_status=config_status,
            status_code=status.HTTP_200_OK,
        )
    test_result = {
        "source_text": TEST_TRANSLATION_TEXT,
        "translations": [
            {"language": lang, "text": str(translated.get(lang, TEST_TRANSLATION_TEXT))}
            for lang in target_langs
        ],
    }
    return _render_translations_page(
        request,
        current_user,
        db,
        message="Testübersetzung erfolgreich.",
        test_result=test_result,
        config_status=config_status,
        status_code=status.HTTP_200_OK,
    )


