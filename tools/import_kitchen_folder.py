from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import re
import sqlite3
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.category_canonical import load_category_mapping_rules, suggest_canonical_category
from app.config import get_settings
from app.database import SessionLocal
from app.image_utils import safe_image_filename, validate_image_upload
from app.models import Ingredient, Recipe, RecipeImage, RecipeIngredient, RecipeSubmission, SubmissionImage, SubmissionIngredient, User
from app.security import hash_password
from app.services import normalize_category

try:
    from bs4 import BeautifulSoup
except Exception:
    BeautifulSoup = None

SETTINGS = get_settings()
RECIPE_SUFFIXES = {".json", ".html", ".htm", ".txt", ".md", ".markdown"}
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}
SKIP_RECIPE_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    "node_modules",
    "app",
    "scripts",
    "tests",
    "alembic",
    "templates",
    "static",
}
SKIP_RECIPE_FILENAMES = {
    "requirements.txt",
    "readme.md",
    "readme.txt",
    "license.txt",
    "pipfile",
    "pipfile.lock",
}
DEFAULT_REPORT = "diagnostics/kitchen_import_report.json"
BATCH_SIZE = 50


@dataclass
class RecipeFile:
    path: Path
    relative_path: str


@dataclass
class ImageFile:
    path: Path
    relative_path: str
    size: int


@dataclass
class ParsedRecipe:
    title: str
    description: str
    instructions: str
    ingredients: list[dict[str, Any]]
    category: str


@dataclass
class SqliteRecipeRecord:
    source_uuid: str
    relative_path: str
    parsed: ParsedRecipe
    image: ImageFile | None


@dataclass
class ImportSummary:
    folder: str
    dry_run: bool
    as_submissions: bool
    publish: bool
    creator_email: str
    limit: int | None
    match_strategy: str
    source_mode: str = "files"
    source_db_path: str | None = None
    scanned_recipes: int = 0
    scanned_images: int = 0
    scanned_unknown: int = 0
    processed: int = 0
    inserted: int = 0
    skipped: int = 0
    matched_images: int = 0
    unmatched_recipe_files: list[str] = field(default_factory=list)
    skipped_items: list[dict[str, str]] = field(default_factory=list)
    errors: list[dict[str, str]] = field(default_factory=list)
    unknown_files: list[str] = field(default_factory=list)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Import local folder recipes + images into MealMate DB.")
    parser.add_argument("--folder", required=True, help="Folder to scan recursively.")
    parser.add_argument("--dry-run", action="store_true", help="Validate only, no DB writes.")
    parser.add_argument("--as-submissions", action="store_true", help="Insert into recipe_submissions pending queue.")
    parser.add_argument("--publish", dest="publish", action="store_true", default=True, help="Publish recipes directly.")
    parser.add_argument("--no-publish", dest="publish", action="store_false", help="Insert recipes unpublished.")
    parser.add_argument("--creator-email", default=(SETTINGS.seed_admin_email or "admin@mealmate.local"))
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--match-strategy", choices=["stem", "nearest"], default="stem")
    parser.add_argument("--report", default=DEFAULT_REPORT)
    return parser.parse_args()


def clean_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "").strip())


def normalize_stem(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.casefold())


def make_source_uuid(relative_path: str, title: str) -> str:
    return hashlib.sha1(f"{relative_path}|{title}".encode("utf-8", errors="ignore")).hexdigest()


def make_sqlite_source_uuid(db_path: Path, recipe_id: int) -> str:
    payload = f"sqlite:{db_path.as_posix()}:{recipe_id}"
    return hashlib.sha1(payload.encode("utf-8", errors="ignore")).hexdigest()


def image_content_type(path: Path) -> str:
    guessed, _ = mimetypes.guess_type(path.name)
    if guessed:
        return guessed.lower()
    if path.suffix.lower() in {".jpg", ".jpeg"}:
        return "image/jpeg"
    if path.suffix.lower() == ".png":
        return "image/png"
    if path.suffix.lower() == ".webp":
        return "image/webp"
    return "application/octet-stream"


