# Kategorie-Filter + Pagination UX Fix

## Geaenderte Dateien

- `app/services.py`
- `app/routers/recipes.py`
- `app/routers/admin.py`
- `app/templates/home.html`
- `app/templates/partials/recipe_list.html`
- `app/templates/recipe_form.html`
- `app/templates/admin.html`
- `app/static/style.css`
- `app/static/security.js`
- `app/i18n/de.py`

## app/services.py
```python
import csv
import html
import io
import json
import re
from collections import Counter
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal
from urllib.parse import unquote, urlparse
from urllib.request import Request, urlopen

from PIL import Image, UnidentifiedImageError
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import AppMeta, Ingredient, Recipe, RecipeImage, RecipeIngredient, User

settings = get_settings()

ALLOWED_DIFFICULTIES = {"easy", "medium", "hard"}
DEFAULT_CATEGORY = "Unkategorisiert"
IMPORT_MODE = Literal["insert_only", "update_existing"]


@dataclass
class CSVImportReport:
    inserted: int = 0
    updated: int = 0
    skipped: int = 0
    errors: list[str] = field(default_factory=list)


def parse_ingredient_text(raw: str) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for line in raw.splitlines():
        normalized = line.strip()
        if not normalized:
            continue
        parts = [part.strip() for part in normalized.split("|")]
        if len(parts) == 1:
            items.append({"name": parts[0], "quantity_text": "", "grams": None})
            continue
        if len(parts) == 2:
            items.append({"name": parts[0], "quantity_text": parts[1], "grams": None})
            continue
        grams = parse_optional_int(parts[2])
        items.append({"name": parts[0], "quantity_text": parts[1], "grams": grams})
    return items


def parse_optional_int(value: Any) -> int | None:
    if value is None:
        return None
    if isinstance(value, int):
        return value
    text = str(value).strip()
    if not text:
        return None
    match = re.search(r"\d+", text)
    return int(match.group(0)) if match else None


def sanitize_difficulty(value: str) -> str:
    normalized = value.strip().lower()
    german_map = {"leicht": "easy", "mittel": "medium", "schwer": "hard"}
    normalized = german_map.get(normalized, normalized)
    if normalized not in ALLOWED_DIFFICULTIES:
        return "medium"
    return normalized


def normalize_category(value: Any, fallback: str = DEFAULT_CATEGORY, allow_empty: bool = False) -> str:
    text = str(value or "").replace("_", " ")
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return "" if allow_empty else fallback
    if text.casefold() in {"general", "allgemein", "uncategorized", "unkategorisiert"}:
        return fallback
    return text.title()[:120]


def build_category_index(db: Session) -> dict[str, list[str]]:
    raw_categories = db.scalars(select(Recipe.category)).all()
    variants: dict[str, set[str]] = {}
    for raw in raw_categories:
        raw_value = str(raw or "")
        normalized = normalize_category(raw_value, allow_empty=True)
        key = normalized or DEFAULT_CATEGORY
        variants.setdefault(key, set()).update({raw_value, key})
    return {key: sorted(values) for key, values in variants.items()}


def get_distinct_categories(db: Session) -> list[str]:
    categories = sorted(build_category_index(db).keys(), key=str.casefold)
    if not categories:
        return [DEFAULT_CATEGORY]
    return categories


def get_category_stats(db: Session, limit: int = 10) -> tuple[int, list[tuple[str, int]]]:
    raw_categories = db.scalars(select(Recipe.category)).all()
    counter = Counter(normalize_category(value) for value in raw_categories)
    if not counter:
        counter = Counter({DEFAULT_CATEGORY: 0})
    top_categories = sorted(counter.items(), key=lambda item: (-item[1], item[0].casefold()))[:limit]
    return len(counter), top_categories


def normalize_ingredient_name(name: str) -> str:
    return re.sub(r"\s+", " ", name.strip().lower())


def parse_list_like(raw_value: Any) -> list[str]:
    if isinstance(raw_value, list):
        return [str(item).strip() for item in raw_value if str(item).strip()]
    if raw_value is None:
        return []
    value = str(raw_value).strip()
    if not value:
        return []
    if value.startswith("[") and value.endswith("]"):
        try:
            loaded = json.loads(value)
        except json.JSONDecodeError:
            loaded = None
        if isinstance(loaded, list):
            return [str(item).strip() for item in loaded if str(item).strip()]
    separator = "\n" if "\n" in value else ","
    return [item.strip().strip('"') for item in value.split(separator) if item.strip()]


def parse_text_block(raw_value: Any) -> str:
    parts = parse_list_like(raw_value)
    if parts:
        return "\n".join(parts)
    return str(raw_value or "").strip()


def get_or_create_ingredient(db: Session, name: str) -> Ingredient:
    normalized = normalize_ingredient_name(name)
    ingredient = db.scalar(select(Ingredient).where(Ingredient.name == normalized))
    if ingredient:
        return ingredient
    ingredient = Ingredient(name=normalized)
    db.add(ingredient)
    db.flush()
    return ingredient


def replace_recipe_ingredients(db: Session, recipe: Recipe, ingredient_entries: list[dict[str, Any]]) -> None:
    recipe.recipe_ingredients.clear()
    merged_entries: dict[str, dict[str, Any]] = {}
    for entry in ingredient_entries:
        name = str(entry.get("name") or "").strip()
        if not name:
            continue
        key = normalize_ingredient_name(name)
        quantity_text = str(entry.get("quantity_text") or "").strip()
        grams = parse_optional_int(entry.get("grams"))
        if key not in merged_entries:
            merged_entries[key] = {"name": name, "quantity_text": quantity_text, "grams": grams}
            continue
        current = merged_entries[key]
        if quantity_text:
            if current["quantity_text"]:
                current["quantity_text"] = f"{current['quantity_text']} | {quantity_text}"
            else:
                current["quantity_text"] = quantity_text
        if current["grams"] is None and grams is not None:
            current["grams"] = grams
    for merged in merged_entries.values():
        ingredient = get_or_create_ingredient(db, merged["name"])
        db.add(
            RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient,
                quantity_text=merged["quantity_text"],
                grams=merged["grams"],
            )
        )


def validate_upload(content_type: str, file_size_bytes: int, file_bytes: bytes | None = None) -> None:
    if content_type not in settings.allowed_image_types:
        raise ValueError(f"Unsupported MIME type '{content_type}'.")
    max_bytes = settings.max_upload_mb * 1024 * 1024
    if file_size_bytes > max_bytes:
        raise ValueError(f"Image too large. Max size is {settings.max_upload_mb} MB.")
    if file_bytes is not None:
        try:
            with Image.open(io.BytesIO(file_bytes)) as image:
                image.verify()
        except (UnidentifiedImageError, OSError) as exc:
            raise ValueError("Uploaded file is not a valid image.") from exc


@lru_cache(maxsize=4096)
def resolve_title_image_url(image_url: str) -> str | None:
    cleaned = image_url.strip()
    if not cleaned:
        return None
    lower = cleaned.lower()
    if "kein_bild" in lower:
        return None
    if lower.endswith((".jpg", ".jpeg", ".png", ".webp")) and "/wiki/" not in lower:
        return cleaned
    parsed = urlparse(cleaned)
    host = parsed.netloc.lower()
    path = unquote(parsed.path).lower()
    if "kochwiki.org" in host and "/wiki/" in parsed.path and "datei" in path:
        request = Request(cleaned, headers={"User-Agent": "MealMate/1.0"})
        with urlopen(request, timeout=12) as response:
            html_text = response.read(300_000).decode("utf-8", errors="ignore")
        match = re.search(
            r'<meta\s+property=["\']og:image["\']\s+content=["\']([^"\']+)["\']',
            html_text,
            flags=re.IGNORECASE,
        )
        if match:
            return html.unescape(match.group(1))
    return cleaned


def extract_token(raw_header: str | None) -> str | None:
    if not raw_header:
        return None
    prefix = "Bearer "
    if raw_header.startswith(prefix):
        return raw_header[len(prefix) :].strip()
    return raw_header.strip()


def can_manage_recipe(current_user: User, recipe: Recipe) -> bool:
    return current_user.role == "admin" or recipe.creator_id == current_user.id


def get_meta_value(db: Session, key: str) -> str | None:
    meta = db.scalar(select(AppMeta).where(AppMeta.key == key))
    return meta.value if meta else None


def set_meta_value(db: Session, key: str, value: str) -> None:
    meta = db.scalar(select(AppMeta).where(AppMeta.key == key))
    if not meta:
        db.add(AppMeta(key=key, value=value))
        return
    meta.value = value


def is_meta_true(db: Session, key: str) -> bool:
    return get_meta_value(db, key) == "1"


def normalize_columns(row: dict[str, Any]) -> dict[str, Any]:
    return {str(key).strip().lower(): value for key, value in row.items()}


def read_kochwiki_csv(csv_path: str | Path) -> list[dict[str, Any]]:
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {path}")
    data = path.read_bytes()
    return read_kochwiki_csv_bytes(data)


def _read_csv_rows(text: str, delimiter: str) -> list[dict[str, Any]]:
    reader = csv.DictReader(io.StringIO(text), delimiter=delimiter)
    return [normalize_columns(row) for row in reader]


def read_kochwiki_csv_bytes(csv_bytes: bytes) -> list[dict[str, Any]]:
    text = csv_bytes.decode("utf-8-sig", errors="replace")
    sample_lines = [line for line in text.splitlines() if line.strip()][:5]
    sample = "\n".join(sample_lines)
    delimiter = ";" if sample.count(";") >= sample.count(",") else ","
    rows = _read_csv_rows(text, delimiter)
    if delimiter == ";" and rows and len(rows[0]) <= 1:
        fallback_rows = _read_csv_rows(text, ",")
        if fallback_rows and len(fallback_rows[0]) > 1:
            rows = fallback_rows
    return rows


def _pick_value(row: dict[str, Any], keys: tuple[str, ...]) -> Any:
    for key in keys:
        value = row.get(key)
        if value not in (None, ""):
            return value
    return None


def _clean_title(value: Any) -> str:
    title = re.sub(r"\s+", " ", str(value or "").strip())
    return title[:255]


def _normalize_title_for_match(title: str) -> str:
    return re.sub(r"\s+", " ", title.strip().lower())


def _parse_source_image_url(raw_value: Any) -> str | None:
    candidate = str(raw_value or "").strip()
    if not candidate:
        return None
    if "kein_bild" in candidate.lower():
        return None
    return candidate[:1024]


def _parse_kochwiki_ingredients(raw_value: Any) -> list[dict[str, Any]]:
    entries = []
    for item in parse_list_like(raw_value):
        cleaned = re.sub(r"\s+", " ", item.strip())
        if not cleaned:
            continue
        match = re.match(r"^\s*([\d.,/\-]+\s*[A-Za-z%]*)\s+(.+)$", cleaned)
        if match:
            quantity_text = match.group(1).strip()
            name = match.group(2).strip()
        else:
            quantity_text = ""
            name = cleaned
        entries.append({"name": name, "quantity_text": quantity_text, "grams": parse_optional_int(cleaned)})
    return entries


def _build_category(row: dict[str, Any]) -> str:
    categories = parse_list_like(row.get("kategorien"))
    if categories:
        return normalize_category(categories[0])
    for key in ("mahlzeit", "landkuche", "landkueche", "category"):
        value = str(row.get(key) or "").strip()
        if value:
            return normalize_category(value)
    return DEFAULT_CATEGORY


def _build_instructions(row: dict[str, Any]) -> str:
    instructions = parse_text_block(row.get("zubereitung") or row.get("instructions") or row.get("steps"))
    return instructions or "No instructions provided."


def _build_description(row: dict[str, Any]) -> str:
    description = str(row.get("beschreibung") or row.get("description") or "").strip()
    return description or "Imported from KochWiki."


def _find_existing_recipe(
    db: Session,
    source_uuid: str | None,
    title_normalized: str,
    source_url: str | None,
) -> Recipe | None:
    if source_uuid:
        recipe = db.scalar(select(Recipe).where(Recipe.source_uuid == source_uuid))
        if recipe:
            return recipe
    if source_url:
        return db.scalar(
            select(Recipe).where(
                func.lower(Recipe.title) == title_normalized,
                Recipe.source_url == source_url,
            )
        )
    return None


def _apply_update_fields(recipe: Recipe, payload: dict[str, Any]) -> None:
    recipe.description = payload["description"]
    recipe.instructions = payload["instructions"]
    recipe.category = payload["category"]
    recipe.total_time_minutes = payload["total_time_minutes"]
    recipe.prep_time_minutes = payload["prep_time_minutes"]
    recipe.difficulty = payload["difficulty"]
    recipe.servings_text = payload["servings_text"]
    if payload["source_url"] and not recipe.source_url:
        recipe.source_url = payload["source_url"]
    if payload["source_uuid"] and not recipe.source_uuid:
        recipe.source_uuid = payload["source_uuid"]
    if payload["source_image_url"]:
        recipe.source_image_url = payload["source_image_url"]
        recipe.title_image_url = payload["source_image_url"]
    recipe.source = recipe.source or "kochwiki"


def _download_image_if_enabled(db: Session, recipe: Recipe, source_image_url: str | None) -> None:
    if not settings.import_download_images or not source_image_url:
        return
    resolved_url = resolve_title_image_url(source_image_url)
    if not resolved_url:
        return
    request = Request(resolved_url, headers={"User-Agent": "MealMate/1.0"})
    with urlopen(request, timeout=12) as response:
        content_type = str(response.headers.get("Content-Type") or "").split(";")[0].strip().lower()
        data = response.read(settings.max_upload_mb * 1024 * 1024 + 1)
    validate_upload(content_type, len(data), data)
    filename = Path(urlparse(resolved_url).path).name or "import-image"
    db.add(
        RecipeImage(
            recipe_id=recipe.id,
            filename=filename[:255],
            content_type=content_type,
            data=data,
        )
    )


def _prepare_kochwiki_payload(row: dict[str, Any]) -> dict[str, Any]:
    title = _clean_title(row.get("titel") or row.get("title") or row.get("name"))
    if not title:
        raise ValueError("missing title")
    source_url = str(row.get("quelle_url") or row.get("source_url") or "").strip()[:1024] or None
    source_uuid = str(row.get("rezept_uuid") or row.get("source_uuid") or "").strip()[:120] or None
    source_image_url = _parse_source_image_url(row.get("titelbild") or row.get("source_image_url"))
    prep_time_minutes = parse_optional_int(row.get("zeit_prep_min"))
    if prep_time_minutes is None:
        prep_time_minutes = parse_optional_int(row.get("arbeitszeit")) or 30
    total_time_minutes = parse_optional_int(row.get("zeit_total_min"))
    if total_time_minutes is None:
        total_time_minutes = parse_optional_int(row.get("arbeitszeit"))
    servings_text = str(row.get("portionen_text") or row.get("portionen") or "").strip()[:120] or None
    payload = {
        "title": title,
        "title_normalized": _normalize_title_for_match(title),
        "source": "kochwiki",
        "source_uuid": source_uuid,
        "source_url": source_url,
        "source_image_url": source_image_url,
        "description": _build_description(row),
        "instructions": _build_instructions(row),
        "category": _build_category(row),
        "prep_time_minutes": prep_time_minutes,
        "difficulty": sanitize_difficulty(str(row.get("schwierigkeit") or row.get("difficulty") or "medium")),
        "servings_text": servings_text,
        "total_time_minutes": total_time_minutes,
        "ingredients": _parse_kochwiki_ingredients(row.get("zutaten")),
    }
    return payload


def import_kochwiki_csv(
    db: Session,
    csv_source: str | Path | bytes,
    creator_id: int,
    mode: IMPORT_MODE = "insert_only",
    batch_size: int = 200,
    autocommit: bool = True,
) -> CSVImportReport:
    if mode not in {"insert_only", "update_existing"}:
        raise ValueError("mode must be 'insert_only' or 'update_existing'")
    rows = read_kochwiki_csv_bytes(csv_source) if isinstance(csv_source, bytes) else read_kochwiki_csv(csv_source)
    report = CSVImportReport()
    pending_writes = 0
    for row_index, row in enumerate(rows, start=2):
        try:
            payload = _prepare_kochwiki_payload(row)
            with db.begin_nested():
                existing = _find_existing_recipe(
                    db,
                    payload["source_uuid"],
                    payload["title_normalized"],
                    payload["source_url"],
                )
                if existing and mode == "insert_only":
                    report.skipped += 1
                    continue
                if existing and mode == "update_existing":
                    _apply_update_fields(existing, payload)
                    replace_recipe_ingredients(db, existing, payload["ingredients"])
                    db.add(existing)
                    report.updated += 1
                    pending_writes += 1
                    continue
                recipe = Recipe(
                    title=payload["title"],
                    title_image_url=payload["source_image_url"],
                    source=payload["source"],
                    source_uuid=payload["source_uuid"],
                    source_url=payload["source_url"],
                    source_image_url=payload["source_image_url"],
                    servings_text=payload["servings_text"],
                    total_time_minutes=payload["total_time_minutes"],
                    description=payload["description"],
                    instructions=payload["instructions"],
                    category=payload["category"],
                    prep_time_minutes=payload["prep_time_minutes"],
                    difficulty=payload["difficulty"],
                    creator_id=creator_id,
                )
                db.add(recipe)
                db.flush()
                replace_recipe_ingredients(db, recipe, payload["ingredients"])
                _download_image_if_enabled(db, recipe, payload["source_image_url"])
                report.inserted += 1
                pending_writes += 1
            if pending_writes >= batch_size:
                if autocommit:
                    db.commit()
                else:
                    db.flush()
                pending_writes = 0
        except Exception as exc:
            report.skipped += 1
            report.errors.append(f"Row {row_index}: {exc}")
    if pending_writes > 0:
        if autocommit:
            db.commit()
        else:
            db.flush()
    return report


def build_recipe_pdf(recipe: Recipe, avg_rating: float, review_count: int) -> bytes:
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    top = height - 50
    if recipe.images:
        image = recipe.images[0]
        image_reader = ImageReader(io.BytesIO(image.data))
        pdf.drawImage(image_reader, 50, top - 120, width=120, height=90, preserveAspectRatio=True, mask="auto")
        top -= 130
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(50, top, recipe.title)
    top -= 24
    pdf.setFont("Helvetica", 11)
    meta = f"Category: {recipe.category} | Difficulty: {recipe.difficulty} | Prep: {recipe.prep_time_minutes} min"
    pdf.drawString(50, top, meta)
    top -= 18
    rating_line = f"Average rating: {avg_rating:.2f} ({review_count} reviews)"
    pdf.drawString(50, top, rating_line)
    top -= 26
    pdf.setFont("Helvetica-Bold", 13)
    pdf.drawString(50, top, "Ingredients")
    top -= 18
    pdf.setFont("Helvetica", 11)
    for link in recipe.recipe_ingredients:
        line = f"- {link.ingredient.name} {link.quantity_text}".strip()
        if link.grams:
            line = f"{line} ({link.grams} g)"
        top = draw_wrapped_line(pdf, line, 50, top, width - 100)
        if top < 100:
            pdf.showPage()
            top = height - 50
            pdf.setFont("Helvetica", 11)
    top -= 6
    pdf.setFont("Helvetica-Bold", 13)
    pdf.drawString(50, top, "Instructions")
    top -= 18
    pdf.setFont("Helvetica", 11)
    for paragraph in [piece.strip() for piece in recipe.instructions.splitlines() if piece.strip()]:
        top = draw_wrapped_line(pdf, paragraph, 50, top, width - 100)
        top -= 4
        if top < 80:
            pdf.showPage()
            top = height - 50
            pdf.setFont("Helvetica", 11)
    pdf.save()
    buffer.seek(0)
    return buffer.getvalue()


def draw_wrapped_line(pdf: canvas.Canvas, text: str, x: int, y: int, max_width: int) -> int:
    words = text.split()
    current = ""
    for word in words:
        trial = f"{current} {word}".strip()
        if pdf.stringWidth(trial, "Helvetica", 11) <= max_width:
            current = trial
            continue
        pdf.drawString(x, y, current)
        y -= 14
        current = word
    if current:
        pdf.drawString(x, y, current)
        y -= 14
    return y


def readable_file_size(size_bytes: int) -> str:
    return f"{size_bytes / (1024 * 1024):.2f} MB"

```
ZEILEN-ERKLAERUNG
1. Diese Zeile importiert benoetigte Module fuer die folgenden Funktionen.
2. Diese Zeile importiert benoetigte Module fuer die folgenden Funktionen.
3. Diese Zeile importiert benoetigte Module fuer die folgenden Funktionen.
4. Diese Zeile importiert benoetigte Module fuer die folgenden Funktionen.
5. Diese Zeile importiert benoetigte Module fuer die folgenden Funktionen.
6. Diese Zeile importiert gezielt Elemente aus einem anderen Modul.
7. Diese Zeile importiert gezielt Elemente aus einem anderen Modul.
8. Diese Zeile importiert gezielt Elemente aus einem anderen Modul.
9. Diese Zeile importiert gezielt Elemente aus einem anderen Modul.
10. Diese Zeile importiert gezielt Elemente aus einem anderen Modul.
11. Diese Zeile importiert gezielt Elemente aus einem anderen Modul.
12. Diese Zeile importiert gezielt Elemente aus einem anderen Modul.
13. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
14. Diese Zeile importiert gezielt Elemente aus einem anderen Modul.
15. Diese Zeile importiert gezielt Elemente aus einem anderen Modul.
16. Diese Zeile importiert gezielt Elemente aus einem anderen Modul.
17. Diese Zeile importiert gezielt Elemente aus einem anderen Modul.
18. Diese Zeile importiert gezielt Elemente aus einem anderen Modul.
19. Diese Zeile importiert gezielt Elemente aus einem anderen Modul.
20. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
21. Diese Zeile importiert gezielt Elemente aus einem anderen Modul.
22. Diese Zeile importiert gezielt Elemente aus einem anderen Modul.
23. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
24. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
25. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
26. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
27. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
28. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
29. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
30. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
31. Diese Zeile deklariert einen Decorator fuer die nachfolgende Funktion.
32. Diese Zeile startet die Definition einer Klasse.
33. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
34. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
35. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
36. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
37. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
38. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
39. Diese Zeile startet die Definition einer Funktion.
40. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
41. Diese Zeile startet eine Schleife ueber mehrere Elemente.
42. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
43. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
44. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
45. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
46. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
47. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
48. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
49. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
50. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
51. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
52. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
53. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
54. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
55. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
56. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
57. Diese Zeile startet die Definition einer Funktion.
58. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
59. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
60. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
61. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
62. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
63. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
64. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
65. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
66. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
67. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
68. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
69. Diese Zeile startet die Definition einer Funktion.
70. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
71. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
72. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
73. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
74. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
75. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
76. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
77. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
78. Diese Zeile startet die Definition einer Funktion.
79. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
80. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
81. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
82. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
83. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
84. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
85. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
86. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
87. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
88. Diese Zeile startet die Definition einer Funktion.
89. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
90. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
91. Diese Zeile startet eine Schleife ueber mehrere Elemente.
92. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
93. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
94. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
95. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
96. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
97. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
98. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
99. Diese Zeile startet die Definition einer Funktion.
100. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
101. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
102. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
103. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
104. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
105. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
106. Diese Zeile startet die Definition einer Funktion.
107. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
108. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
109. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
110. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
111. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
112. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
113. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
114. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
115. Diese Zeile startet die Definition einer Funktion.
116. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
117. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
118. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
119. Diese Zeile startet die Definition einer Funktion.
120. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
121. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
122. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
123. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
124. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
125. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
126. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
127. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
128. Diese Zeile startet einen Fehlerbehandlungsblock.
129. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
130. Diese Zeile faengt einen moeglichen Fehler aus dem Try-Block ab.
131. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
132. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
133. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
134. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
135. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
136. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
137. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
138. Diese Zeile startet die Definition einer Funktion.
139. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
140. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
141. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
142. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
143. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
144. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
145. Diese Zeile startet die Definition einer Funktion.
146. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
147. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
148. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
149. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
150. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
151. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
152. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
153. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
154. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
155. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
156. Diese Zeile startet die Definition einer Funktion.
157. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
158. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
159. Diese Zeile startet eine Schleife ueber mehrere Elemente.
160. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
161. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
162. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
163. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
164. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
165. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
166. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
167. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
168. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
169. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
170. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
171. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
172. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
173. Diese Zeile definiert den Alternativzweig der vorherigen Bedingung.
174. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
175. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
176. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
177. Diese Zeile startet eine Schleife ueber mehrere Elemente.
178. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
179. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
180. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
181. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
182. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
183. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
184. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
185. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
186. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
187. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
188. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
189. Diese Zeile startet die Definition einer Funktion.
190. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
191. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
192. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
193. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
194. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
195. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
196. Diese Zeile startet einen Fehlerbehandlungsblock.
197. Diese Zeile oeffnet einen Kontextmanager fuer sichere Ressourcenverwaltung.
198. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
199. Diese Zeile faengt einen moeglichen Fehler aus dem Try-Block ab.
200. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
201. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
202. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
203. Diese Zeile deklariert einen Decorator fuer die nachfolgende Funktion.
204. Diese Zeile startet die Definition einer Funktion.
205. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
206. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
207. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
208. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
209. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
210. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
211. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
212. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
213. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
214. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
215. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
216. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
217. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
218. Diese Zeile oeffnet einen Kontextmanager fuer sichere Ressourcenverwaltung.
219. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
220. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
221. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
222. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
223. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
224. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
225. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
226. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
227. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
228. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
229. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
230. Diese Zeile startet die Definition einer Funktion.
231. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
232. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
233. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
234. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
235. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
236. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
237. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
238. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
239. Diese Zeile startet die Definition einer Funktion.
240. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
241. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
242. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
243. Diese Zeile startet die Definition einer Funktion.
244. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
245. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
246. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
247. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
248. Diese Zeile startet die Definition einer Funktion.
249. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
250. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
251. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
252. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
253. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
254. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
255. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
256. Diese Zeile startet die Definition einer Funktion.
257. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
258. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
259. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
260. Diese Zeile startet die Definition einer Funktion.
261. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
262. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
263. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
264. Diese Zeile startet die Definition einer Funktion.
265. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
266. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
267. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
268. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
269. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
270. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
271. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
272. Diese Zeile startet die Definition einer Funktion.
273. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
274. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
275. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
276. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
277. Diese Zeile startet die Definition einer Funktion.
278. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
279. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
280. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
281. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
282. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
283. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
284. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
285. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
286. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
287. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
288. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
289. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
290. Diese Zeile startet die Definition einer Funktion.
291. Diese Zeile startet eine Schleife ueber mehrere Elemente.
292. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
293. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
294. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
295. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
296. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
297. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
298. Diese Zeile startet die Definition einer Funktion.
299. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
300. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
301. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
302. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
303. Diese Zeile startet die Definition einer Funktion.
304. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
305. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
306. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
307. Diese Zeile startet die Definition einer Funktion.
308. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
309. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
310. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
311. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
312. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
313. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
314. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
315. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
316. Diese Zeile startet die Definition einer Funktion.
317. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
318. Diese Zeile startet eine Schleife ueber mehrere Elemente.
319. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
320. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
321. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
322. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
323. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
324. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
325. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
326. Diese Zeile definiert den Alternativzweig der vorherigen Bedingung.
327. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
328. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
329. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
330. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
331. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
332. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
333. Diese Zeile startet die Definition einer Funktion.
334. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
335. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
336. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
337. Diese Zeile startet eine Schleife ueber mehrere Elemente.
338. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
339. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
340. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
341. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
342. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
343. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
344. Diese Zeile startet die Definition einer Funktion.
345. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
346. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
347. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
348. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
349. Diese Zeile startet die Definition einer Funktion.
350. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
351. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
352. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
353. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
354. Diese Zeile startet die Definition einer Funktion.
355. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
356. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
357. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
358. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
359. Diese Zeile oeffnet einen neuen logisch eingerueckten Block.
360. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
361. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
362. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
363. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
364. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
365. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
366. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
367. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
368. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
369. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
370. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
371. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
372. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
373. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
374. Diese Zeile startet die Definition einer Funktion.
375. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
376. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
377. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
378. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
379. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
380. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
381. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
382. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
383. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
384. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
385. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
386. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
387. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
388. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
389. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
390. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
391. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
392. Diese Zeile startet die Definition einer Funktion.
393. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
394. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
395. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
396. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
397. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
398. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
399. Diese Zeile oeffnet einen Kontextmanager fuer sichere Ressourcenverwaltung.
400. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
401. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
402. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
403. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
404. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
405. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
406. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
407. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
408. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
409. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
410. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
411. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
412. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
413. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
414. Diese Zeile startet die Definition einer Funktion.
415. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
416. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
417. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
418. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
419. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
420. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
421. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
422. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
423. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
424. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
425. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
426. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
427. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
428. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
429. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
430. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
431. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
432. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
433. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
434. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
435. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
436. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
437. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
438. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
439. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
440. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
441. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
442. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
443. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
444. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
445. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
446. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
447. Diese Zeile startet die Definition einer Funktion.
448. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
449. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
450. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
451. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
452. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
453. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
454. Diese Zeile oeffnet einen neuen logisch eingerueckten Block.
455. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
456. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
457. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
458. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
459. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
460. Diese Zeile startet eine Schleife ueber mehrere Elemente.
461. Diese Zeile startet einen Fehlerbehandlungsblock.
462. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
463. Diese Zeile oeffnet einen Kontextmanager fuer sichere Ressourcenverwaltung.
464. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
465. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
466. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
467. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
468. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
469. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
470. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
471. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
472. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
473. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
474. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
475. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
476. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
477. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
478. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
479. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
480. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
481. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
482. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
483. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
484. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
485. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
486. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
487. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
488. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
489. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
490. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
491. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
492. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
493. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
494. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
495. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
496. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
497. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
498. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
499. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
500. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
501. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
502. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
503. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
504. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
505. Diese Zeile definiert den Alternativzweig der vorherigen Bedingung.
506. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
507. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
508. Diese Zeile faengt einen moeglichen Fehler aus dem Try-Block ab.
509. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
510. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
511. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
512. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
513. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
514. Diese Zeile definiert den Alternativzweig der vorherigen Bedingung.
515. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
516. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
517. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
518. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
519. Diese Zeile startet die Definition einer Funktion.
520. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
521. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
522. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
523. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
524. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
525. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
526. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
527. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
528. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
529. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
530. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
531. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
532. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
533. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
534. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
535. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
536. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
537. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
538. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
539. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
540. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
541. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
542. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
543. Diese Zeile startet eine Schleife ueber mehrere Elemente.
544. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
545. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
546. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
547. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
548. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
549. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
550. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
551. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
552. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
553. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
554. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
555. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
556. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
557. Diese Zeile startet eine Schleife ueber mehrere Elemente.
558. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
559. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
560. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
561. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
562. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
563. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
564. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
565. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
566. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
567. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
568. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
569. Diese Zeile startet die Definition einer Funktion.
570. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
571. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
572. Diese Zeile startet eine Schleife ueber mehrere Elemente.
573. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
574. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
575. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
576. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
577. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
578. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
579. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
580. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
581. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
582. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
583. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
584. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
585. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
586. Diese Zeile startet die Definition einer Funktion.
587. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.

