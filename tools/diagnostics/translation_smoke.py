from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import inspect, select

from app.config import get_settings
from app.database import SessionLocal
from app.models import Recipe
from app.translation_models import RecipeTranslation
from app.translation_provider import TranslationProviderError, resolve_translation_provider
from app.translation_service import build_recipe_source_payload, build_source_hash, get_source_language, get_target_languages

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DIAGNOSTICS_DIR = PROJECT_ROOT / "diagnostics"
REPORT_PATH = DIAGNOSTICS_DIR / "translation_smoke.md"
DEFAULT_LANGS_TO_CHECK = ("de", "en", "fr")


@dataclass
class TranslationSmokeResult:
    ok: bool
    recipe_id: int | None = None
    source_hash: str = ""
    env_summary: dict[str, str] = field(default_factory=dict)
    row_counts: dict[str, int] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    failures: list[str] = field(default_factory=list)
    real_api_preview: dict[str, str] = field(default_factory=dict)
    mock_write_result: str = ""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run translation smoke diagnostics against DB/services.")
    parser.add_argument("--recipe-id", type=int, default=0, help="Explicit published recipe id for checks.")
    parser.add_argument("--real-api", action="store_true", help="Run optional real provider call for a tiny text.")
    parser.add_argument("--mock-write", action="store_true", help="Write mock translation rows for de/en/fr.")
    parser.add_argument("--report", default=str(REPORT_PATH), help="Markdown report output path.")
    return parser.parse_args()


def _normalize_report_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return (PROJECT_ROOT / path).resolve()


def _bool_text(value: bool) -> str:
    return "1" if value else "0"


def _collect_env_summary() -> dict[str, str]:
    settings = get_settings()
    return {
        "APP_ENV": settings.app_env,
        "TRANSLATION_PROVIDER": settings.translation_provider,
        "TRANSLATEAPI_ENABLED": _bool_text(bool(settings.translateapi_enabled)),
        "TRANSLATEAPI_KEY_SET": _bool_text(bool((settings.translateapi_api_key or "").strip())),
        "TRANSLATE_SOURCE_LANG": settings.translate_source_lang,
        "TRANSLATE_TARGET_LANGS": ",".join(settings.translate_target_langs),
        "TRANSLATE_AUTO_ON_PUBLISH": _bool_text(bool(settings.translate_auto_on_publish)),
        "TRANSLATE_LAZY_ON_VIEW": _bool_text(bool(settings.translate_lazy_on_view)),
    }


def _pick_recipe_id(explicit_recipe_id: int) -> int | None:
    with SessionLocal() as db:
        if explicit_recipe_id > 0:
            recipe = db.scalar(select(Recipe).where(Recipe.id == explicit_recipe_id, Recipe.is_published.is_(True)))
            return int(recipe.id) if recipe else None
        recipe = db.scalar(select(Recipe).where(Recipe.is_published.is_(True)).order_by(Recipe.id.desc()))
        return int(recipe.id) if recipe else None


def _count_translation_rows(recipe_id: int) -> dict[str, int]:
    result: dict[str, int] = {lang: 0 for lang in DEFAULT_LANGS_TO_CHECK}
    with SessionLocal() as db:
        rows = db.scalars(
            select(RecipeTranslation)
            .where(RecipeTranslation.recipe_id == recipe_id, RecipeTranslation.language.in_(DEFAULT_LANGS_TO_CHECK))
        ).all()
    for row in rows:
        result[row.language] = result.get(row.language, 0) + 1
    return result


def _compute_source_hash(recipe_id: int) -> str:
    with SessionLocal() as db:
        recipe = db.scalar(select(Recipe).where(Recipe.id == recipe_id))
        if not recipe:
            return ""
        payload = build_recipe_source_payload(recipe)
    return build_source_hash(payload)


def _run_real_api_preview() -> tuple[dict[str, str], str]:
    settings = get_settings()
    if not settings.translateapi_enabled:
        return {}, "TRANSLATEAPI_ENABLED=0; real call skipped."
    if not (settings.translateapi_api_key or "").strip():
        return {}, "TRANSLATEAPI_API_KEY missing; real call skipped."
    provider = resolve_translation_provider(settings)
    try:
        translated = provider.translate("Hallo Welt", ["en", "fr"], source_lang=get_source_language())
        return translated, ""
    except TranslationProviderError as exc:
        return {}, f"Real provider error: {exc}"
    except Exception as exc:  # pragma: no cover - defensive for external runtime
        return {}, f"Real provider unexpected error: {exc}"