def parse_ingredient_item(item: Any) -> dict[str, Any] | None:
    if isinstance(item, dict):
        name = clean_text(item.get("name") or item.get("ingredient") or item.get("item") or "")
        if not name:
            return None
        quantity = clean_text(item.get("quantity") or item.get("quantity_text") or item.get("amount") or "")
        grams = int(item["grams"]) if isinstance(item.get("grams"), int) else None
        return {"name": name[:200], "quantity_text": quantity[:120], "grams": grams}
    raw = clean_text(item)
    if not raw:
        return None
    match = re.match(r"^([\d.,/]+\s*[A-Za-z%]*?)\s+(.+)$", raw)
    quantity = clean_text(match.group(1)) if match else ""
    name = clean_text(match.group(2)) if match else raw
    return {"name": name[:200], "quantity_text": quantity[:120], "grams": None}


def parse_ingredients(raw: Any) -> list[dict[str, Any]]:
    if raw is None:
        return []
    if isinstance(raw, (list, tuple)):
        return [p for p in (parse_ingredient_item(item) for item in raw) if p]
    if isinstance(raw, dict):
        parsed = parse_ingredient_item(raw)
        return [parsed] if parsed else []
    text = str(raw).strip()
    if not text:
        return []
    if text.startswith("["):
        try:
            return parse_ingredients(json.loads(text))
        except json.JSONDecodeError:
            pass
    parts = [part.strip("-• \t") for part in re.split(r"\r?\n|\|", text) if part.strip()]
    return [p for p in (parse_ingredient_item(item) for item in parts) if p]


def parse_json_recipe(path: Path) -> ParsedRecipe:
    payload = json.loads(path.read_text(encoding="utf-8", errors="ignore"))
    if not isinstance(payload, dict):
        raise ValueError("JSON root must be an object")
    title = clean_text(payload.get("title") or payload.get("name") or payload.get("recipe_title") or "")
    description = clean_text(payload.get("description") or payload.get("summary") or payload.get("intro") or "")
    raw_steps = payload.get("instructions") or payload.get("steps") or payload.get("method") or payload.get("zubereitung")
    instructions = "\n".join(clean_text(x) for x in raw_steps if clean_text(x)) if isinstance(raw_steps, list) else clean_text(raw_steps)
    ingredients = parse_ingredients(payload.get("ingredients") or payload.get("zutaten") or payload.get("ingredient_list"))
    category = clean_text(payload.get("category") or payload.get("kategorie") or payload.get("course") or "")
    return ParsedRecipe(title, description, instructions, ingredients, category)


def parse_html_recipe_regex(text: str) -> ParsedRecipe:
    def strip_tags(value: str) -> str:
        return clean_text(re.sub(r"<[^>]+>", " ", value))

    title_match = re.search(r"<h1[^>]*>(.*?)</h1>", text, flags=re.IGNORECASE | re.DOTALL)
    if not title_match:
        title_match = re.search(r"<title[^>]*>(.*?)</title>", text, flags=re.IGNORECASE | re.DOTALL)
    title = strip_tags(title_match.group(1)) if title_match else ""
    description_match = re.search(r"<meta[^>]+name=[\"']description[\"'][^>]+content=[\"'](.*?)[\"']", text, flags=re.IGNORECASE)
    description = clean_text(description_match.group(1)) if description_match else ""
    ingredients = [parse_ingredient_item(strip_tags(item)) for item in re.findall(r"<li[^>]*>(.*?)</li>", text, flags=re.IGNORECASE | re.DOTALL)]
    ingredients = [item for item in ingredients if item]
    paragraphs = [strip_tags(item) for item in re.findall(r"<p[^>]*>(.*?)</p>", text, flags=re.IGNORECASE | re.DOTALL)]
    instructions = "\n".join(line for line in paragraphs if line)
    return ParsedRecipe(title, description, instructions, ingredients, "")