## app/routers/recipes.py
```python
from io import BytesIO

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status
from fastapi.responses import RedirectResponse, Response, StreamingResponse
from sqlalchemy import and_, desc, func, select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.database import get_db
from app.dependencies import get_current_user, get_current_user_optional, template_context
from app.image_utils import ImageValidationError, safe_image_filename, validate_image_upload
from app.models import Favorite, Ingredient, Recipe, RecipeImage, RecipeIngredient, Review, User
from app.pdf_service import build_recipe_pdf
from app.rate_limit import key_by_user_or_ip, limiter
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


def ensure_recipe_access(user: User, recipe: Recipe) -> None:
    if not can_manage_recipe(user, recipe):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions for this recipe.")


def get_primary_image(recipe: Recipe) -> RecipeImage | None:
    for image in recipe.images:
        if image.is_primary:
            return image
    return recipe.images[0] if recipe.images else None


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


def render_image_section(request: Request, db: Session, recipe_id: int, current_user: User | None):
    recipe = fetch_recipe_or_404(db, recipe_id)
    primary_image = get_primary_image(recipe)
    return templates.TemplateResponse(
        "partials/recipe_images.html",
        template_context(
            request,
            current_user,
            recipe=recipe,
            primary_image=primary_image,
        ),
    )


@router.get("/")
def home_page(
    request: Request,
    page: int = 1,
    per_page: int = PAGE_SIZE_DEFAULT,
    sort: str = "date",
    title: str = "",
    category: str = "",
    difficulty: str = "",
    ingredient: str = "",
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    page = max(page, 1)
    if per_page not in PAGE_SIZE_OPTIONS:
        per_page = PAGE_SIZE_DEFAULT
    category_index = build_category_index(db)
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
    recipes_data = [{"recipe": row[0], "avg_rating": float(row[1] or 0), "review_count": int(row[2] or 0)} for row in rows]
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
    )
    if request.headers.get("HX-Request") == "true":
        return templates.TemplateResponse("partials/recipe_list.html", context)
    return templates.TemplateResponse("home.html", context)


@router.get("/recipes/new")
def create_recipe_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return templates.TemplateResponse(
        "recipe_form.html",
        template_context(
            request,
            current_user,
            recipe=None,
            error=None,
            form_mode="create",
            category_options=get_distinct_categories(db),
            selected_category=DEFAULT_CATEGORY,
            category_new_value="",
        ),
    )


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
    current_user: User = Depends(get_current_user),
):
    prep_time = parse_positive_int(prep_time_minutes, "prep_time_minutes")
    normalized_difficulty = sanitize_difficulty(difficulty)
    if not title.strip() or not instructions.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Title and instructions are required.")
    recipe = Recipe(
        title=title.strip(),
        title_image_url=normalize_image_url(title_image_url),
        description=description.strip(),
        instructions=instructions.strip(),
        category=resolve_category_value(category_select, category_new, category),
        prep_time_minutes=prep_time,
        difficulty=normalized_difficulty,
        creator_id=current_user.id,
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
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    recipe = fetch_recipe_or_404(db, recipe_id)
    avg_rating = db.scalar(select(func.coalesce(func.avg(Review.rating), 0)).where(Review.recipe_id == recipe_id)) or 0
    review_count = db.scalar(select(func.count(Review.id)).where(Review.recipe_id == recipe_id)) or 0
    primary_image = get_primary_image(recipe)
    is_favorite = False
    if current_user:
        is_favorite = db.scalar(
            select(Favorite).where(and_(Favorite.user_id == current_user.id, Favorite.recipe_id == recipe_id))
        ) is not None
    return templates.TemplateResponse(
        "recipe_detail.html",
        template_context(
            request,
            current_user,
            recipe=recipe,
            avg_rating=float(avg_rating),
            review_count=int(review_count),
            is_favorite=is_favorite,
            primary_image=primary_image,
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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    recipe = db.scalar(select(Recipe).where(Recipe.id == recipe_id))
    if not recipe:
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
        return templates.TemplateResponse(
            "partials/favorite_button.html",
            template_context(request, current_user, recipe=recipe, is_favorite=is_favorite),
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
        .where(Favorite.user_id == current_user.id)
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
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _ = response
    recipe = fetch_recipe_or_404(db, recipe_id)
    ensure_recipe_access(current_user, recipe)
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
        return render_image_section(request, db, recipe_id, current_user)
    return redirect(f"/recipes/{recipe_id}")


@router.get("/images/{image_id}")
def get_image(image_id: int, db: Session = Depends(get_db)):
    image = db.scalar(select(RecipeImage).where(RecipeImage.id == image_id))
    if not image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found.")
    return Response(content=image.data, media_type=image.content_type)


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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found.")
    ensure_recipe_access(current_user, image.recipe)
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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found.")
    recipe = image.recipe
    recipe_id = image.recipe_id
    ensure_recipe_access(current_user, recipe)
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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found.")
    recipe = image.recipe
    ensure_recipe_access(current_user, recipe)
    set_recipe_primary_image(db, recipe, image.id)
    db.commit()
    if request.headers.get("HX-Request") == "true":
        return render_image_section(request, db, recipe.id, current_user)
    return redirect(f"/recipes/{recipe.id}")


@router.get("/recipes/{recipe_id}/pdf")
def recipe_pdf(
    recipe_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    recipe = fetch_recipe_or_404(db, recipe_id)
    avg_rating = db.scalar(select(func.coalesce(func.avg(Review.rating), 0)).where(Review.recipe_id == recipe_id)) or 0
    review_count = db.scalar(select(func.count(Review.id)).where(Review.recipe_id == recipe_id)) or 0
    pdf_bytes = build_recipe_pdf(recipe, float(avg_rating), int(review_count))
    filename = f"mealmate_recipe_{recipe_id}.pdf"
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return StreamingResponse(BytesIO(pdf_bytes), media_type="application/pdf", headers=headers)


@router.get("/categories")
def categories_api(db: Session = Depends(get_db)):
    return {"categories": get_distinct_categories(db)}

```
ZEILEN-ERKLAERUNG
1. Diese Zeile importiert gezielt Elemente aus einem anderen Modul.
2. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
3. Diese Zeile importiert gezielt Elemente aus einem anderen Modul.
4. Diese Zeile importiert gezielt Elemente aus einem anderen Modul.
5. Diese Zeile importiert gezielt Elemente aus einem anderen Modul.
6. Diese Zeile importiert gezielt Elemente aus einem anderen Modul.
7. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
8. Diese Zeile importiert gezielt Elemente aus einem anderen Modul.
9. Diese Zeile importiert gezielt Elemente aus einem anderen Modul.
10. Diese Zeile importiert gezielt Elemente aus einem anderen Modul.
11. Diese Zeile importiert gezielt Elemente aus einem anderen Modul.
12. Diese Zeile importiert gezielt Elemente aus einem anderen Modul.
13. Diese Zeile importiert gezielt Elemente aus einem anderen Modul.
14. Diese Zeile importiert gezielt Elemente aus einem anderen Modul.
15. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
16. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
17. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
18. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
19. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
20. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
21. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
22. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
23. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
24. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
25. Diese Zeile importiert gezielt Elemente aus einem anderen Modul.
26. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
27. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
28. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
29. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
30. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
31. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
32. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
33. Diese Zeile startet die Definition einer Funktion.
34. Diese Zeile startet einen Fehlerbehandlungsblock.
35. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
36. Diese Zeile faengt einen moeglichen Fehler aus dem Try-Block ab.
37. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
38. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
39. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
40. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
41. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
42. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
43. Diese Zeile startet die Definition einer Funktion.
44. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
45. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
46. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
47. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
48. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
49. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
50. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
51. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
52. Diese Zeile startet die Definition einer Funktion.
53. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
54. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
55. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
56. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
57. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
58. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
59. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
60. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
61. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
62. Diese Zeile startet die Definition einer Funktion.
63. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
64. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
65. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
66. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
67. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
68. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
69. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
70. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
71. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
72. Diese Zeile startet die Definition einer Funktion.
73. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
74. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
75. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
76. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
77. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
78. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
79. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
80. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
81. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
82. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
83. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
84. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
85. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
86. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
87. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
88. Diese Zeile startet die Definition einer Funktion.
89. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
90. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
91. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
92. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
93. Diese Zeile startet die Definition einer Funktion.
94. Diese Zeile startet eine Schleife ueber mehrere Elemente.
95. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
96. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
97. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
98. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
99. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
100. Diese Zeile startet die Definition einer Funktion.
101. Diese Zeile startet eine Schleife ueber mehrere Elemente.
102. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
103. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
104. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
105. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
106. Diese Zeile startet die Definition einer Funktion.
107. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
108. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
109. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
110. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
111. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
112. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
113. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
114. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
115. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
116. Diese Zeile startet die Definition einer Funktion.
117. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
118. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
119. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
120. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
121. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
122. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
123. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
124. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
125. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
126. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
127. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
128. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
129. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
130. Diese Zeile deklariert einen Decorator fuer die nachfolgende Funktion.
131. Diese Zeile startet die Definition einer Funktion.
132. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
133. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
134. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
135. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
136. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
137. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
138. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
139. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
140. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
141. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
142. Diese Zeile oeffnet einen neuen logisch eingerueckten Block.
143. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
144. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
145. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
146. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
147. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
148. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
149. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
150. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
151. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
152. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
153. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
154. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
155. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
156. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
157. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
158. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
159. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
160. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
161. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
162. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
163. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
164. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
165. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
166. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
167. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
168. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
169. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
170. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
171. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
172. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
173. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
174. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
175. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
176. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
177. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
178. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
179. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
180. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
181. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
182. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
183. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
184. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
185. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
186. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
187. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
188. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
189. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
190. Diese Zeile definiert den Alternativzweig der vorherigen Bedingung.
191. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
192. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
193. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
194. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
195. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
196. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
197. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
198. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
199. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
200. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
201. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
202. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
203. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
204. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
205. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
206. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
207. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
208. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
209. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
210. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
211. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
212. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
213. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
214. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
215. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
216. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
217. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
218. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
219. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
220. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
221. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
222. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
223. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
224. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
225. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
226. Diese Zeile deklariert einen Decorator fuer die nachfolgende Funktion.
227. Diese Zeile startet die Definition einer Funktion.
228. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
229. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
230. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
231. Diese Zeile oeffnet einen neuen logisch eingerueckten Block.
232. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
233. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
234. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
235. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
236. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
237. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
238. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
239. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
240. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
241. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
242. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
243. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
244. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
245. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
246. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
247. Diese Zeile deklariert einen Decorator fuer die nachfolgende Funktion.
248. Diese Zeile startet die Definition einer asynchronen Funktion.
249. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
250. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
251. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
252. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
253. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
254. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
255. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
256. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
257. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
258. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
259. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
260. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
261. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
262. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
263. Diese Zeile oeffnet einen neuen logisch eingerueckten Block.
264. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
265. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
266. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
267. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
268. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
269. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
270. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
271. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
272. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
273. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
274. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
275. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
276. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
277. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
278. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
279. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
280. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
281. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
282. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
283. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
284. Diese Zeile startet einen Fehlerbehandlungsblock.
285. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
286. Diese Zeile faengt einen moeglichen Fehler aus dem Try-Block ab.
287. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
288. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
289. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
290. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
291. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
292. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
293. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
294. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
295. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
296. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
297. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
298. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
299. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
300. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
301. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
302. Diese Zeile deklariert einen Decorator fuer die nachfolgende Funktion.
303. Diese Zeile startet die Definition einer Funktion.
304. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
305. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
306. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
307. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
308. Diese Zeile oeffnet einen neuen logisch eingerueckten Block.
309. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
310. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
311. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
312. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
313. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
314. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
315. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
316. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
317. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
318. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
319. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
320. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
321. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
322. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
323. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
324. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
325. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
326. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
327. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
328. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
329. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
330. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
331. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
332. Diese Zeile deklariert einen Decorator fuer die nachfolgende Funktion.
333. Diese Zeile startet die Definition einer Funktion.
334. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
335. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
336. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
337. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
338. Diese Zeile oeffnet einen neuen logisch eingerueckten Block.
339. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
340. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
341. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
342. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
343. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
344. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
345. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
346. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
347. Diese Zeile startet eine Schleife ueber mehrere Elemente.
348. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
349. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
350. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
351. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
352. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
353. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
354. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
355. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
356. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
357. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
358. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
359. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
360. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
361. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
362. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
363. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
364. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
365. Diese Zeile deklariert einen Decorator fuer die nachfolgende Funktion.
366. Diese Zeile startet die Definition einer asynchronen Funktion.
367. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
368. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
369. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
370. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
371. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
372. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
373. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
374. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
375. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
376. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
377. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
378. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
379. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
380. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
381. Diese Zeile oeffnet einen neuen logisch eingerueckten Block.
382. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
383. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
384. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
385. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
386. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
387. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
388. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
389. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
390. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
391. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
392. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
393. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
394. Diese Zeile startet einen Fehlerbehandlungsblock.
395. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
396. Diese Zeile faengt einen moeglichen Fehler aus dem Try-Block ab.
397. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
398. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
399. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
400. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
401. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
402. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
403. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
404. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
405. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
406. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
407. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
408. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
409. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
410. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
411. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
412. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
413. Diese Zeile deklariert einen Decorator fuer die nachfolgende Funktion.
414. Diese Zeile startet die Definition einer Funktion.
415. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
416. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
417. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
418. Diese Zeile oeffnet einen neuen logisch eingerueckten Block.
419. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
420. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
421. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
422. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
423. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
424. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
425. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
426. Diese Zeile deklariert einen Decorator fuer die nachfolgende Funktion.
427. Diese Zeile startet die Definition einer Funktion.
428. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
429. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
430. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
431. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
432. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
433. Diese Zeile oeffnet einen neuen logisch eingerueckten Block.
434. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
435. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
436. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
437. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
438. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
439. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
440. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
441. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
442. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
443. Diese Zeile definiert den Alternativzweig der vorherigen Bedingung.
444. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
445. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
446. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
447. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
448. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
449. Diese Zeile deklariert einen Decorator fuer die nachfolgende Funktion.
450. Diese Zeile startet die Definition einer Funktion.
451. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
452. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
453. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
454. Diese Zeile oeffnet einen neuen logisch eingerueckten Block.
455. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
456. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
457. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
458. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
459. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
460. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
461. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
462. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
463. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
464. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
465. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
466. Diese Zeile deklariert einen Decorator fuer die nachfolgende Funktion.
467. Diese Zeile startet die Definition einer Funktion.
468. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
469. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
470. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
471. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
472. Diese Zeile oeffnet einen neuen logisch eingerueckten Block.
473. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
474. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
475. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
476. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
477. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
478. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
479. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
480. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
481. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
482. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
483. Diese Zeile definiert den Alternativzweig der vorherigen Bedingung.
484. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
485. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
486. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
487. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
488. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
489. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
490. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
491. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
492. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
493. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
494. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
495. Diese Zeile deklariert einen Decorator fuer die nachfolgende Funktion.
496. Diese Zeile startet die Definition einer Funktion.
497. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
498. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
499. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
500. Diese Zeile oeffnet einen neuen logisch eingerueckten Block.
501. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
502. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
503. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
504. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
505. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
506. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
507. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
508. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
509. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
510. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
511. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
512. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
513. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
514. Diese Zeile deklariert einen Decorator fuer die nachfolgende Funktion.
515. Diese Zeile startet die Definition einer Funktion.
516. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
517. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
518. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
519. Diese Zeile oeffnet einen neuen logisch eingerueckten Block.
520. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
521. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
522. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
523. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
524. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
525. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
526. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
527. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
528. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
529. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
530. Diese Zeile deklariert einen Decorator fuer die nachfolgende Funktion.
531. Diese Zeile deklariert einen Decorator fuer die nachfolgende Funktion.
532. Diese Zeile startet die Definition einer asynchronen Funktion.
533. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
534. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
535. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
536. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
537. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
538. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
539. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
540. Diese Zeile oeffnet einen neuen logisch eingerueckten Block.
541. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
542. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
543. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
544. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
545. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
546. Diese Zeile startet einen Fehlerbehandlungsblock.
547. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
548. Diese Zeile faengt einen moeglichen Fehler aus dem Try-Block ab.
549. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
550. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
551. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
552. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
553. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
554. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
555. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
556. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
557. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
558. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
559. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
560. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
561. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
562. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
563. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
564. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
565. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
566. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
567. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
568. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
569. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
570. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
571. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
572. Diese Zeile deklariert einen Decorator fuer die nachfolgende Funktion.
573. Diese Zeile startet die Definition einer Funktion.
574. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
575. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
576. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
577. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
578. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
579. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
580. Diese Zeile deklariert einen Decorator fuer die nachfolgende Funktion.
581. Diese Zeile startet die Definition einer Funktion.
582. Diese Zeile startet einen Fehlerbehandlungsblock.
583. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
584. Diese Zeile faengt einen moeglichen Fehler aus dem Try-Block ab.
585. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
586. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
587. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
588. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
589. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
590. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
591. Diese Zeile deklariert einen Decorator fuer die nachfolgende Funktion.
592. Diese Zeile startet die Definition einer Funktion.
593. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
594. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
595. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
596. Diese Zeile oeffnet einen neuen logisch eingerueckten Block.
597. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
598. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
599. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
600. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
601. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
602. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
603. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
604. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
605. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
606. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
607. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
608. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
609. Diese Zeile deklariert einen Decorator fuer die nachfolgende Funktion.
610. Diese Zeile startet die Definition einer Funktion.
611. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
612. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
613. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
614. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
615. Diese Zeile oeffnet einen neuen logisch eingerueckten Block.
616. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
617. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
618. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
619. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
620. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
621. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
622. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
623. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
624. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
625. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
626. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
627. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
628. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
629. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
630. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
631. Diese Zeile deklariert einen Decorator fuer die nachfolgende Funktion.
632. Diese Zeile startet die Definition einer Funktion.
633. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
634. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
635. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
636. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
637. Diese Zeile oeffnet einen neuen logisch eingerueckten Block.
638. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
639. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
640. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
641. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
642. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
643. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
644. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
645. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
646. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
647. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
648. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
649. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
650. Diese Zeile deklariert einen Decorator fuer die nachfolgende Funktion.
651. Diese Zeile startet die Definition einer Funktion.
652. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
653. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
654. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
655. Diese Zeile oeffnet einen neuen logisch eingerueckten Block.
656. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
657. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
658. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
659. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
660. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
661. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
662. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
663. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
664. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
665. Diese Zeile deklariert einen Decorator fuer die nachfolgende Funktion.
666. Diese Zeile startet die Definition einer Funktion.
667. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.