def _run_mock_write(recipe_id: int, source_hash: str) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    with SessionLocal() as db:
        recipe = db.scalar(select(Recipe).where(Recipe.id == recipe_id))
        if not recipe:
            return "Skipped mock write: recipe not found."
        payload = build_recipe_source_payload(recipe)
        current_source_hash = source_hash or build_source_hash(payload)
        for language in DEFAULT_LANGS_TO_CHECK:
            row = db.scalar(
                select(RecipeTranslation).where(
                    RecipeTranslation.recipe_id == recipe_id,
                    RecipeTranslation.language == language,
                )
            )
            title_value = f"TEST {language.upper()} TITLE {stamp}"[:255]
            description_value = f"TEST {language.upper()} DESCRIPTION {stamp}"
            instructions_value = f"TEST {language.upper()} INSTRUCTIONS {stamp}"
            ingredients_value = f"TEST {language.upper()} INGREDIENTS {stamp}"
            if row is None:
                row = RecipeTranslation(
                    recipe_id=recipe_id,
                    language=language,
                    title=title_value,
                    description=description_value,
                    instructions=instructions_value,
                    ingredients_text=ingredients_value,
                    source_hash=current_source_hash,
                    stale=False,
                )
                db.add(row)
            else:
                row.title = title_value
                row.description = description_value
                row.instructions = instructions_value
                row.ingredients_text = ingredients_value
                row.source_hash = current_source_hash
                row.stale = False
        db.commit()
    return "Mock rows upserted for languages: de,en,fr."


def run_translation_smoke(
    *,
    recipe_id: int = 0,
    real_api: bool = False,
    mock_write: bool = False,
    report_path: Path = REPORT_PATH,
) -> TranslationSmokeResult:
    result = TranslationSmokeResult(ok=True)
    result.env_summary = _collect_env_summary()

    with SessionLocal() as db:
        inspector = inspect(db.bind)
        has_table = inspector.has_table("recipe_translations")
    if not has_table:
        result.ok = False
        result.failures.append("Table 'recipe_translations' does not exist.")
        _write_report(result, report_path)
        return result

    selected_recipe_id = _pick_recipe_id(recipe_id)
    result.recipe_id = selected_recipe_id
    if not selected_recipe_id:
        result.ok = False
        result.failures.append("No published recipe found for translation smoke.")
        _write_report(result, report_path)
        return result

    result.source_hash = _compute_source_hash(selected_recipe_id)
    result.row_counts = _count_translation_rows(selected_recipe_id)

    target_languages = get_target_languages()
    if target_languages:
        missing_targets = [lang for lang in target_languages if result.row_counts.get(lang, 0) == 0]
        if missing_targets:
            result.warnings.append(f"Missing target translation rows for: {', '.join(missing_targets)}")
    else:
        result.warnings.append("No target languages configured.")

    if real_api:
        preview, preview_error = _run_real_api_preview()
        result.real_api_preview = preview
        if preview_error:
            result.warnings.append(preview_error)

    if mock_write:
        result.mock_write_result = _run_mock_write(selected_recipe_id, result.source_hash)
        result.row_counts = _count_translation_rows(selected_recipe_id)

    _write_report(result, report_path)
    return result


def _write_report(result: TranslationSmokeResult, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    lines.append("# Translation Smoke Report")
    lines.append("")
    lines.append(f"- Generated at: {datetime.now(timezone.utc).isoformat()}")
    lines.append(f"- Status: {'PASS' if result.ok else 'FAIL'}")
    lines.append("")
    lines.append("## ENV Summary")
    lines.append("| Key | Value |")
    lines.append("| --- | --- |")
    for key, value in sorted(result.env_summary.items(), key=lambda item: item[0]):
        safe_value = str(value).replace("|", "\\|")
        lines.append(f"| `{key}` | `{safe_value}` |")
    lines.append("")
    lines.append("## Recipe Check")
    lines.append(f"- recipe_id: {result.recipe_id if result.recipe_id is not None else '-'}")
    lines.append(f"- source_hash: `{result.source_hash or '-'}`")
    lines.append("")
    lines.append("## Translation Rows")
    lines.append("| Language | Count |")
    lines.append("| --- | ---: |")
    if result.row_counts:
        for lang in DEFAULT_LANGS_TO_CHECK:
            lines.append(f"| `{lang}` | {int(result.row_counts.get(lang, 0))} |")
    else:
        lines.append("| `-` | 0 |")
    lines.append("")
    lines.append("## Optional Runs")
    lines.append(f"- mock_write: {result.mock_write_result or 'not requested'}")
    if result.real_api_preview:
        lines.append(f"- real_api_preview: `{result.real_api_preview}`")
    else:
        lines.append("- real_api_preview: not requested or no result")
    lines.append("")
    lines.append("## Warnings")
    if result.warnings:
        for warning in result.warnings:
            lines.append(f"- {warning}")
    else:
        lines.append("- none")
    lines.append("")
    lines.append("## Failures")
    if result.failures:
        for failure in result.failures:
            lines.append(f"- {failure}")
    else:
        lines.append("- none")
    lines.append("")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    report_path = _normalize_report_path(args.report)
    result = run_translation_smoke(
        recipe_id=int(args.recipe_id or 0),
        real_api=bool(args.real_api),
        mock_write=bool(args.mock_write),
        report_path=report_path,
    )
    print(f"Report written: {report_path}")
    print(f"Status: {'PASS' if result.ok else 'FAIL'}")
    if result.failures:
        for item in result.failures:
            print(f"- FAIL: {item}")
    if result.warnings:
        for item in result.warnings:
            print(f"- WARN: {item}")
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