def parse_html_recipe(path: Path) -> ParsedRecipe:
    text = path.read_text(encoding="utf-8", errors="ignore")
    if BeautifulSoup is None:
        return parse_html_recipe_regex(text)

    soup = BeautifulSoup(text, "html.parser")
    title_tag = soup.find("h1") or soup.find("title")
    title = clean_text(title_tag.get_text(" ", strip=True) if title_tag else "")
    meta_desc = soup.find("meta", attrs={"name": "description"})
    description = clean_text(meta_desc.get("content")) if meta_desc and meta_desc.get("content") else ""
    if not description:
        first_p = soup.find("p")
        description = clean_text(first_p.get_text(" ", strip=True) if first_p else "")

    category_node = soup.find(attrs={"itemprop": "recipeCategory"})
    category = clean_text(category_node.get_text(" ", strip=True) if category_node else "")

    ingredients: list[dict[str, Any]] = []
    instructions_lines: list[str] = []
    for heading in soup.find_all(["h1", "h2", "h3", "h4", "strong"]):
        label = clean_text(heading.get_text(" ", strip=True)).casefold()
        if "zutat" in label or "ingredient" in label:
            container = heading.find_next(["ul", "ol", "div"])
            if container:
                for node in container.find_all(["li", "p"]):
                    parsed = parse_ingredient_item(node.get_text(" ", strip=True))
                    if parsed:
                        ingredients.append(parsed)
        if "zubereitung" in label or "anleitung" in label or "instruction" in label or "method" in label:
            container = heading.find_next(["ol", "ul", "div", "section"])
            if container:
                for node in container.find_all(["li", "p"]):
                    line = clean_text(node.get_text(" ", strip=True))
                    if line:
                        instructions_lines.append(line)

    if not ingredients:
        ingredients = [
            p
            for node in soup.select("[class*=ingredient], [id*=ingredient]")
            for p in [parse_ingredient_item(node.get_text(" ", strip=True))]
            if p
        ]
    if not instructions_lines:
        instructions_lines = [
            clean_text(node.get_text(" ", strip=True))
            for node in soup.select("[class*=instruction], [id*=instruction], [class*=method], [id*=method]")
            if clean_text(node.get_text(" ", strip=True))
        ]

    instructions = "\n".join(dict.fromkeys(instructions_lines))
    return ParsedRecipe(title, description, instructions, ingredients, category)


def parse_text_recipe(path: Path) -> ParsedRecipe:
    lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    non_empty = [line.strip() for line in lines if line.strip()]
    title = clean_text(non_empty[0]) if non_empty else ""
    category = ""
    section = "description"
    description_lines: list[str] = []
    ingredient_lines: list[str] = []
    instruction_lines: list[str] = []

    for line in lines[1:] if len(lines) > 1 else []:
        raw = line.strip()
        if not raw:
            continue
        normalized = clean_text(raw)
        lowered = normalized.casefold().rstrip(":")
        if lowered.startswith("kategorie"):
            category = clean_text(normalized.split(":", 1)[1] if ":" in normalized else "")
            continue
        if lowered in {"zutaten", "zutatenliste", "ingredients"}:
            section = "ingredients"
            continue
        if lowered in {"zubereitung", "anleitung", "instructions", "steps", "methode"}:
            section = "instructions"
            continue
        if section == "ingredients":
            ingredient_lines.append(normalized)
        elif section == "instructions":
            instruction_lines.append(normalized)
        else:
            description_lines.append(normalized)

    ingredients = [p for p in (parse_ingredient_item(line) for line in ingredient_lines) if p]
    description = clean_text(" ".join(description_lines[:3]))
    instructions = "\n".join(instruction_lines)
    return ParsedRecipe(title, description, instructions, ingredients, category)


def parse_recipe_file(recipe_file: RecipeFile) -> ParsedRecipe:
    suffix = recipe_file.path.suffix.lower()
    if suffix == ".json":
        return parse_json_recipe(recipe_file.path)
    if suffix in {".html", ".htm"}:
        return parse_html_recipe(recipe_file.path)
    return parse_text_recipe(recipe_file.path)