## app/routers/admin.py
```python
import logging
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, Response, UploadFile, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.config import get_settings
from app.database import get_db
from app.dependencies import get_admin_user, template_context
from app.i18n import t
from app.models import Recipe, User
from app.rate_limit import key_by_user_or_ip, limiter
from app.services import get_category_stats, import_kochwiki_csv, is_meta_true, set_meta_value
from app.views import redirect, templates

router = APIRouter(tags=["admin"])
settings = get_settings()
logger = logging.getLogger("mealmate.admin")


def admin_dashboard_context(
    request: Request,
    db: Session,
    current_user: User,
    report=None,
    error: str | None = None,
    message: str | None = None,
):
    users = db.scalars(select(User).order_by(User.created_at.desc())).all()
    recipes = db.scalars(
        select(Recipe).order_by(Recipe.created_at.desc()).options(selectinload(Recipe.creator))
    ).all()
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
        error=error,
        message=message,
        seed_done=is_meta_true(db, "kochwiki_seed_done"),
        default_csv_path=settings.kochwiki_csv_path,
        distinct_category_count=distinct_category_count,
        top_categories=top_categories,
    )


@router.get("/admin")
def admin_panel(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    return templates.TemplateResponse("admin.html", admin_dashboard_context(request, db, current_user))


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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    _ = response
    max_bytes = settings.max_csv_upload_mb * 1024 * 1024
    mode = "insert_only"
    if update_existing:
        mode = "update_existing"
    elif not insert_only:
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
        report = import_kochwiki_csv(
            db,
            raw_bytes,
            current_user.id,
            mode=mode,
            autocommit=False,
        )
        db.commit()
        message = t("error.import_finished_insert")
        if mode == "update_existing":
            message = t("error.import_finished_update")
        return templates.TemplateResponse(
            "admin.html",
            admin_dashboard_context(request, db, current_user, report=report, message=message),
        )
    except (FileNotFoundError, ValueError) as exc:
        db.rollback()
        return templates.TemplateResponse(
            "admin.html",
            admin_dashboard_context(request, db, current_user, error=str(exc)),
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    except Exception:
        db.rollback()
        raise

```
ZEILEN-ERKLAERUNG
1. Diese Zeile importiert benoetigte Module fuer die folgenden Funktionen.
2. Diese Zeile importiert gezielt Elemente aus einem anderen Modul.
3. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
4. Diese Zeile importiert gezielt Elemente aus einem anderen Modul.
5. Diese Zeile importiert gezielt Elemente aus einem anderen Modul.
6. Diese Zeile importiert gezielt Elemente aus einem anderen Modul.
7. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
8. Diese Zeile importiert gezielt Elemente aus einem anderen Modul.
9. Diese Zeile importiert gezielt Elemente aus einem anderen Modul.
10. Diese Zeile importiert gezielt Elemente aus einem anderen Modul.
11. Diese Zeile importiert gezielt Elemente aus einem anderen Modul.
12. Diese Zeile importiert gezielt Elemente aus einem anderen Modul.
13. Diese Zeile importiert gezielt Elemente aus einem anderen Modul.
14. Diese Zeile importiert gezielt Elemente aus einem anderen Modul.
15. Diese Zeile importiert gezielt Elemente aus einem anderen Modul.
16. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
17. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
18. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
19. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
20. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
21. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
22. Diese Zeile startet die Definition einer Funktion.
23. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
24. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
25. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
26. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
27. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
28. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
29. Diese Zeile oeffnet einen neuen logisch eingerueckten Block.
30. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
31. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
32. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
33. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
34. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
35. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
36. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
37. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
38. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
39. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
40. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
41. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
42. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
43. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
44. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
45. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
46. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
47. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
48. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
49. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
50. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
51. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
52. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
53. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
54. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
55. Diese Zeile deklariert einen Decorator fuer die nachfolgende Funktion.
56. Diese Zeile startet die Definition einer Funktion.
57. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
58. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
59. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
60. Diese Zeile oeffnet einen neuen logisch eingerueckten Block.
61. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
62. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
63. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
64. Diese Zeile deklariert einen Decorator fuer die nachfolgende Funktion.
65. Diese Zeile startet die Definition einer Funktion.
66. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
67. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
68. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
69. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
70. Diese Zeile oeffnet einen neuen logisch eingerueckten Block.
71. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
72. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
73. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
74. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
75. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
76. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
77. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
78. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
79. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
80. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
81. Diese Zeile deklariert einen Decorator fuer die nachfolgende Funktion.
82. Diese Zeile startet die Definition einer Funktion.
83. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
84. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
85. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
86. Diese Zeile oeffnet einen neuen logisch eingerueckten Block.
87. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
88. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
89. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
90. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
91. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
92. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
93. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
94. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
95. Diese Zeile deklariert einen Decorator fuer die nachfolgende Funktion.
96. Diese Zeile startet die Definition einer Funktion.
97. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
98. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
99. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
100. Diese Zeile oeffnet einen neuen logisch eingerueckten Block.
101. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
102. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
103. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
104. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
105. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
106. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
107. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
108. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
109. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
110. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
111. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
112. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
113. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
114. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
115. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
116. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
117. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
118. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
119. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
120. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
121. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
122. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
123. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
124. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
125. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
126. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
127. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
128. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
129. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
130. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
131. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
132. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
133. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
134. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
135. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
136. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
137. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
138. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
139. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
140. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
141. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
142. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
143. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
144. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
145. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
146. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
147. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
148. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
149. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
150. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
151. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
152. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
153. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
154. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
155. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
156. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
157. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
158. Diese Zeile deklariert einen Decorator fuer die nachfolgende Funktion.
159. Diese Zeile deklariert einen Decorator fuer die nachfolgende Funktion.
160. Diese Zeile startet die Definition einer asynchronen Funktion.
161. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
162. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
163. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
164. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
165. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
166. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
167. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
168. Diese Zeile oeffnet einen neuen logisch eingerueckten Block.
169. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
170. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
171. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
172. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
173. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
174. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
175. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
176. Diese Zeile startet einen Fehlerbehandlungsblock.
177. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
178. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
179. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
180. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
181. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
182. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
183. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
184. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
185. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
186. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
187. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
188. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
189. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
190. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
191. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
192. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
193. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
194. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
195. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
196. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
197. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
198. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
199. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
200. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
201. Diese Zeile faengt einen moeglichen Fehler aus dem Try-Block ab.
202. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
203. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
204. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
205. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
206. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
207. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
208. Diese Zeile faengt einen moeglichen Fehler aus dem Try-Block ab.
209. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
210. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.

