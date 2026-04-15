from __future__ import annotations

import argparse
import re
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

from fastapi.testclient import TestClient
from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import selectinload

from app.main import app
from app.database import SessionLocal
from app.models import Recipe, RecipeImage

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DIAGNOSTICS_DIR = PROJECT_ROOT / "diagnostics"
REPORT_PATH = DIAGNOSTICS_DIR / "image_smoke.md"
IMG_SRC_RE = re.compile(r'<img[^>]+src="([^"]+)"', re.IGNORECASE)
IMAGES_SECTION_RE = re.compile(r'<section class="panel" id="recipe-images-section">(.*?)</section>', re.DOTALL)


@dataclass
class SampleRecipeCheck:
    recipe_id: int
    title: str
    expected_kind: str
    expected_src: str
    status: str
    detail_status_code: int
    note: str


@dataclass
class ImageSmokeResult:
    ok: bool
    db_counts: dict[str, int] = field(default_factory=dict)
    sample_checks: list[SampleRecipeCheck] = field(default_factory=list)
    csp_value: str = ""
    home_status_code: int = 0
    home_img_sources_count: int = 0
    home_unique_img_sources_count: int = 0
    home_top_sources: list[tuple[str, int]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    failures: list[str] = field(default_factory=list)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run image fallback/caching smoke diagnostics.")
    parser.add_argument("--report", default=str(REPORT_PATH), help="Markdown report output path.")
    return parser.parse_args()


def _normalize_report_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return (PROJECT_ROOT / path).resolve()


def _extract_detail_images_section(html_text: str) -> str:
    match = IMAGES_SECTION_RE.search(html_text)
    if not match:
        return html_text
    return match.group(1)


def _resolve_expected_image(recipe: Recipe) -> tuple[str, str]:
    sorted_images = sorted(recipe.images, key=lambda image: (0 if image.is_primary else 1, image.created_at, image.id))
    if sorted_images:
        selected = sorted_images[0]
        return "db", f"/images/{selected.id}"
    external_url = (recipe.source_image_url or "").strip() or (recipe.title_image_url or "").strip()
    if external_url:
        return "external", f"/external-image?url={quote(external_url, safe='')}"
    return "placeholder", ""


def _collect_db_counts() -> dict[str, int]:
    with SessionLocal() as db:
        total_images = int(db.scalar(select(func.count()).select_from(RecipeImage)) or 0)
        recipes_with_primary = int(
            db.scalar(select(func.count(func.distinct(RecipeImage.recipe_id))).where(RecipeImage.is_primary.is_(True))) or 0
        )
        recipes_with_source_url = int(
            db.scalar(
                select(func.count())
                .select_from(Recipe)
                .where(
                    Recipe.is_published.is_(True),
                    or_(
                        and_(Recipe.source_image_url.is_not(None), Recipe.source_image_url != ""),
                        and_(Recipe.title_image_url.is_not(None), Recipe.title_image_url != ""),
                    ),
                )
            )
            or 0
        )
    return {
        "recipe_images_total": total_images,
        "recipes_with_primary_image": recipes_with_primary,
        "recipes_with_source_or_title_url": recipes_with_source_url,
    }


def _sample_recipes() -> list[Recipe]:
    with SessionLocal() as db:
        has_any_image = select(RecipeImage.id).where(RecipeImage.recipe_id == Recipe.id).exists()
        primary_ids = db.scalars(
            select(RecipeImage.recipe_id)
            .join(Recipe, Recipe.id == RecipeImage.recipe_id)
            .where(Recipe.is_published.is_(True), RecipeImage.is_primary.is_(True))
            .distinct()
            .order_by(RecipeImage.recipe_id.desc())
            .limit(3)
        ).all()
        external_only = db.scalars(
            select(Recipe.id).where(
                Recipe.is_published.is_(True),
                ~has_any_image,
                or_(
                    and_(Recipe.source_image_url.is_not(None), Recipe.source_image_url != ""),
                    and_(Recipe.title_image_url.is_not(None), Recipe.title_image_url != ""),
                ),
            )
            .order_by(Recipe.id.desc())
            .limit(3)
        ).all()
        no_image_candidates = db.scalars(
            select(Recipe.id).where(
                Recipe.is_published.is_(True),
                ~has_any_image,
                or_(Recipe.source_image_url.is_(None), Recipe.source_image_url == ""),
                or_(Recipe.title_image_url.is_(None), Recipe.title_image_url == ""),
            )
            .order_by(Recipe.id.desc())
            .limit(3)
        ).all()
        random_one = db.scalars(
            select(Recipe.id).where(Recipe.is_published.is_(True)).order_by(func.random()).limit(1)
        ).all()

        selected_ids: list[int] = []
        for candidate in [*primary_ids, *external_only, *no_image_candidates, *random_one]:
            value = int(candidate)
            if value not in selected_ids:
                selected_ids.append(value)

        if not selected_ids:
            return []
        recipes = db.scalars(
            select(Recipe).where(Recipe.id.in_(selected_ids)).options(selectinload(Recipe.images)).order_by(Recipe.id.desc())
        ).all()
    return list(recipes)


def run_image_smoke(*, report_path: Path = REPORT_PATH) -> ImageSmokeResult:
    result = ImageSmokeResult(ok=True)
    result.db_counts = _collect_db_counts()
    samples = _sample_recipes()
    with TestClient(app) as client:
        home_response = client.get("/?per_page=80")
        result.home_status_code = int(home_response.status_code)
        result.csp_value = home_response.headers.get("content-security-policy", "")
        if home_response.status_code != 200:
            result.ok = False
            result.failures.append(f"GET / returned status {home_response.status_code}")
        if "img-src" not in result.csp_value:
            result.ok = False
            result.failures.append("CSP header missing img-src directive.")

        home_img_sources = IMG_SRC_RE.findall(home_response.text)
        result.home_img_sources_count = len(home_img_sources)
        unique_sources = sorted(set(home_img_sources))
        result.home_unique_img_sources_count = len(unique_sources)
        source_counter = Counter(home_img_sources)
        result.home_top_sources = source_counter.most_common(5)

        if result.home_img_sources_count >= 3 and result.home_top_sources:
            top_src, top_count = result.home_top_sources[0]
            ratio = top_count / result.home_img_sources_count
            if ratio > 0.7:
                result.warnings.append(
                    f"More than 70% of home img src values are identical ({top_count}/{result.home_img_sources_count})."
                )
                result.failures.append(f"Likely repeated image source detected: {top_src}")
                result.ok = False

        for recipe in samples:
            expected_kind, expected_src = _resolve_expected_image(recipe)
            detail = client.get(f"/recipes/{recipe.id}")
            note = ""
            status = "PASS"
            if detail.status_code != 200:
                status = "FAIL"
                note = f"detail status={detail.status_code}"
                result.ok = False
                result.failures.append(f"Recipe detail for id={recipe.id} returned {detail.status_code}")
            else:
                section_html = _extract_detail_images_section(detail.text)
                if expected_kind == "db":
                    if expected_src not in section_html:
                        status = "FAIL"
                        note = f"expected db src missing: {expected_src}"
                elif expected_kind == "external":
                    if expected_src not in section_html:
                        status = "FAIL"
                        note = f"expected external src missing: {expected_src}"
                else:
                    has_db_src = '/images/' in section_html
                    has_external_src = '/external-image?url=' in section_html
                    if has_db_src or has_external_src:
                        status = "FAIL"
                        note = "placeholder expected but image src found in detail section"
                if status == "FAIL":
                    result.ok = False
                    result.failures.append(f"Fallback mismatch for recipe_id={recipe.id}: {note}")
            result.sample_checks.append(
                SampleRecipeCheck(
                    recipe_id=int(recipe.id),
                    title=(recipe.title or "").strip()[:80],
                    expected_kind=expected_kind,
                    expected_src=expected_src or "-",
                    status=status,
                    detail_status_code=int(detail.status_code),
                    note=note or "-",
                )
            )

    _write_report(result, report_path)
    return result


def _write_report(result: ImageSmokeResult, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    lines.append("# Image Smoke Report")
    lines.append("")
    lines.append(f"- Generated at: {datetime.now(timezone.utc).isoformat()}")
    lines.append(f"- Status: {'PASS' if result.ok else 'FAIL'}")
    lines.append("")
    lines.append("## DB Counts")
    lines.append("| Metric | Value |")
    lines.append("| --- | ---: |")
    for key, value in sorted(result.db_counts.items(), key=lambda item: item[0]):
        lines.append(f"| `{key}` | {int(value)} |")
    lines.append("")
    lines.append("## Home Page Check")
    lines.append(f"- GET / status: {result.home_status_code}")
    lines.append(f"- img src count: {result.home_img_sources_count}")
    lines.append(f"- unique img src count: {result.home_unique_img_sources_count}")
    lines.append(f"- CSP: `{result.csp_value or '-'}`")
    lines.append("")
    lines.append("### Top img src values")
    if result.home_top_sources:
        lines.append("| Src | Count |")
        lines.append("| --- | ---: |")
        for src, count in result.home_top_sources:
            safe_src = src.replace("|", "\\|")
            lines.append(f"| `{safe_src}` | {int(count)} |")
    else:
        lines.append("- none")
    lines.append("")
    lines.append("## Sample Recipe Checks")
    if result.sample_checks:
        lines.append("| Recipe ID | Title | Expected Kind | Expected Src | Detail Status | Result | Note |")
        lines.append("| ---: | --- | --- | --- | ---: | --- | --- |")
        for check in result.sample_checks:
            safe_title = check.title.replace("|", "\\|")
            safe_src = check.expected_src.replace("|", "\\|")
            safe_note = check.note.replace("|", "\\|")
            lines.append(
                f"| {check.recipe_id} | {safe_title} | {check.expected_kind} | `{safe_src}` | "
                f"{check.detail_status_code} | {check.status} | {safe_note} |"
            )
    else:
        lines.append("- no published recipes sampled")
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
    result = run_image_smoke(report_path=report_path)
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