def canonicalize(parsed: ParsedRecipe) -> ParsedRecipe:
    title = clean_text(parsed.title)
    if not title:
        raise ValueError("title missing")
    instructions = clean_text(parsed.instructions)
    if not instructions:
        raise ValueError("instructions missing")
    description = clean_text(parsed.description) or "Import aus Kitchen-Ordner."
    category = normalize_category(parsed.category or "Unkategorisiert")
    ingredients = [p for p in (parse_ingredient_item(item) for item in parsed.ingredients) if p]
    return ParsedRecipe(title[:255], description, instructions, ingredients, category)


def scan_files(folder: Path) -> tuple[list[RecipeFile], list[ImageFile], list[str]]:
    recipes: list[RecipeFile] = []
    images: list[ImageFile] = []
    unknown: list[str] = []
    for path in folder.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(folder).as_posix()
        suffix = path.suffix.lower()
        if (
            suffix in RECIPE_SUFFIXES
            and path.name.casefold() not in SKIP_RECIPE_FILENAMES
            and not any(part.casefold() in SKIP_RECIPE_DIRS for part in path.parts)
        ):
            recipes.append(RecipeFile(path, rel))
        elif suffix in IMAGE_SUFFIXES:
            images.append(ImageFile(path, rel, path.stat().st_size))
        else:
            unknown.append(rel)
    recipes.sort(key=lambda item: item.relative_path.casefold())
    images.sort(key=lambda item: item.relative_path.casefold())
    unknown.sort(key=str.casefold)
    return recipes, images, unknown


def sqlite_has_table(db_path: Path, table_name: str) -> bool:
    connection = sqlite3.connect(str(db_path))
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=? LIMIT 1", (table_name,))
        return cursor.fetchone() is not None
    except sqlite3.Error:
        return False
    finally:
        connection.close()


def detect_source_sqlite_db(folder: Path) -> Path | None:
    candidates = sorted(folder.rglob("*.db"), key=lambda item: item.as_posix().casefold())
    if not candidates:
        return None
    preferred_names = {"kitchen_hell_heaven.db", "kitchenhellheaven.db"}
    for candidate in candidates:
        if candidate.name.casefold() in preferred_names and sqlite_has_table(candidate, "recipes"):
            return candidate
    for candidate in candidates:
        if sqlite_has_table(candidate, "recipes"):
            return candidate
    return None


def resolve_image_file(path: Path, root_folder: Path) -> ImageFile | None:
    if not path.exists() or not path.is_file():
        return None
    if path.suffix.lower() not in IMAGE_SUFFIXES:
        return None
    try:
        relative = path.relative_to(root_folder).as_posix()
    except ValueError:
        relative = path.name
    return ImageFile(path=path, relative_path=relative, size=path.stat().st_size)


def load_sqlite_recipe_records(source_db_path: Path, folder: Path) -> list[SqliteRecipeRecord]:
    connection = sqlite3.connect(str(source_db_path))
    connection.row_factory = sqlite3.Row
    records: list[SqliteRecipeRecord] = []
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT id, title, description, ingredients, instructions, category FROM recipes ORDER BY id ASC")
        recipe_rows = cursor.fetchall()
        image_map: dict[int, str] = {}
        if sqlite_has_table(source_db_path, "recipe_images"):
            cursor.execute(
                """
                SELECT recipe_id, file_path, sort_order, id
                FROM recipe_images
                ORDER BY recipe_id ASC, sort_order ASC, id ASC
                """
            )
            for row in cursor.fetchall():
                recipe_id = int(row["recipe_id"])
                if recipe_id not in image_map and row["file_path"]:
                    image_map[recipe_id] = str(row["file_path"]).strip()

        try:
            db_relative_path = source_db_path.relative_to(folder).as_posix()
        except ValueError:
            db_relative_path = source_db_path.name

        for row in recipe_rows:
            recipe_id = int(row["id"])
            parsed = ParsedRecipe(
                title=clean_text(row["title"]),
                description=clean_text(row["description"]),
                instructions=clean_text(row["instructions"]),
                ingredients=parse_ingredients(row["ingredients"]),
                category=clean_text(row["category"]),
            )
            image_file = None
            stored_path = image_map.get(recipe_id, "")
            if stored_path:
                primary = (source_db_path.parent / stored_path).resolve()
                secondary = (folder / stored_path).resolve()
                image_file = resolve_image_file(primary, folder) or resolve_image_file(secondary, folder)
            records.append(
                SqliteRecipeRecord(
                    source_uuid=make_sqlite_source_uuid(source_db_path, recipe_id),
                    relative_path=f"{db_relative_path}#recipe:{recipe_id}",
                    parsed=parsed,
                    image=image_file,
                )
            )
    finally:
        connection.close()
    return records