## app/templates/home.html
```html
{% extends "base.html" %}
{% block content %}
<section class="panel">
  <h1>{{ t("home.title") }}</h1>
  <form class="grid" hx-get="/" hx-target="#recipe-list" hx-push-url="true">
    <input type="text" name="title" value="{{ title }}" placeholder="{{ t('home.title_contains') }}">
    <select name="category">
      <option value="">{{ t("home.all_categories") }}</option>
      {% for option in category_options %}
      <option value="{{ option }}" {% if category == option %}selected{% endif %}>{{ option }}</option>
      {% endfor %}
    </select>
    <select name="difficulty">
      <option value="">{{ t("home.difficulty") }}</option>
      <option value="easy" {% if difficulty == "easy" %}selected{% endif %}>{{ t("difficulty.easy") }}</option>
      <option value="medium" {% if difficulty == "medium" %}selected{% endif %}>{{ t("difficulty.medium") }}</option>
      <option value="hard" {% if difficulty == "hard" %}selected{% endif %}>{{ t("difficulty.hard") }}</option>
    </select>
    <input type="text" name="ingredient" value="{{ ingredient }}" placeholder="{{ t('home.ingredient') }}">
    <select name="sort">
      <option value="date" {% if sort == "date" %}selected{% endif %}>{{ t("sort.newest") }}</option>
      <option value="prep_time" {% if sort == "prep_time" %}selected{% endif %}>{{ t("sort.prep_time") }}</option>
      <option value="avg_rating" {% if sort == "avg_rating" %}selected{% endif %}>{{ t("sort.highest_rated") }}</option>
    </select>
    <select name="per_page">
      {% for option in per_page_options %}
      <option value="{{ option }}" {% if per_page == option %}selected{% endif %}>{{ t("home.per_page") }}: {{ option }}</option>
      {% endfor %}
    </select>
    <button type="submit">{{ t("home.apply") }}</button>
  </form>
</section>
<section id="recipe-list">
  {% include "partials/recipe_list.html" %}
</section>
{% endblock %}

```
ZEILEN-ERKLAERUNG
1. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
2. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
3. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
4. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
5. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
6. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
7. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
8. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
9. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
10. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
11. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
12. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
13. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
14. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
15. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
16. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
17. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
18. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
19. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
20. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
21. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
22. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
23. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
24. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
25. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
26. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
27. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
28. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
29. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
30. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
31. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
32. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
33. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
34. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
35. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
36. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.

