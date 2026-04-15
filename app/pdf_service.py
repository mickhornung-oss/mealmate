import io
from typing import Iterable

from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from app.models import Recipe, RecipeImage


def _draw_wrapped_text(pdf: canvas.Canvas, text: str, x: int, y: int, max_width: int) -> int:
    words = text.split()
    line = ""
    for word in words:
        trial = f"{line} {word}".strip()
        if pdf.stringWidth(trial, "Helvetica", 10) <= max_width:
            line = trial
            continue
        if line:
            pdf.drawString(x, y, line)
            y -= 13
        line = word
    if line:
        pdf.drawString(x, y, line)
        y -= 13
    return y


def _safe_image_reader(image: RecipeImage) -> ImageReader | None:
    image_bytes = image.data
    if image.content_type == "image/webp":
        try:
            with Image.open(io.BytesIO(image_bytes)) as webp_image:
                rgb = webp_image.convert("RGB")
                png_buffer = io.BytesIO()
                rgb.save(png_buffer, format="PNG")
                image_bytes = png_buffer.getvalue()
        except Exception:
            return None
    try:
        return ImageReader(io.BytesIO(image_bytes))
    except Exception:
        return None


def _pick_primary_image(images: Iterable[RecipeImage]) -> RecipeImage | None:
    image_list = list(images)
    for image in image_list:
        if image.is_primary:
            return image
    return image_list[0] if image_list else None


def build_recipe_pdf(recipe: Recipe, avg_rating: float, review_count: int) -> bytes:
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 50
    primary_image = _pick_primary_image(recipe.images)
    if primary_image:
        image_reader = _safe_image_reader(primary_image)
        if image_reader:
            pdf.drawImage(image_reader, 50, y - 120, width=120, height=90, preserveAspectRatio=True, mask="auto")
            y -= 130
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(50, y, recipe.title)
    y -= 24
    pdf.setFont("Helvetica", 11)
    servings = recipe.servings_text or "-"
    total_time = f"{recipe.total_time_minutes} min" if recipe.total_time_minutes is not None else "-"
    meta = (
        f"Category: {recipe.category} | Difficulty: {recipe.difficulty} | "
        f"Prep: {recipe.prep_time_minutes} min | Total: {total_time} | Servings: {servings}"
    )
    y = _draw_wrapped_text(pdf, meta, 50, y, width - 100)
    y -= 6
    pdf.drawString(50, y, f"Rating: {avg_rating:.2f} ({review_count} reviews)")
    y -= 20
    pdf.setFont("Helvetica-Bold", 13)
    pdf.drawString(50, y, "Ingredients")
    y -= 18
    pdf.setFont("Helvetica", 10)
    for link in recipe.recipe_ingredients:
        qty = link.quantity_text.strip()
        grams = f" ({link.grams} g)" if link.grams is not None else ""
        line = f"- {qty} {link.ingredient.name}{grams}".strip()
        y = _draw_wrapped_text(pdf, line, 50, y, width - 100)
        if y < 90:
            pdf.showPage()
            y = height - 50
            pdf.setFont("Helvetica", 10)
    y -= 8
    pdf.setFont("Helvetica-Bold", 13)
    pdf.drawString(50, y, "Instructions")
    y -= 18
    pdf.setFont("Helvetica", 10)
    paragraphs = [part.strip() for part in recipe.instructions.splitlines() if part.strip()]
    for index, paragraph in enumerate(paragraphs, start=1):
        y = _draw_wrapped_text(pdf, f"{index}. {paragraph}", 50, y, width - 100)
        y -= 2
        if y < 90:
            pdf.showPage()
            y = height - 50
            pdf.setFont("Helvetica", 10)
    pdf.save()
    buffer.seek(0)
    return buffer.getvalue()