def match_image(recipe_file: RecipeFile, images_by_dir: dict[Path, list[ImageFile]], used_images: set[Path], strategy: str) -> ImageFile | None:
    candidates = [img for img in images_by_dir.get(recipe_file.path.parent, []) if img.path not in used_images]
    if not candidates:
        return None
    recipe_stem = normalize_stem(recipe_file.path.stem)
    exact = [img for img in candidates if normalize_stem(img.path.stem) == recipe_stem]
    if exact:
        return max(exact, key=lambda item: item.size)
    if strategy == "stem":
        return None
    scored = [
        (SequenceMatcher(None, recipe_stem, normalize_stem(img.path.stem)).ratio(), img.size, img)
        for img in candidates
    ]
    scored.sort(key=lambda item: (item[0], item[1]), reverse=True)
    return scored[0][2] if scored and scored[0][0] >= 0.35 else None


def ensure_admin(db: Session, email: str) -> User:
    normalized = email.strip().lower()
    user = db.scalar(select(User).where(User.email == normalized))
    if user:
        if user.role != "admin":
            user.role = "admin"
            db.flush()
        return user
    user = User(email=normalized, hashed_password=hash_password(SETTINGS.seed_admin_password), role="admin")
    db.add(user)
    db.flush()
    return user


def get_or_create_ingredient(db: Session, name: str) -> Ingredient:
    normalized = clean_text(name).casefold()
    ingredient = db.scalar(select(Ingredient).where(Ingredient.name == normalized))
    if ingredient:
        return ingredient
    ingredient = Ingredient(name=normalized)
    db.add(ingredient)
    db.flush()
    return ingredient


def insert_recipe(db: Session, parsed: ParsedRecipe, source_uuid: str, rel_path: str, creator_id: int, publish: bool, image: ImageFile | None, mapping_rules) -> bool:
    suggestion = suggest_canonical_category(raw_category=parsed.category, title=parsed.title, description=parsed.description, mapping_rules=mapping_rules)
    recipe = Recipe(
        title=parsed.title,
        description=parsed.description,
        instructions=parsed.instructions,
        category=parsed.category,
        canonical_category=suggestion.canonical_category,
        prep_time_minutes=30,
        difficulty="easy",
        creator_id=creator_id,
        source="kitchen_folder",
        source_uuid=source_uuid,
        source_url=f"file://{rel_path}",
        is_published=publish,
    )
    db.add(recipe)
    db.flush()
    ingredient_payload: dict[int, dict[str, Any]] = {}
    for item in parsed.ingredients:
        ingredient = get_or_create_ingredient(db, item["name"])
        quantity_text = clean_text(item.get("quantity_text", ""))
        existing = ingredient_payload.get(ingredient.id)
        if existing is None:
            ingredient_payload[ingredient.id] = {
                "quantities": [quantity_text] if quantity_text else [],
                "grams": item.get("grams"),
            }
            continue
        if quantity_text and quantity_text not in existing["quantities"]:
            existing["quantities"].append(quantity_text)
        if existing["grams"] is None and item.get("grams") is not None:
            existing["grams"] = item.get("grams")

    for ingredient_id, payload in ingredient_payload.items():
        quantity_text = " + ".join(payload["quantities"])[:120]
        db.add(
            RecipeIngredient(
                recipe_id=recipe.id,
                ingredient_id=ingredient_id,
                quantity_text=quantity_text,
                grams=payload["grams"],
            )
        )
    if not image:
        return False
    data = image.path.read_bytes()
    content_type = image_content_type(image.path)
    validate_image_upload(content_type, data)
    db.add(RecipeImage(recipe_id=recipe.id, filename=safe_image_filename(image.path.name, content_type), content_type=content_type, data=data, is_primary=True))
    return True