## app/templates/partials/recipe_list.html
```html
<p class="list-summary">
  {% if total > 0 %}
  {{ t("pagination.results_range", start=start_item, end=end_item, total=total) }}
  {% else %}
  {{ t("recipe.no_results") }}
  {% endif %}
</p>
<div class="cards">
  {% for entry in recipes_data %}
  {% set recipe = entry.recipe %}
  <article class="card">
    {% if recipe.images %}
    <img src="/images/{{ recipe.images[0].id }}" alt="{{ recipe.title }}" class="thumb">
    {% elif recipe.title_image_url %}
    <img src="/external-image?url={{ recipe.title_image_url|urlencode }}" alt="{{ recipe.title }}" class="thumb">
    {% endif %}
    <h3><a href="/recipes/{{ recipe.id }}">{{ recipe.title }}</a></h3>
    <p class="summary">{{ recipe.description }}</p>
    <p class="meta">{{ recipe.category }} | {{ difficulty_label(recipe.difficulty) }} | {{ recipe.prep_time_minutes }} min</p>
    <p class="meta">{{ t("recipe.rating_short") }} {{ "%.2f"|format(entry.avg_rating) }} ({{ entry.review_count }})</p>
  </article>
  {% endfor %}
</div>
{% if pages > 1 %}
{% set filter_query = "per_page=" ~ per_page ~ "&sort=" ~ (sort|urlencode) ~ "&title=" ~ (title|urlencode) ~ "&category=" ~ (category|urlencode) ~ "&difficulty=" ~ (difficulty|urlencode) ~ "&ingredient=" ~ (ingredient|urlencode) %}
<div class="pagination">
  <div class="pagination-links">
    {% if page > 1 %}
    <a href="/?page={{ page - 1 }}&{{ filter_query }}" hx-get="/?page={{ page - 1 }}&{{ filter_query }}" hx-target="#recipe-list" hx-push-url="true">{{ t("pagination.previous") }}</a>
    {% else %}
    <span class="disabled">{{ t("pagination.previous") }}</span>
    {% endif %}
    {% for item in pagination_items %}
    {% if item is none %}
    <span class="ellipsis">...</span>
    {% elif item == page %}
    <span class="active">{{ item }}</span>
    {% else %}
    <a href="/?page={{ item }}&{{ filter_query }}" hx-get="/?page={{ item }}&{{ filter_query }}" hx-target="#recipe-list" hx-push-url="true">{{ item }}</a>
    {% endif %}
    {% endfor %}
    {% if page < pages %}
    <a href="/?page={{ page + 1 }}&{{ filter_query }}" hx-get="/?page={{ page + 1 }}&{{ filter_query }}" hx-target="#recipe-list" hx-push-url="true">{{ t("pagination.next") }}</a>
    {% else %}
    <span class="disabled">{{ t("pagination.next") }}</span>
    {% endif %}
  </div>
  <span class="pagination-info">{{ t("pagination.page") }} {{ page }} / {{ total_pages }}</span>
</div>
{% endif %}

```
ZEILEN-ERKLAERUNG
1. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
2. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
3. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
4. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
5. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
6. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
7. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
8. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
9. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
10. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
11. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
12. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
13. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
14. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
15. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
16. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
17. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
18. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
19. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
20. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
21. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
22. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
23. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
24. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
25. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
26. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
27. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
28. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
29. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
30. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
31. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
32. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
33. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
34. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
35. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
36. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
37. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
38. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
39. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
40. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
41. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
42. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
43. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
44. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
45. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
46. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
47. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
48. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
49. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
50. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.

## app/templates/recipe_form.html
```html
{% extends "base.html" %}
{% block content %}
<section class="panel">
  <h1>{% if form_mode == "edit" %}{{ t("recipe_form.edit_title") }}{% else %}{{ t("recipe_form.create_title") }}{% endif %}</h1>
  {% if error %}<p class="error">{{ error }}</p>{% endif %}
  <form method="post" enctype="multipart/form-data" class="stack" action="{% if form_mode == 'edit' %}/recipes/{{ recipe.id }}/edit{% else %}/recipes/new{% endif %}">
    <label>{{ t("recipe_form.title") }} <input type="text" name="title" value="{{ recipe.title if recipe else '' }}" required></label>
    <label>{{ t("recipe_form.title_image_url") }} <input type="url" name="title_image_url" value="{{ recipe.title_image_url if recipe else '' }}" placeholder="https://..."></label>
    <label>{{ t("recipe_form.description") }} <textarea name="description" rows="3" required>{{ recipe.description if recipe else '' }}</textarea></label>
    <label>{{ t("recipe_form.instructions") }} <textarea name="instructions" rows="8" required>{{ recipe.instructions if recipe else '' }}</textarea></label>
    <label>{{ t("recipe_form.category") }}
      <select name="category_select" id="category_select">
        {% for option in category_options %}
        <option value="{{ option }}" {% if selected_category == option %}selected{% endif %}>{{ option }}</option>
        {% endfor %}
        <option value="__new__">{{ t("recipe_form.new_category_option") }}</option>
      </select>
    </label>
    <div id="new-category-wrapper" class="stack hidden">
      <label>{{ t("recipe_form.new_category_label") }} <input type="text" id="category_new" name="category_new" value="{{ category_new_value }}"></label>
    </div>
    <label>{{ t("recipe_form.prep_time") }} <input type="number" min="1" name="prep_time_minutes" value="{{ recipe.prep_time_minutes if recipe else 30 }}" required></label>
    <label>{{ t("recipe_form.difficulty") }}
      <select name="difficulty">
        <option value="easy" {% if recipe and recipe.difficulty == "easy" %}selected{% endif %}>{{ t("difficulty.easy") }}</option>
        <option value="medium" {% if not recipe or recipe.difficulty == "medium" %}selected{% endif %}>{{ t("difficulty.medium") }}</option>
        <option value="hard" {% if recipe and recipe.difficulty == "hard" %}selected{% endif %}>{{ t("difficulty.hard") }}</option>
      </select>
    </label>
    <label>{{ t("recipe_form.ingredients") }}
      <textarea name="ingredients_text" rows="8">{{ ingredients_text if ingredients_text else '' }}</textarea>
    </label>
    <label>{{ t("recipe_form.optional_image") }} <input type="file" name="image" accept="image/png,image/jpeg,image/webp"></label>
    <button type="submit">{% if form_mode == "edit" %}{{ t("recipe_form.save") }}{% else %}{{ t("recipe_form.create") }}{% endif %}</button>
  </form>
</section>
{% endblock %}

```
ZEILEN-ERKLAERUNG
1. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
2. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
3. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
4. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
5. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
6. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
7. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
8. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
9. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
10. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
11. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
12. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
13. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
14. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
15. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
16. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
17. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
18. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
19. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
20. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
21. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
22. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
23. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
24. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
25. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
26. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
27. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
28. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
29. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
30. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
31. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
32. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
33. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
34. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
35. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
36. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
37. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.

## app/templates/admin.html
```html
{% extends "base.html" %}
{% block content %}
<section class="panel">
  <h1>{{ t("admin.title") }}</h1>
  {% if message %}
  <p class="meta">{{ message }}</p>
  {% endif %}
  {% if error %}
  <p class="error">{{ error }}</p>
  {% endif %}
</section>
<section class="panel">
  <h2>{{ t("admin.seed_title") }}</h2>
  <p class="meta">{{ t("admin.csv_path") }}: {{ default_csv_path }}</p>
  {% if seed_done %}
  <p class="meta">{{ t("admin.seed_done") }}</p>
  {% else %}
  <form method="post" action="/admin/run-kochwiki-seed">
    <button type="submit">{{ t("admin.seed_run") }}</button>
  </form>
  {% endif %}
</section>
<section class="panel">
  <h2>{{ t("admin.import_title") }}</h2>
  <form method="post" action="/admin/import-recipes" enctype="multipart/form-data" class="stack">
    <label>{{ t("admin.upload_label") }}
      <input type="file" name="file" accept=".csv" required>
    </label>
    <label class="inline">
      <input type="checkbox" name="insert_only" checked>
      {{ t("admin.insert_only") }}
    </label>
    <label class="inline">
      <input type="checkbox" name="update_existing">
      {{ t("admin.update_existing") }}
    </label>
    <button type="submit">{{ t("admin.start_import") }}</button>
  </form>
  {% if report %}
  <p class="meta">
    {{ t("admin.report_inserted") }}: {{ report.inserted }},
    {{ t("admin.report_updated") }}: {{ report.updated }},
    {{ t("admin.report_skipped") }}: {{ report.skipped }},
    {{ t("admin.report_errors") }}: {{ report.errors|length }}
  </p>
  {% if report.errors %}
  <ul>
    {% for item in report.errors %}
    <li>{{ item }}</li>
    {% endfor %}
  </ul>
  {% endif %}
  {% endif %}
</section>
<section class="panel">
  <h2>{{ t("admin.category_stats_title") }}</h2>
  <p class="meta">{{ t("admin.category_distinct_count") }}: {{ distinct_category_count }}</p>
  <h3>{{ t("admin.category_top") }}</h3>
  <ul>
    {% for category_name, category_count in top_categories %}
    <li>{{ category_name }} ({{ category_count }})</li>
    {% endfor %}
  </ul>
</section>
<section class="panel">
  <h2>{{ t("admin.users") }}</h2>
  <table>
    <thead>
      <tr><th>{{ t("admin.id") }}</th><th>{{ t("admin.email") }}</th><th>{{ t("admin.role") }}</th><th>{{ t("admin.action") }}</th></tr>
    </thead>
    <tbody>
      {% for user in users %}
      <tr>
        <td>{{ user.id }}</td>
        <td>{{ user.email }}</td>
        <td>{{ role_label(user.role) }}</td>
        <td>
          <form method="post" action="/admin/users/{{ user.id }}/role" class="inline">
            <select name="role">
              <option value="user" {% if user.role == "user" %}selected{% endif %}>{{ t("role.user") }}</option>
              <option value="admin" {% if user.role == "admin" %}selected{% endif %}>{{ t("role.admin") }}</option>
            </select>
            <button type="submit">{{ t("admin.save") }}</button>
          </form>
        </td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
</section>
<section class="panel">
  <h2>{{ t("admin.recipes") }}</h2>
  <table>
    <thead>
      <tr><th>{{ t("admin.id") }}</th><th>{{ t("admin.title_column") }}</th><th>{{ t("admin.creator") }}</th><th>{{ t("admin.source") }}</th><th>{{ t("admin.action") }}</th></tr>
    </thead>
    <tbody>
      {% for recipe in recipes %}
      <tr>
        <td>{{ recipe.id }}</td>
        <td><a href="/recipes/{{ recipe.id }}">{{ recipe.title }}</a></td>
        <td>{{ recipe.creator.email }}</td>
        <td>{{ recipe.source }}</td>
        <td>
          <form method="post" action="/admin/recipes/{{ recipe.id }}/delete">
            <button type="submit">{{ t("recipe.delete") }}</button>
          </form>
        </td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
</section>
{% endblock %}

```
ZEILEN-ERKLAERUNG
1. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
2. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
3. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
4. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
5. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
6. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
7. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
8. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
9. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
10. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
11. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
12. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
13. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
14. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
15. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
16. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
17. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
18. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
19. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
20. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
21. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
22. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
23. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
24. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
25. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
26. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
27. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
28. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
29. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
30. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
31. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
32. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
33. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
34. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
35. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
36. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
37. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
38. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
39. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
40. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
41. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
42. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
43. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
44. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
45. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
46. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
47. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
48. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
49. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
50. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
51. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
52. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
53. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
54. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
55. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
56. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
57. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
58. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
59. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
60. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
61. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
62. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
63. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
64. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
65. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
66. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
67. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
68. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
69. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
70. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
71. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
72. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
73. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
74. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
75. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
76. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
77. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
78. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
79. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
80. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
81. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
82. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
83. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
84. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
85. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
86. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
87. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
88. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
89. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
90. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
91. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
92. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
93. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
94. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
95. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
96. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
97. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
98. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
99. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
100. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
101. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
102. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
103. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
104. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
105. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
106. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
107. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
108. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
109. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
110. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
111. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
112. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
113. Diese Zeile enthaelt ein HTML-Element fuer die Benutzeroberflaeche.
114. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.