def insert_submission(db: Session, parsed: ParsedRecipe, submitter: User, image: ImageFile | None) -> bool:
    submission = RecipeSubmission(
        submitter_user_id=submitter.id,
        submitter_email=submitter.email,
        title=parsed.title,
        description=parsed.description,
        category=parsed.category,
        difficulty="easy",
        prep_time_minutes=30,
        instructions=parsed.instructions,
        status="pending",
    )
    db.add(submission)
    db.flush()
    for item in parsed.ingredients:
        db.add(SubmissionIngredient(submission_id=submission.id, ingredient_name=clean_text(item["name"])[:200], quantity_text=clean_text(item.get("quantity_text", ""))[:120], grams=item.get("grams"), ingredient_name_normalized=clean_text(item["name"]).casefold()[:200]))
    if not image:
        return False
    data = image.path.read_bytes()
    content_type = image_content_type(image.path)
    validate_image_upload(content_type, data)
    db.add(SubmissionImage(submission_id=submission.id, filename=safe_image_filename(image.path.name, content_type), content_type=content_type, data=data, is_primary=True))
    return True


def run_import(args: argparse.Namespace) -> ImportSummary:
    folder = Path(args.folder).expanduser().resolve()
    if not folder.exists() or not folder.is_dir():
        raise ValueError(f"Folder does not exist or is not a directory: {folder}")
    recipe_files, image_files, unknown_files = scan_files(folder)
    sqlite_source_db = detect_source_sqlite_db(folder) if not recipe_files else None
    sqlite_records = load_sqlite_recipe_records(sqlite_source_db, folder) if sqlite_source_db else []
    if args.limit and args.limit > 0:
        if recipe_files:
            recipe_files = recipe_files[: args.limit]
        else:
            sqlite_records = sqlite_records[: args.limit]

    source_mode = "files" if recipe_files else "sqlite" if sqlite_records else "none"
    scanned_recipes = len(recipe_files) if recipe_files else len(sqlite_records)

    summary = ImportSummary(
        folder=str(folder),
        dry_run=bool(args.dry_run),
        as_submissions=bool(args.as_submissions),
        publish=bool(args.publish),
        creator_email=args.creator_email.strip().lower(),
        limit=args.limit,
        match_strategy=args.match_strategy,
        source_mode=source_mode,
        source_db_path=str(sqlite_source_db) if sqlite_source_db else None,
        scanned_recipes=scanned_recipes,
        scanned_images=len(image_files),
        scanned_unknown=len(unknown_files),
        unknown_files=unknown_files,
    )

    images_by_dir: dict[Path, list[ImageFile]] = {}
    for img in image_files:
        images_by_dir.setdefault(img.path.parent, []).append(img)
    for key in images_by_dir:
        images_by_dir[key].sort(key=lambda item: item.size, reverse=True)

    used_images: set[Path] = set()
    db = SessionLocal()
    mapping_rules = load_category_mapping_rules(db)
    pending_writes = 0

    try:
        creator = ensure_admin(db, summary.creator_email)
        if summary.dry_run:
            db.rollback()

        for recipe_file in recipe_files:
            summary.processed += 1
            try:
                parsed = canonicalize(parse_recipe_file(recipe_file))
                source_uuid = make_source_uuid(recipe_file.relative_path, parsed.title)
                if db.scalar(select(Recipe.id).where(Recipe.source_uuid == source_uuid)):
                    summary.skipped += 1
                    summary.skipped_items.append({"file": recipe_file.relative_path, "reason": "duplicate_source_uuid"})
                    continue
                if summary.as_submissions and db.scalar(select(RecipeSubmission.id).where(RecipeSubmission.title == parsed.title, RecipeSubmission.instructions == parsed.instructions, RecipeSubmission.submitter_user_id == creator.id)):
                    summary.skipped += 1
                    summary.skipped_items.append({"file": recipe_file.relative_path, "reason": "duplicate_submission"})
                    continue

                image = match_image(recipe_file, images_by_dir, used_images, summary.match_strategy)
                if image is None:
                    summary.unmatched_recipe_files.append(recipe_file.relative_path)

                if summary.dry_run:
                    summary.inserted += 1
                    if image:
                        summary.matched_images += 1
                    continue

                with db.begin_nested():
                    attached = insert_submission(db, parsed, creator, image) if summary.as_submissions else insert_recipe(db, parsed, source_uuid, recipe_file.relative_path, creator.id, summary.publish, image, mapping_rules)
                summary.inserted += 1
                if image and attached:
                    used_images.add(image.path)
                    summary.matched_images += 1
                pending_writes += 1
                if pending_writes >= BATCH_SIZE:
                    db.commit()
                    pending_writes = 0
            except Exception as exc:
                summary.skipped += 1
                summary.errors.append({"file": recipe_file.relative_path, "reason": str(exc)})

        for record in sqlite_records:
            summary.processed += 1
            try:
                parsed = canonicalize(record.parsed)
                if db.scalar(select(Recipe.id).where(Recipe.source_uuid == record.source_uuid)):
                    summary.skipped += 1
                    summary.skipped_items.append({"file": record.relative_path, "reason": "duplicate_source_uuid"})
                    continue
                if summary.as_submissions and db.scalar(
                    select(RecipeSubmission.id).where(
                        RecipeSubmission.title == parsed.title,
                        RecipeSubmission.instructions == parsed.instructions,
                        RecipeSubmission.submitter_user_id == creator.id,
                    )
                ):
                    summary.skipped += 1
                    summary.skipped_items.append({"file": record.relative_path, "reason": "duplicate_submission"})
                    continue

                image = record.image
                if image is None:
                    summary.unmatched_recipe_files.append(record.relative_path)

                if summary.dry_run:
                    summary.inserted += 1
                    if image:
                        summary.matched_images += 1
                    continue

                with db.begin_nested():
                    attached = (
                        insert_submission(db, parsed, creator, image)
                        if summary.as_submissions
                        else insert_recipe(
                            db,
                            parsed,
                            record.source_uuid,
                            record.relative_path,
                            creator.id,
                            summary.publish,
                            image,
                            mapping_rules,
                        )
                    )
                summary.inserted += 1
                if image and attached:
                    used_images.add(image.path)
                    summary.matched_images += 1
                pending_writes += 1
                if pending_writes >= BATCH_SIZE:
                    db.commit()
                    pending_writes = 0
            except Exception as exc:
                summary.skipped += 1
                summary.errors.append({"file": record.relative_path, "reason": str(exc)})

        if summary.dry_run:
            db.rollback()
        elif pending_writes > 0:
            db.commit()
    finally:
        db.close()

    return summary


def write_report(path: Path, summary: ImportSummary) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {**asdict(summary), "generated_at": datetime.now(timezone.utc).isoformat()}
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def main() -> int:
    args = parse_args()
    report_path = Path(args.report).expanduser()
    if not report_path.is_absolute():
        report_path = Path.cwd() / report_path
    summary = run_import(args)
    write_report(report_path, summary)
    print("[kitchen-import] finished")
    print(f" folder: {summary.folder}")
    print(f" source_mode: {summary.source_mode}")
    if summary.source_db_path:
        print(f" source_db: {summary.source_db_path}")
    print(f" processed: {summary.processed}")
    print(f" inserted: {summary.inserted}")
    print(f" skipped: {summary.skipped}")
    print(f" errors: {len(summary.errors)}")
    print(f" matched_images: {summary.matched_images}")
    print(f" unknown_files: {summary.scanned_unknown}")
    print(f" report: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