## app/static/style.css
```css
:root {
  --bg: #f8f7f3;
  --panel: #ffffff;
  --ink: #1d2433;
  --accent: #0f766e;
  --danger: #b91c1c;
  --border: #d1d5db;
  --font: "Segoe UI", "Trebuchet MS", sans-serif;
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  color: var(--ink);
  background: radial-gradient(circle at top right, #e8f5f1, var(--bg));
  font-family: var(--font);
}

.topbar {
  position: sticky;
  top: 0;
  z-index: 9;
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: center;
  padding: 1rem;
  background: #fff;
  border-bottom: 1px solid var(--border);
}

.brand {
  text-decoration: none;
  color: var(--accent);
  font-weight: 700;
  font-size: 1.25rem;
}

nav {
  display: flex;
  flex-wrap: wrap;
  gap: 0.6rem;
  align-items: center;
}

a {
  color: var(--accent);
}

.container {
  max-width: 1080px;
  margin: 1.2rem auto;
  padding: 0 1rem 2rem;
}

.panel {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 1rem;
  margin-bottom: 1rem;
  box-shadow: 0 5px 14px rgba(0, 0, 0, 0.05);
}

.narrow {
  max-width: 480px;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
  gap: 0.5rem;
}

.stack {
  display: grid;
  gap: 0.7rem;
}

.cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
  gap: 0.8rem;
}

.card {
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 0.8rem;
  background: #fff;
}

.card h3 {
  margin: 0.2rem 0 0.4rem;
  font-size: 1rem;
  line-height: 1.3;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.meta {
  color: #4b5563;
  font-size: 0.95rem;
}

.summary {
  margin: 0.2rem 0 0.45rem;
  color: #24303f;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.thumb {
  width: 100%;
  height: 160px;
  object-fit: cover;
  border-radius: 8px;
  margin-bottom: 0.5rem;
}

.hero-image {
  width: 100%;
  max-height: 380px;
  object-fit: cover;
  border-radius: 10px;
  margin-bottom: 0.8rem;
}

input,
select,
textarea,
button {
  width: 100%;
  padding: 0.55rem 0.6rem;
  border-radius: 8px;
  border: 1px solid var(--border);
  font: inherit;
}

button {
  cursor: pointer;
  background: var(--accent);
  color: #fff;
  border: none;
}

.inline {
  display: inline-flex;
  gap: 0.4rem;
  align-items: center;
}

.inline button,
.inline input,
.inline select {
  width: auto;
}

.actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.7rem;
}

.hidden {
  display: none !important;
}

.error {
  color: var(--danger);
  font-weight: 700;
}

.pagination {
  display: grid;
  justify-items: center;
  gap: 0.55rem;
  margin-top: 1rem;
}

.list-summary {
  margin: 0.3rem 0 0.8rem;
  font-weight: 600;
}

.pagination-links {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 0.4rem;
  align-items: center;
}

.pagination-links a {
  min-width: 2rem;
  text-align: center;
  text-decoration: none;
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 0.35rem 0.55rem;
  background: #fff;
}

.pagination-links .active {
  min-width: 2rem;
  text-align: center;
  border: 1px solid var(--accent);
  border-radius: 8px;
  padding: 0.35rem 0.55rem;
  background: var(--accent);
  color: #fff;
}

.pagination-links .disabled {
  min-width: 2rem;
  text-align: center;
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 0.35rem 0.55rem;
  color: #9ca3af;
  background: #f3f4f6;
}

.pagination-links .ellipsis {
  min-width: 2rem;
  text-align: center;
  padding: 0.35rem 0.55rem;
  color: #6b7280;
}

.pagination-info {
  color: #4b5563;
  font-size: 0.95rem;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th,
td {
  border-bottom: 1px solid var(--border);
  padding: 0.6rem 0.4rem;
  text-align: left;
}

```
ZEILEN-ERKLAERUNG
1. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
2. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
3. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
4. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
5. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
6. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
7. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
8. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
9. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
10. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
11. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
12. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
13. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
14. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
15. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
16. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
17. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
18. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
19. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
20. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
21. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
22. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
23. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
24. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
25. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
26. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
27. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
28. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
29. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
30. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
31. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
32. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
33. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
34. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
35. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
36. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
37. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
38. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
39. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
40. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
41. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
42. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
43. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
44. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
45. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
46. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
47. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
48. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
49. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
50. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
51. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
52. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
53. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
54. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
55. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
56. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
57. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
58. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
59. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
60. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
61. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
62. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
63. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
64. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
65. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
66. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
67. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
68. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
69. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
70. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
71. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
72. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
73. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
74. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
75. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
76. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
77. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
78. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
79. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
80. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
81. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
82. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
83. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
84. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
85. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
86. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
87. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
88. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
89. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
90. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
91. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
92. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
93. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
94. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
95. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
96. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
97. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
98. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
99. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
100. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
101. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
102. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
103. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
104. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
105. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
106. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
107. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
108. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
109. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
110. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
111. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
112. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
113. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
114. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
115. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
116. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
117. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
118. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
119. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
120. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
121. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
122. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
123. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
124. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
125. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
126. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
127. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
128. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
129. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
130. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
131. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
132. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
133. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
134. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
135. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
136. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
137. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
138. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
139. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
140. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
141. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
142. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
143. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
144. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
145. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
146. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
147. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
148. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
149. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
150. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
151. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
152. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
153. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
154. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
155. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
156. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
157. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
158. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
159. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
160. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
161. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
162. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
163. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
164. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
165. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
166. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
167. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
168. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
169. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
170. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
171. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
172. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
173. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
174. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
175. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
176. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
177. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
178. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
179. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
180. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
181. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
182. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
183. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
184. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
185. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
186. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
187. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
188. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
189. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
190. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
191. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
192. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
193. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
194. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
195. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
196. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
197. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
198. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
199. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
200. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
201. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
202. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
203. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
204. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
205. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
206. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
207. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
208. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
209. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
210. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
211. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
212. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
213. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
214. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
215. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
216. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
217. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
218. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
219. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
220. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
221. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
222. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
223. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
224. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
225. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
226. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
227. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
228. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
229. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
230. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
231. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
232. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
233. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
234. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
235. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
236. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
237. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
238. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
239. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
240. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
241. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
242. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
243. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
244. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
245. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
246. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
247. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
248. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
249. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
250. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
251. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
252. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
253. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
254. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.

## app/static/security.js
```javascript
function getCookie(name) {
  const parts = document.cookie ? document.cookie.split("; ") : [];
  for (const part of parts) {
    const splitIndex = part.indexOf("=");
    if (splitIndex === -1) {
      continue;
    }
    const key = decodeURIComponent(part.slice(0, splitIndex));
    if (key === name) {
      return decodeURIComponent(part.slice(splitIndex + 1));
    }
  }
  return "";
}

function addCsrfInput(form, token) {
  if (!token) {
    return;
  }
  const method = (form.getAttribute("method") || "get").toUpperCase();
  if (!["POST", "PUT", "PATCH", "DELETE"].includes(method)) {
    return;
  }
  let csrfInput = form.querySelector('input[name="csrf_token"]');
  if (!csrfInput) {
    csrfInput = document.createElement("input");
    csrfInput.type = "hidden";
    csrfInput.name = "csrf_token";
    form.appendChild(csrfInput);
  }
  csrfInput.value = token;
}

function injectCsrfIntoForms() {
  const token = getCookie("csrf_token");
  document.querySelectorAll("form").forEach((form) => addCsrfInput(form, token));
}

function initCategorySelector() {
  const select = document.getElementById("category_select");
  const wrapper = document.getElementById("new-category-wrapper");
  const input = document.getElementById("category_new");
  if (!select || !wrapper || !input || select.dataset.categoryInit === "1") {
    return;
  }
  const syncCategoryMode = () => {
    const useNewCategory = select.value === "__new__";
    wrapper.classList.toggle("hidden", !useNewCategory);
    input.required = useNewCategory;
    if (!useNewCategory) {
      input.value = "";
    }
  };
  select.addEventListener("change", syncCategoryMode);
  select.dataset.categoryInit = "1";
  syncCategoryMode();
}

document.addEventListener("DOMContentLoaded", () => {
  injectCsrfIntoForms();
  initCategorySelector();
});

document.addEventListener(
  "submit",
  (event) => {
    const form = event.target;
    if (!(form instanceof HTMLFormElement)) {
      return;
    }
    addCsrfInput(form, getCookie("csrf_token"));
  },
  true
);

document.body.addEventListener("htmx:configRequest", (event) => {
  const token = getCookie("csrf_token");
  if (!token) {
    return;
  }
  event.detail.headers["X-CSRF-Token"] = token;
});

document.body.addEventListener("htmx:afterSwap", () => {
  injectCsrfIntoForms();
  initCategorySelector();
});

```
ZEILEN-ERKLAERUNG
1. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
2. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
3. Diese Zeile startet eine Schleife ueber mehrere Elemente.
4. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
5. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
6. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
7. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
8. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
9. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
10. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
11. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
12. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
13. Diese Zeile gibt einen Rueckgabewert aus der aktuellen Funktion zurueck.
14. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
15. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
16. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
17. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
18. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
19. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
20. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
21. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
22. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
23. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
24. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
25. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
26. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
27. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
28. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
29. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
30. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
31. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
32. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
33. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
34. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
35. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
36. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
37. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
38. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
39. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
40. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
41. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
42. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
43. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
44. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
45. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
46. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
47. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
48. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
49. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
50. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
51. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
52. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
53. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
54. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
55. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
56. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
57. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
58. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
59. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
60. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
61. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
62. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
63. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
64. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
65. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
66. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
67. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
68. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
69. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
70. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
71. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
72. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
73. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
74. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
75. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
76. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
77. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
78. Diese Zeile prueft eine Bedingung fuer den weiteren Kontrollfluss.
79. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
80. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
81. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
82. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
83. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
84. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
85. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
86. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
87. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.

## app/i18n/de.py
```python
DE_TEXTS: dict[str, str] = {
    "app.name": "MealMate",
    "nav.discover": "Rezepte entdecken",
    "nav.create_recipe": "Rezept erstellen",
    "nav.my_recipes": "Meine Rezepte",
    "nav.favorites": "Favoriten",
    "nav.profile": "Mein Profil",
    "nav.admin": "Admin",
    "nav.login": "Anmelden",
    "nav.register": "Registrieren",
    "nav.logout": "Abmelden",
    "home.title": "Rezepte entdecken",
    "home.title_contains": "Titel enthaelt",
    "home.category": "Kategorie",
    "home.all_categories": "Alle Kategorien",
    "home.difficulty": "Schwierigkeit",
    "home.ingredient": "Zutat",
    "home.per_page": "Pro Seite",
    "home.apply": "Anwenden",
    "sort.newest": "Neueste",
    "sort.oldest": "Aelteste",
    "sort.highest_rated": "Beste Bewertung",
    "sort.lowest_rated": "Schlechteste Bewertung",
    "sort.prep_time": "Zubereitungszeit",
    "pagination.previous": "Zurueck",
    "pagination.next": "Weiter",
    "pagination.first": "Erste",
    "pagination.last": "Letzte",
    "pagination.page": "Seite",
    "pagination.results_range": "Zeige {start}-{end} von {total} Rezepten",
    "difficulty.easy": "Einfach",
    "difficulty.medium": "Mittel",
    "difficulty.hard": "Schwer",
    "role.user": "Nutzer",
    "role.admin": "Administrator",
    "auth.login_title": "Anmelden",
    "auth.register_title": "Registrieren",
    "auth.email": "E-Mail",
    "auth.password": "Passwort",
    "auth.login_button": "Anmelden",
    "auth.register_button": "Konto erstellen",
    "profile.title": "Mein Profil",
    "profile.email": "E-Mail",
    "profile.role": "Rolle",
    "profile.joined": "Registriert am",
    "favorites.title": "Favoriten",
    "favorites.remove": "Favorit entfernen",
    "favorites.empty": "Keine Favoriten gespeichert.",
    "my_recipes.title": "Meine Rezepte",
    "my_recipes.empty": "Noch keine Rezepte vorhanden.",
    "recipe.edit": "Bearbeiten",
    "recipe.delete": "Loeschen",
    "recipe.pdf_download": "PDF herunterladen",
    "recipe.average_rating": "Durchschnittliche Bewertung",
    "recipe.review_count_label": "Bewertungen",
    "recipe.ingredients": "Zutaten",
    "recipe.instructions": "Anleitung",
    "recipe.reviews": "Bewertungen",
    "recipe.rating": "Bewertung",
    "recipe.comment": "Kommentar",
    "recipe.save_review": "Bewertung speichern",
    "recipe.no_ingredients": "Keine Zutaten gespeichert.",
    "recipe.no_reviews": "Noch keine Bewertungen vorhanden.",
    "recipe.no_results": "Keine Rezepte gefunden.",
    "recipe.rating_short": "Bewertung",
    "recipe_form.create_title": "Rezept erstellen",
    "recipe_form.edit_title": "Rezept bearbeiten",
    "recipe_form.title": "Titel",
    "recipe_form.title_image_url": "Titelbild-URL",
    "recipe_form.description": "Beschreibung",
    "recipe_form.instructions": "Anleitung",
    "recipe_form.category": "Kategorie",
    "recipe_form.new_category_option": "Neue Kategorie...",
    "recipe_form.new_category_label": "Neue Kategorie",
    "recipe_form.prep_time": "Zubereitungszeit (Minuten)",
    "recipe_form.difficulty": "Schwierigkeit",
    "recipe_form.ingredients": "Zutaten (Format: name|menge|gramm)",
    "recipe_form.optional_image": "Optionales Bild",
    "recipe_form.save": "Speichern",
    "recipe_form.create": "Erstellen",
    "images.title": "Bilder",
    "images.new_file": "Neue Bilddatei",
    "images.set_primary": "Als Hauptbild setzen",
    "images.upload": "Bild hochladen",
    "images.primary": "Hauptbild",
    "images.delete": "Loeschen",
    "images.empty": "Noch keine Bilder vorhanden.",
    "favorite.add": "Zu Favoriten",
    "favorite.remove": "Aus Favoriten entfernen",
    "admin.title": "Admin-Bereich",
    "admin.seed_title": "KochWiki-Seed (einmalig)",
    "admin.csv_path": "CSV-Pfad",
    "admin.seed_done": "Seed-Status: bereits ausgefuehrt.",
    "admin.seed_run": "Einmaligen KochWiki-Seed ausfuehren",
    "admin.import_title": "CSV manuell importieren",
    "admin.upload_label": "CSV-Upload",
    "admin.insert_only": "Nur neue hinzufuegen (UPSERT SAFE)",
    "admin.update_existing": "Existierende aktualisieren (Warnung: nur ausgewaehlte Felder!)",
    "admin.start_import": "Import starten",
    "admin.report_inserted": "Neu",
    "admin.report_updated": "Aktualisiert",
    "admin.report_skipped": "Uebersprungen",
    "admin.report_errors": "Fehler",
    "admin.users": "Nutzer",
    "admin.recipes": "Rezepte",
    "admin.category_stats_title": "Kategorien-Status",
    "admin.category_distinct_count": "Anzahl eindeutiger Kategorien",
    "admin.category_top": "Top 10 Kategorien",
    "admin.id": "ID",
    "admin.email": "E-Mail",
    "admin.role": "Rolle",
    "admin.action": "Aktion",
    "admin.save": "Speichern",
    "admin.title_column": "Titel",
    "admin.creator": "Ersteller",
    "admin.source": "Quelle",
    "error.404_title": "404 - Seite nicht gefunden",
    "error.404_text": "Die angeforderte Seite existiert nicht oder wurde verschoben.",
    "error.500_title": "500 - Interner Fehler",
    "error.500_text": "Beim Verarbeiten der Anfrage ist ein unerwarteter Fehler aufgetreten.",
    "error.home_link": "Zur Startseite",
    "error.trace": "Stacktrace (nur Dev)",
    "error.auth_required": "Anmeldung erforderlich.",
    "error.admin_required": "Administratorrechte erforderlich.",
    "error.invalid_credentials": "Ungueltige Zugangsdaten.",
    "error.email_registered": "Diese E-Mail ist bereits registriert.",
    "error.password_min_length": "Das Passwort muss mindestens 10 Zeichen enthalten.",
    "error.password_upper": "Das Passwort muss mindestens einen Grossbuchstaben enthalten.",
    "error.password_number": "Das Passwort muss mindestens eine Zahl enthalten.",
    "error.password_special": "Das Passwort muss mindestens ein Sonderzeichen enthalten.",
    "error.role_invalid": "Die Rolle muss 'user' oder 'admin' sein.",
    "error.user_not_found": "Nutzer nicht gefunden.",
    "error.recipe_not_found": "Rezept nicht gefunden.",
    "error.review_not_found": "Bewertung nicht gefunden.",
    "error.image_not_found": "Bild nicht gefunden.",
    "error.recipe_permission": "Keine ausreichenden Rechte fuer dieses Rezept.",
    "error.review_permission": "Keine ausreichenden Rechte fuer diese Bewertung.",
    "error.rating_range": "Die Bewertung muss zwischen 1 und 5 liegen.",
    "error.title_instructions_required": "Titel und Anleitung sind erforderlich.",
    "error.image_url_scheme": "Die title_image_url muss mit http:// oder https:// beginnen.",
    "error.no_image_url": "Keine Bild-URL verfuegbar.",
    "error.image_resolve_prefix": "Die Bild-URL konnte nicht aufgeloest werden",
    "error.seed_already_done": "Der KochWiki-Seed ist bereits als abgeschlossen markiert.",
    "error.seed_not_empty": "Der Seed darf nur bei leerer Rezepttabelle laufen.",
    "error.seed_finished_errors": "Der Seed wurde mit Fehlern beendet; Marker wurde nicht gesetzt.",
    "error.seed_success": "Der KochWiki-Seed wurde erfolgreich abgeschlossen und markiert.",
    "error.csv_upload_required": "Bitte eine CSV-Datei hochladen.",
    "error.csv_only": "Es sind nur CSV-Uploads erlaubt.",
    "error.csv_too_large": "CSV-Upload ist zu gross.",
    "error.csv_empty": "Die hochgeladene CSV-Datei ist leer.",
    "error.csv_not_found_prefix": "CSV-Datei nicht gefunden",
    "error.import_finished_insert": "Import im Modus 'nur neu' abgeschlossen.",
    "error.import_finished_update": "Import im Modus 'bestehende aktualisieren' abgeschlossen.",
    "error.csrf_failed": "CSRF-Pruefung fehlgeschlagen.",
    "error.internal": "Interner Serverfehler.",
    "error.field_int": "{field} muss eine ganze Zahl sein.",
    "error.field_positive": "{field} muss groesser als null sein.",
    "error.mime_unsupported": "Nicht unterstuetzter MIME-Typ '{content_type}'.",
    "error.magic_mismatch": "Dateisignatur passt nicht zum Content-Type.",
    "error.webp_signature": "Ungueltige WEBP-Dateisignatur.",
    "error.image_too_large": "Bild ist zu gross. Maximal {max_mb} MB.",
    "error.image_too_small": "Die hochgeladene Datei ist zu klein fuer ein gueltiges Bild.",
    "error.image_invalid": "Die hochgeladene Datei ist kein gueltiges Bild.",
    "error.image_format_mismatch": "Das Bildformat passt nicht zum Content-Type.",
}

```
ZEILEN-ERKLAERUNG
1. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
2. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
3. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
4. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
5. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
6. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
7. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
8. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
9. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
10. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
11. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
12. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
13. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
14. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
15. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
16. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
17. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
18. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
19. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
20. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
21. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
22. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
23. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
24. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
25. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
26. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
27. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
28. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
29. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
30. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
31. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
32. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
33. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
34. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
35. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
36. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
37. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
38. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
39. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
40. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
41. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
42. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
43. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
44. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
45. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
46. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
47. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
48. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
49. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
50. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
51. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
52. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
53. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
54. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
55. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
56. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
57. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
58. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
59. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
60. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
61. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
62. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
63. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
64. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
65. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
66. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
67. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
68. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
69. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
70. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
71. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
72. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
73. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
74. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
75. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
76. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
77. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
78. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
79. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
80. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
81. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
82. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
83. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
84. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
85. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
86. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
87. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
88. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
89. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
90. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
91. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
92. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
93. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
94. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
95. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
96. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
97. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
98. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
99. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
100. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
101. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
102. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
103. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
104. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
105. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
106. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
107. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
108. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
109. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
110. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
111. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
112. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
113. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
114. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
115. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
116. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
117. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
118. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
119. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
120. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
121. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
122. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
123. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
124. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
125. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
126. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
127. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
128. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
129. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
130. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
131. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
132. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
133. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
134. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
135. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
136. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
137. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
138. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
139. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
140. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
141. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
142. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
143. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
144. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
145. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
146. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
147. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
148. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
149. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
150. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
151. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
152. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
153. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
154. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
155. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
156. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
157. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
158. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
159. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
160. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
161. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
162. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
163. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
164. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
165. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
