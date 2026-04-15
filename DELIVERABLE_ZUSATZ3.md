# Projektstruktur
```text
.
|-- .env.example
|-- requirements.txt
|-- app/
|   |-- config.py
|   |-- image_utils.py
|   |-- models.py
|   |-- pdf_service.py
|   |-- routers/
|   |   `-- recipes.py
|   `-- templates/
|       |-- recipe_detail.html
|       `-- partials/
|           `-- recipe_images.html
`-- alembic/
    `-- versions/
        `-- 20260303_0004_recipe_images_primary.py
```

## .env.example
```dotenv
APP_NAME=MealMate
APP_URL=http://localhost:8000
SECRET_KEY=change-this-in-production
ALGORITHM=HS256
TOKEN_EXPIRE_MINUTES=60
# DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/mealmate
DATABASE_URL=sqlite:///./mealmate.db
MAX_UPLOAD_MB=4
ALLOWED_IMAGE_TYPES=image/png,image/jpeg,image/webp
AUTO_SEED_KOCHWIKI=0
KOCHWIKI_CSV_PATH=rezepte_kochwiki_clean_3713.csv
IMPORT_DOWNLOAD_IMAGES=0
SEED_ADMIN_EMAIL=admin@mealmate.local
SEED_ADMIN_PASSWORD=AdminPass123!
```
ZEILEN-ERKLAERUNG
1. Diese Zeile setzt einen Teil der Implementierung um.
2. Diese Zeile setzt einen Teil der Implementierung um.
3. Diese Zeile setzt einen Teil der Implementierung um.
4. Diese Zeile setzt einen Teil der Implementierung um.
5. Diese Zeile setzt einen Teil der Implementierung um.
6. Diese Zeile ist ein erlaeuternder Kommentar.
7. Diese Zeile setzt einen Teil der Implementierung um.
8. Diese Zeile setzt einen Teil der Implementierung um.
9. Diese Zeile setzt einen Teil der Implementierung um.
10. Diese Zeile setzt einen Teil der Implementierung um.
11. Diese Zeile setzt einen Teil der Implementierung um.
12. Diese Zeile setzt einen Teil der Implementierung um.
13. Diese Zeile setzt einen Teil der Implementierung um.
14. Diese Zeile setzt einen Teil der Implementierung um.

## requirements.txt
```text
fastapi==0.116.1
uvicorn[standard]==0.35.0
jinja2==3.1.6
sqlalchemy==2.0.43
alembic==1.16.5
python-jose[cryptography]==3.5.0
pwdlib==0.2.1
argon2-cffi==25.1.0
python-multipart==0.0.20
pydantic-settings==2.10.1
reportlab==4.4.4
pillow==11.3.0
psycopg[binary]==3.2.13
```
ZEILEN-ERKLAERUNG
1. Diese Zeile setzt einen Teil der Implementierung um.
2. Diese Zeile setzt einen Teil der Implementierung um.
3. Diese Zeile setzt einen Teil der Implementierung um.
4. Diese Zeile setzt einen Teil der Implementierung um.
5. Diese Zeile setzt einen Teil der Implementierung um.
6. Diese Zeile setzt einen Teil der Implementierung um.
7. Diese Zeile setzt einen Teil der Implementierung um.
8. Diese Zeile setzt einen Teil der Implementierung um.
9. Diese Zeile setzt einen Teil der Implementierung um.
10. Diese Zeile setzt einen Teil der Implementierung um.
11. Diese Zeile setzt einen Teil der Implementierung um.
12. Diese Zeile setzt einen Teil der Implementierung um.
13. Diese Zeile setzt einen Teil der Implementierung um.

## app/config.py
```python
from functools import lru_cache

from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore", case_sensitive=False)

    app_name: str = "MealMate"
    app_url: AnyHttpUrl = "http://localhost:8000"
    secret_key: str = "change-me"
    algorithm: str = "HS256"
    token_expire_minutes: int = 60
    database_url: str = "sqlite:///./mealmate.db"
    max_upload_mb: int = 4
    allowed_image_types: list[str] = ["image/png", "image/jpeg", "image/webp"]
    auto_seed_kochwiki: bool = False
    kochwiki_csv_path: str = "rezepte_kochwiki_clean_3713.csv"
    import_download_images: bool = False
    seed_admin_email: str = "admin@mealmate.local"
    seed_admin_password: str = "AdminPass123!"

    @field_validator("allowed_image_types", mode="before")
    @classmethod
    def parse_allowed_image_types(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, list):
            return value
        return [item.strip() for item in value.split(",") if item.strip()]

    @property
    def is_sqlite(self) -> bool:
        return self.database_url.startswith("sqlite")


@lru_cache
def get_settings() -> Settings:
    return Settings()
```
ZEILEN-ERKLAERUNG
1. Diese Zeile importiert eine benoetigte Abhaengigkeit.
2. Diese Zeile ist absichtlich leer.
3. Diese Zeile importiert eine benoetigte Abhaengigkeit.
4. Diese Zeile importiert eine benoetigte Abhaengigkeit.
5. Diese Zeile ist absichtlich leer.
6. Diese Zeile ist absichtlich leer.
7. Diese Zeile startet eine Klassendefinition.
8. Diese Zeile setzt einen Teil der Implementierung um.
9. Diese Zeile ist absichtlich leer.
10. Diese Zeile setzt einen Teil der Implementierung um.
11. Diese Zeile setzt einen Teil der Implementierung um.
12. Diese Zeile setzt einen Teil der Implementierung um.
13. Diese Zeile setzt einen Teil der Implementierung um.
14. Diese Zeile setzt einen Teil der Implementierung um.
15. Diese Zeile setzt einen Teil der Implementierung um.
16. Diese Zeile setzt einen Teil der Implementierung um.
17. Diese Zeile setzt einen Teil der Implementierung um.
18. Diese Zeile setzt einen Teil der Implementierung um.
19. Diese Zeile setzt einen Teil der Implementierung um.
20. Diese Zeile setzt einen Teil der Implementierung um.
21. Diese Zeile setzt einen Teil der Implementierung um.
22. Diese Zeile setzt einen Teil der Implementierung um.
23. Diese Zeile ist absichtlich leer.
24. Diese Zeile definiert einen Dekorator fuer die naechste Funktion.
25. Diese Zeile definiert einen Dekorator fuer die naechste Funktion.
26. Diese Zeile startet eine Funktionsdefinition.
27. Diese Zeile steuert den bedingten Ablauf.
28. Diese Zeile gibt einen Wert an den Aufrufer zurueck.
29. Diese Zeile gibt einen Wert an den Aufrufer zurueck.
30. Diese Zeile ist absichtlich leer.
31. Diese Zeile definiert einen Dekorator fuer die naechste Funktion.
32. Diese Zeile startet eine Funktionsdefinition.
33. Diese Zeile gibt einen Wert an den Aufrufer zurueck.
34. Diese Zeile ist absichtlich leer.
35. Diese Zeile ist absichtlich leer.
36. Diese Zeile definiert einen Dekorator fuer die naechste Funktion.
37. Diese Zeile startet eine Funktionsdefinition.
38. Diese Zeile gibt einen Wert an den Aufrufer zurueck.

## app/models.py
```python
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, LargeBinary, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), default="user", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    recipes: Mapped[list["Recipe"]] = relationship(back_populates="creator", cascade="all, delete-orphan")
    reviews: Mapped[list["Review"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    favorites: Mapped[list["Favorite"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class Recipe(Base):
    __tablename__ = "recipes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    title_image_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    source: Mapped[str] = mapped_column(String(50), nullable=False, default="user", index=True)
    source_uuid: Mapped[str | None] = mapped_column(String(120), nullable=True, unique=True, index=True)
    source_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    source_image_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    servings_text: Mapped[str | None] = mapped_column(String(120), nullable=True)
    total_time_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    instructions: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    prep_time_minutes: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    difficulty: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    creator_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)

    creator: Mapped["User"] = relationship(back_populates="recipes")
    recipe_ingredients: Mapped[list["RecipeIngredient"]] = relationship(
        back_populates="recipe",
        cascade="all, delete-orphan",
    )
    reviews: Mapped[list["Review"]] = relationship(back_populates="recipe", cascade="all, delete-orphan")
    favorites: Mapped[list["Favorite"]] = relationship(back_populates="recipe", cascade="all, delete-orphan")
    images: Mapped[list["RecipeImage"]] = relationship(
        back_populates="recipe",
        cascade="all, delete-orphan",
        order_by="RecipeImage.created_at",
    )


class Ingredient(Base):
    __tablename__ = "ingredients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), unique=True, nullable=False, index=True)

    recipe_links: Mapped[list["RecipeIngredient"]] = relationship(
        back_populates="ingredient",
        cascade="all, delete-orphan",
    )


class RecipeIngredient(Base):
    __tablename__ = "recipe_ingredients"

    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id", ondelete="CASCADE"), primary_key=True)
    ingredient_id: Mapped[int] = mapped_column(ForeignKey("ingredients.id", ondelete="CASCADE"), primary_key=True)
    quantity_text: Mapped[str] = mapped_column(String(120), default="", nullable=False)
    grams: Mapped[int | None] = mapped_column(Integer, nullable=True)

    recipe: Mapped["Recipe"] = relationship(back_populates="recipe_ingredients")
    ingredient: Mapped["Ingredient"] = relationship(back_populates="recipe_links")


class Review(Base):
    __tablename__ = "reviews"
    __table_args__ = (UniqueConstraint("user_id", "recipe_id", name="uq_reviews_user_recipe"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    comment: Mapped[str] = mapped_column(Text, default="", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    recipe: Mapped["Recipe"] = relationship(back_populates="reviews")
    user: Mapped["User"] = relationship(back_populates="reviews")


class Favorite(Base):
    __tablename__ = "favorites"
    __table_args__ = (UniqueConstraint("user_id", "recipe_id", name="uq_favorites_user_recipe"),)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id", ondelete="CASCADE"), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    user: Mapped["User"] = relationship(back_populates="favorites")
    recipe: Mapped["Recipe"] = relationship(back_populates="favorites")


class RecipeImage(Base):
    __tablename__ = "recipe_images"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False, index=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str] = mapped_column(String(50), nullable=False)
    data: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    recipe: Mapped["Recipe"] = relationship(back_populates="images")


class AppMeta(Base):
    __tablename__ = "app_meta"

    key: Mapped[str] = mapped_column(String(120), primary_key=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)
```
ZEILEN-ERKLAERUNG
1. Diese Zeile importiert eine benoetigte Abhaengigkeit.
2. Diese Zeile ist absichtlich leer.
3. Diese Zeile importiert eine benoetigte Abhaengigkeit.
4. Diese Zeile importiert eine benoetigte Abhaengigkeit.
5. Diese Zeile ist absichtlich leer.
6. Diese Zeile importiert eine benoetigte Abhaengigkeit.
7. Diese Zeile ist absichtlich leer.
8. Diese Zeile ist absichtlich leer.
9. Diese Zeile startet eine Funktionsdefinition.
10. Diese Zeile gibt einen Wert an den Aufrufer zurueck.
11. Diese Zeile ist absichtlich leer.
12. Diese Zeile ist absichtlich leer.
13. Diese Zeile startet eine Klassendefinition.
14. Diese Zeile setzt einen Teil der Implementierung um.
15. Diese Zeile ist absichtlich leer.
16. Diese Zeile setzt einen Teil der Implementierung um.
17. Diese Zeile setzt einen Teil der Implementierung um.
18. Diese Zeile setzt einen Teil der Implementierung um.
19. Diese Zeile setzt einen Teil der Implementierung um.
20. Diese Zeile setzt einen Teil der Implementierung um.
21. Diese Zeile ist absichtlich leer.
22. Diese Zeile setzt einen Teil der Implementierung um.
23. Diese Zeile setzt einen Teil der Implementierung um.
24. Diese Zeile setzt einen Teil der Implementierung um.
25. Diese Zeile ist absichtlich leer.
26. Diese Zeile ist absichtlich leer.
27. Diese Zeile startet eine Klassendefinition.
28. Diese Zeile setzt einen Teil der Implementierung um.
29. Diese Zeile ist absichtlich leer.
30. Diese Zeile setzt einen Teil der Implementierung um.
31. Diese Zeile setzt einen Teil der Implementierung um.
32. Diese Zeile setzt einen Teil der Implementierung um.
33. Diese Zeile setzt einen Teil der Implementierung um.
34. Diese Zeile setzt einen Teil der Implementierung um.
35. Diese Zeile setzt einen Teil der Implementierung um.
36. Diese Zeile setzt einen Teil der Implementierung um.
37. Diese Zeile setzt einen Teil der Implementierung um.
38. Diese Zeile setzt einen Teil der Implementierung um.
39. Diese Zeile setzt einen Teil der Implementierung um.
40. Diese Zeile setzt einen Teil der Implementierung um.
41. Diese Zeile setzt einen Teil der Implementierung um.
42. Diese Zeile setzt einen Teil der Implementierung um.
43. Diese Zeile setzt einen Teil der Implementierung um.
44. Diese Zeile setzt einen Teil der Implementierung um.
45. Diese Zeile setzt einen Teil der Implementierung um.
46. Diese Zeile ist absichtlich leer.
47. Diese Zeile setzt einen Teil der Implementierung um.
48. Diese Zeile setzt einen Teil der Implementierung um.
49. Diese Zeile setzt einen Teil der Implementierung um.
50. Diese Zeile setzt einen Teil der Implementierung um.
51. Diese Zeile setzt einen Teil der Implementierung um.
52. Diese Zeile setzt einen Teil der Implementierung um.
53. Diese Zeile setzt einen Teil der Implementierung um.
54. Diese Zeile setzt einen Teil der Implementierung um.
55. Diese Zeile setzt einen Teil der Implementierung um.
56. Diese Zeile setzt einen Teil der Implementierung um.
57. Diese Zeile setzt einen Teil der Implementierung um.
58. Diese Zeile setzt einen Teil der Implementierung um.
59. Diese Zeile ist absichtlich leer.
60. Diese Zeile ist absichtlich leer.
61. Diese Zeile startet eine Klassendefinition.
62. Diese Zeile setzt einen Teil der Implementierung um.
63. Diese Zeile ist absichtlich leer.
64. Diese Zeile setzt einen Teil der Implementierung um.
65. Diese Zeile setzt einen Teil der Implementierung um.
66. Diese Zeile ist absichtlich leer.
67. Diese Zeile setzt einen Teil der Implementierung um.
68. Diese Zeile setzt einen Teil der Implementierung um.
69. Diese Zeile setzt einen Teil der Implementierung um.
70. Diese Zeile setzt einen Teil der Implementierung um.
71. Diese Zeile ist absichtlich leer.
72. Diese Zeile ist absichtlich leer.
73. Diese Zeile startet eine Klassendefinition.
74. Diese Zeile setzt einen Teil der Implementierung um.
75. Diese Zeile ist absichtlich leer.
76. Diese Zeile setzt einen Teil der Implementierung um.
77. Diese Zeile setzt einen Teil der Implementierung um.
78. Diese Zeile setzt einen Teil der Implementierung um.
79. Diese Zeile setzt einen Teil der Implementierung um.
80. Diese Zeile ist absichtlich leer.
81. Diese Zeile setzt einen Teil der Implementierung um.
82. Diese Zeile setzt einen Teil der Implementierung um.
83. Diese Zeile ist absichtlich leer.
84. Diese Zeile ist absichtlich leer.
85. Diese Zeile startet eine Klassendefinition.
86. Diese Zeile setzt einen Teil der Implementierung um.
87. Diese Zeile setzt einen Teil der Implementierung um.
88. Diese Zeile ist absichtlich leer.
89. Diese Zeile setzt einen Teil der Implementierung um.
90. Diese Zeile setzt einen Teil der Implementierung um.
91. Diese Zeile setzt einen Teil der Implementierung um.
92. Diese Zeile setzt einen Teil der Implementierung um.
93. Diese Zeile setzt einen Teil der Implementierung um.
94. Diese Zeile setzt einen Teil der Implementierung um.
95. Diese Zeile ist absichtlich leer.
96. Diese Zeile setzt einen Teil der Implementierung um.
97. Diese Zeile setzt einen Teil der Implementierung um.
98. Diese Zeile ist absichtlich leer.
99. Diese Zeile ist absichtlich leer.
100. Diese Zeile startet eine Klassendefinition.
101. Diese Zeile setzt einen Teil der Implementierung um.
102. Diese Zeile setzt einen Teil der Implementierung um.
103. Diese Zeile ist absichtlich leer.
104. Diese Zeile setzt einen Teil der Implementierung um.
105. Diese Zeile setzt einen Teil der Implementierung um.
106. Diese Zeile setzt einen Teil der Implementierung um.
107. Diese Zeile ist absichtlich leer.
108. Diese Zeile setzt einen Teil der Implementierung um.
109. Diese Zeile setzt einen Teil der Implementierung um.
110. Diese Zeile ist absichtlich leer.
111. Diese Zeile ist absichtlich leer.
112. Diese Zeile startet eine Klassendefinition.
113. Diese Zeile setzt einen Teil der Implementierung um.
114. Diese Zeile ist absichtlich leer.
115. Diese Zeile setzt einen Teil der Implementierung um.
116. Diese Zeile setzt einen Teil der Implementierung um.
117. Diese Zeile setzt einen Teil der Implementierung um.
118. Diese Zeile setzt einen Teil der Implementierung um.
119. Diese Zeile setzt einen Teil der Implementierung um.
120. Diese Zeile setzt einen Teil der Implementierung um.
121. Diese Zeile setzt einen Teil der Implementierung um.
122. Diese Zeile ist absichtlich leer.
123. Diese Zeile setzt einen Teil der Implementierung um.
124. Diese Zeile ist absichtlich leer.
125. Diese Zeile ist absichtlich leer.
126. Diese Zeile startet eine Klassendefinition.
127. Diese Zeile setzt einen Teil der Implementierung um.
128. Diese Zeile ist absichtlich leer.
129. Diese Zeile setzt einen Teil der Implementierung um.
130. Diese Zeile setzt einen Teil der Implementierung um.

## app/image_utils.py
```python
from app.config import get_settings

settings = get_settings()

MAGIC_SIGNATURES = {
    "image/jpeg": [b"\xff\xd8\xff"],
    "image/png": [b"\x89PNG\r\n\x1a\n"],
    "image/webp": [b"RIFF"],
}


def _validate_magic_bytes(content_type: str, file_bytes: bytes) -> None:
    signatures = MAGIC_SIGNATURES.get(content_type, [])
    if not signatures:
        raise ValueError("Unsupported MIME type.")
    if content_type == "image/webp":
        if not (file_bytes.startswith(b"RIFF") and file_bytes[8:12] == b"WEBP"):
            raise ValueError("Invalid WEBP file signature.")
        return
    if not any(file_bytes.startswith(sig) for sig in signatures):
        raise ValueError("File signature does not match content type.")


def validate_image_upload(content_type: str, file_bytes: bytes) -> None:
    if content_type not in settings.allowed_image_types:
        raise ValueError(f"Unsupported MIME type '{content_type}'.")
    max_bytes = settings.max_upload_mb * 1024 * 1024
    if len(file_bytes) > max_bytes:
        raise ValueError(f"Image too large. Max size is {settings.max_upload_mb} MB.")
    if len(file_bytes) < 12:
        raise ValueError("Uploaded file is too small to be a valid image.")
    _validate_magic_bytes(content_type, file_bytes)
```
ZEILEN-ERKLAERUNG
1. Diese Zeile importiert eine benoetigte Abhaengigkeit.
2. Diese Zeile ist absichtlich leer.
3. Diese Zeile setzt einen Teil der Implementierung um.
4. Diese Zeile ist absichtlich leer.
5. Diese Zeile setzt einen Teil der Implementierung um.
6. Diese Zeile setzt einen Teil der Implementierung um.
7. Diese Zeile setzt einen Teil der Implementierung um.
8. Diese Zeile setzt einen Teil der Implementierung um.
9. Diese Zeile setzt einen Teil der Implementierung um.
10. Diese Zeile ist absichtlich leer.
11. Diese Zeile ist absichtlich leer.
12. Diese Zeile startet eine Funktionsdefinition.
13. Diese Zeile setzt einen Teil der Implementierung um.
14. Diese Zeile steuert den bedingten Ablauf.
15. Diese Zeile setzt einen Teil der Implementierung um.
16. Diese Zeile steuert den bedingten Ablauf.
17. Diese Zeile steuert den bedingten Ablauf.
18. Diese Zeile setzt einen Teil der Implementierung um.
19. Diese Zeile setzt einen Teil der Implementierung um.
20. Diese Zeile steuert den bedingten Ablauf.
21. Diese Zeile setzt einen Teil der Implementierung um.
22. Diese Zeile ist absichtlich leer.
23. Diese Zeile ist absichtlich leer.
24. Diese Zeile startet eine Funktionsdefinition.
25. Diese Zeile steuert den bedingten Ablauf.
26. Diese Zeile setzt einen Teil der Implementierung um.
27. Diese Zeile setzt einen Teil der Implementierung um.
28. Diese Zeile steuert den bedingten Ablauf.
29. Diese Zeile setzt einen Teil der Implementierung um.
30. Diese Zeile steuert den bedingten Ablauf.
31. Diese Zeile setzt einen Teil der Implementierung um.
32. Diese Zeile setzt einen Teil der Implementierung um.

## app/pdf_service.py
```python
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
```
ZEILEN-ERKLAERUNG
1. Diese Zeile importiert eine benoetigte Abhaengigkeit.
2. Diese Zeile importiert eine benoetigte Abhaengigkeit.
3. Diese Zeile ist absichtlich leer.
4. Diese Zeile importiert eine benoetigte Abhaengigkeit.
5. Diese Zeile importiert eine benoetigte Abhaengigkeit.
6. Diese Zeile importiert eine benoetigte Abhaengigkeit.
7. Diese Zeile importiert eine benoetigte Abhaengigkeit.
8. Diese Zeile ist absichtlich leer.
9. Diese Zeile importiert eine benoetigte Abhaengigkeit.
10. Diese Zeile ist absichtlich leer.
11. Diese Zeile ist absichtlich leer.
12. Diese Zeile startet eine Funktionsdefinition.
13. Diese Zeile setzt einen Teil der Implementierung um.
14. Diese Zeile setzt einen Teil der Implementierung um.
15. Diese Zeile startet eine Schleife.
16. Diese Zeile setzt einen Teil der Implementierung um.
17. Diese Zeile steuert den bedingten Ablauf.
18. Diese Zeile setzt einen Teil der Implementierung um.
19. Diese Zeile setzt einen Teil der Implementierung um.
20. Diese Zeile steuert den bedingten Ablauf.
21. Diese Zeile setzt einen Teil der Implementierung um.
22. Diese Zeile setzt einen Teil der Implementierung um.
23. Diese Zeile setzt einen Teil der Implementierung um.
24. Diese Zeile steuert den bedingten Ablauf.
25. Diese Zeile setzt einen Teil der Implementierung um.
26. Diese Zeile setzt einen Teil der Implementierung um.
27. Diese Zeile gibt einen Wert an den Aufrufer zurueck.
28. Diese Zeile ist absichtlich leer.
29. Diese Zeile ist absichtlich leer.
30. Diese Zeile startet eine Funktionsdefinition.
31. Diese Zeile setzt einen Teil der Implementierung um.
32. Diese Zeile steuert den bedingten Ablauf.
33. Diese Zeile gehoert zur Fehlerbehandlung.
34. Diese Zeile setzt einen Teil der Implementierung um.
35. Diese Zeile setzt einen Teil der Implementierung um.
36. Diese Zeile setzt einen Teil der Implementierung um.
37. Diese Zeile setzt einen Teil der Implementierung um.
38. Diese Zeile setzt einen Teil der Implementierung um.
39. Diese Zeile gehoert zur Fehlerbehandlung.
40. Diese Zeile gibt einen Wert an den Aufrufer zurueck.
41. Diese Zeile gehoert zur Fehlerbehandlung.
42. Diese Zeile gibt einen Wert an den Aufrufer zurueck.
43. Diese Zeile gehoert zur Fehlerbehandlung.
44. Diese Zeile gibt einen Wert an den Aufrufer zurueck.
45. Diese Zeile ist absichtlich leer.
46. Diese Zeile ist absichtlich leer.
47. Diese Zeile startet eine Funktionsdefinition.
48. Diese Zeile setzt einen Teil der Implementierung um.
49. Diese Zeile startet eine Schleife.
50. Diese Zeile steuert den bedingten Ablauf.
51. Diese Zeile gibt einen Wert an den Aufrufer zurueck.
52. Diese Zeile gibt einen Wert an den Aufrufer zurueck.
53. Diese Zeile ist absichtlich leer.
54. Diese Zeile ist absichtlich leer.
55. Diese Zeile startet eine Funktionsdefinition.
56. Diese Zeile setzt einen Teil der Implementierung um.
57. Diese Zeile setzt einen Teil der Implementierung um.
58. Diese Zeile setzt einen Teil der Implementierung um.
59. Diese Zeile setzt einen Teil der Implementierung um.
60. Diese Zeile setzt einen Teil der Implementierung um.
61. Diese Zeile steuert den bedingten Ablauf.
62. Diese Zeile setzt einen Teil der Implementierung um.
63. Diese Zeile steuert den bedingten Ablauf.
64. Diese Zeile setzt einen Teil der Implementierung um.
65. Diese Zeile setzt einen Teil der Implementierung um.
66. Diese Zeile setzt einen Teil der Implementierung um.
67. Diese Zeile setzt einen Teil der Implementierung um.
68. Diese Zeile setzt einen Teil der Implementierung um.
69. Diese Zeile setzt einen Teil der Implementierung um.
70. Diese Zeile setzt einen Teil der Implementierung um.
71. Diese Zeile setzt einen Teil der Implementierung um.
72. Diese Zeile setzt einen Teil der Implementierung um.
73. Diese Zeile setzt einen Teil der Implementierung um.
74. Diese Zeile setzt einen Teil der Implementierung um.
75. Diese Zeile setzt einen Teil der Implementierung um.
76. Diese Zeile setzt einen Teil der Implementierung um.
77. Diese Zeile setzt einen Teil der Implementierung um.
78. Diese Zeile setzt einen Teil der Implementierung um.
79. Diese Zeile setzt einen Teil der Implementierung um.
80. Diese Zeile setzt einen Teil der Implementierung um.
81. Diese Zeile setzt einen Teil der Implementierung um.
82. Diese Zeile setzt einen Teil der Implementierung um.
83. Diese Zeile setzt einen Teil der Implementierung um.
84. Diese Zeile startet eine Schleife.
85. Diese Zeile setzt einen Teil der Implementierung um.
86. Diese Zeile setzt einen Teil der Implementierung um.
87. Diese Zeile setzt einen Teil der Implementierung um.
88. Diese Zeile setzt einen Teil der Implementierung um.
89. Diese Zeile steuert den bedingten Ablauf.
90. Diese Zeile setzt einen Teil der Implementierung um.
91. Diese Zeile setzt einen Teil der Implementierung um.
92. Diese Zeile setzt einen Teil der Implementierung um.
93. Diese Zeile setzt einen Teil der Implementierung um.
94. Diese Zeile setzt einen Teil der Implementierung um.
95. Diese Zeile setzt einen Teil der Implementierung um.
96. Diese Zeile setzt einen Teil der Implementierung um.
97. Diese Zeile setzt einen Teil der Implementierung um.
98. Diese Zeile setzt einen Teil der Implementierung um.
99. Diese Zeile startet eine Schleife.
100. Diese Zeile setzt einen Teil der Implementierung um.
101. Diese Zeile setzt einen Teil der Implementierung um.
102. Diese Zeile steuert den bedingten Ablauf.
103. Diese Zeile setzt einen Teil der Implementierung um.
104. Diese Zeile setzt einen Teil der Implementierung um.
105. Diese Zeile setzt einen Teil der Implementierung um.
106. Diese Zeile setzt einen Teil der Implementierung um.
107. Diese Zeile setzt einen Teil der Implementierung um.
108. Diese Zeile gibt einen Wert an den Aufrufer zurueck.

## app/routers/recipes.py
```python
from io import BytesIO

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status
from fastapi.responses import RedirectResponse, Response, StreamingResponse
from sqlalchemy import and_, desc, func, select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.database import get_db
from app.dependencies import get_current_user, get_current_user_optional, template_context
from app.image_utils import validate_image_upload
from app.models import Favorite, Ingredient, Recipe, RecipeImage, RecipeIngredient, Review, User
from app.pdf_service import build_recipe_pdf
from app.services import (
    can_manage_recipe,
    parse_ingredient_text,
    replace_recipe_ingredients,
    resolve_title_image_url,
    sanitize_difficulty,
)
from app.views import redirect, templates

router = APIRouter(tags=["recipes"])

PAGE_SIZE = 8


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
    sort: str = "date",
    title: str = "",
    category: str = "",
    difficulty: str = "",
    ingredient: str = "",
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    page = max(page, 1)
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
    if category.strip():
        stmt = stmt.where(Recipe.category.ilike(category.strip()))
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
    rows = db.execute(stmt.offset((page - 1) * PAGE_SIZE).limit(PAGE_SIZE)).all()
    recipes_data = [{"recipe": row[0], "avg_rating": float(row[1] or 0), "review_count": int(row[2] or 0)} for row in rows]
    pages = max((total + PAGE_SIZE - 1) // PAGE_SIZE, 1)
    context = template_context(
        request,
        current_user,
        recipes_data=recipes_data,
        page=page,
        pages=pages,
        sort=sort,
        title=title,
        category=category,
        difficulty=difficulty,
        ingredient=ingredient,
    )
    if request.headers.get("HX-Request") == "true":
        return templates.TemplateResponse("partials/recipe_list.html", context)
    return templates.TemplateResponse("home.html", context)


@router.get("/recipes/new")
def create_recipe_page(request: Request, current_user: User = Depends(get_current_user)):
    return templates.TemplateResponse(
        "recipe_form.html",
        template_context(request, current_user, recipe=None, error=None, form_mode="create"),
    )


@router.post("/recipes/new")
async def create_recipe_submit(
    request: Request,
    title: str = Form(...),
    description: str = Form(...),
    instructions: str = Form(...),
    category: str = Form(...),
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
        category=category.strip() or "General",
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
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
        db.add(
            RecipeImage(
                recipe_id=recipe.id,
                filename=image.filename,
                content_type=(image.content_type or "application/octet-stream").lower(),
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
        ),
    )


@router.post("/recipes/{recipe_id}/edit")
async def edit_recipe_submit(
    recipe_id: int,
    title: str = Form(...),
    description: str = Form(...),
    instructions: str = Form(...),
    category: str = Form(...),
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
    recipe.category = category.strip() or "General"
    recipe.prep_time_minutes = parse_positive_int(prep_time_minutes, "prep_time_minutes")
    recipe.difficulty = sanitize_difficulty(difficulty)
    replace_recipe_ingredients(db, recipe, parse_ingredient_text(ingredients_text))
    if image and image.filename:
        data = await image.read()
        try:
            validate_image_upload((image.content_type or "").lower(), data)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
        has_images = db.scalar(select(func.count()).select_from(RecipeImage).where(RecipeImage.recipe_id == recipe.id)) or 0
        db.add(
            RecipeImage(
                recipe_id=recipe.id,
                filename=image.filename,
                content_type=(image.content_type or "application/octet-stream").lower(),
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
async def upload_recipe_image(
    request: Request,
    recipe_id: int,
    set_primary: bool = Form(False),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    recipe = fetch_recipe_or_404(db, recipe_id)
    ensure_recipe_access(current_user, recipe)
    data = await file.read()
    content_type = (file.content_type or "").lower()
    try:
        validate_image_upload(content_type, data)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    has_images = db.scalar(select(func.count()).select_from(RecipeImage).where(RecipeImage.recipe_id == recipe_id)) or 0
    query_value = request.query_params.get("set_primary")
    if query_value is not None:
        set_primary = query_value.strip().lower() in {"1", "true", "yes", "on"}
    new_is_primary = set_primary or has_images == 0
    recipe_image = RecipeImage(
        recipe_id=recipe_id,
        filename=file.filename or "upload",
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
```
ZEILEN-ERKLAERUNG
1. Diese Zeile importiert eine benoetigte Abhaengigkeit.
2. Diese Zeile ist absichtlich leer.
3. Diese Zeile importiert eine benoetigte Abhaengigkeit.
4. Diese Zeile importiert eine benoetigte Abhaengigkeit.
5. Diese Zeile importiert eine benoetigte Abhaengigkeit.
6. Diese Zeile importiert eine benoetigte Abhaengigkeit.
7. Diese Zeile ist absichtlich leer.
8. Diese Zeile importiert eine benoetigte Abhaengigkeit.
9. Diese Zeile importiert eine benoetigte Abhaengigkeit.
10. Diese Zeile importiert eine benoetigte Abhaengigkeit.
11. Diese Zeile importiert eine benoetigte Abhaengigkeit.
12. Diese Zeile importiert eine benoetigte Abhaengigkeit.
13. Diese Zeile importiert eine benoetigte Abhaengigkeit.
14. Diese Zeile setzt einen Teil der Implementierung um.
15. Diese Zeile setzt einen Teil der Implementierung um.
16. Diese Zeile setzt einen Teil der Implementierung um.
17. Diese Zeile setzt einen Teil der Implementierung um.
18. Diese Zeile setzt einen Teil der Implementierung um.
19. Diese Zeile setzt einen Teil der Implementierung um.
20. Diese Zeile importiert eine benoetigte Abhaengigkeit.
21. Diese Zeile ist absichtlich leer.
22. Diese Zeile setzt einen Teil der Implementierung um.
23. Diese Zeile ist absichtlich leer.
24. Diese Zeile setzt einen Teil der Implementierung um.
25. Diese Zeile ist absichtlich leer.
26. Diese Zeile ist absichtlich leer.
27. Diese Zeile startet eine Funktionsdefinition.
28. Diese Zeile gehoert zur Fehlerbehandlung.
29. Diese Zeile setzt einen Teil der Implementierung um.
30. Diese Zeile gehoert zur Fehlerbehandlung.
31. Diese Zeile setzt einen Teil der Implementierung um.
32. Diese Zeile steuert den bedingten Ablauf.
33. Diese Zeile setzt einen Teil der Implementierung um.
34. Diese Zeile gibt einen Wert an den Aufrufer zurueck.
35. Diese Zeile ist absichtlich leer.
36. Diese Zeile ist absichtlich leer.
37. Diese Zeile startet eine Funktionsdefinition.
38. Diese Zeile setzt einen Teil der Implementierung um.
39. Diese Zeile steuert den bedingten Ablauf.
40. Diese Zeile gibt einen Wert an den Aufrufer zurueck.
41. Diese Zeile steuert den bedingten Ablauf.
42. Diese Zeile setzt einen Teil der Implementierung um.
43. Diese Zeile gibt einen Wert an den Aufrufer zurueck.
44. Diese Zeile ist absichtlich leer.
45. Diese Zeile ist absichtlich leer.
46. Diese Zeile startet eine Funktionsdefinition.
47. Diese Zeile setzt einen Teil der Implementierung um.
48. Diese Zeile setzt einen Teil der Implementierung um.
49. Diese Zeile setzt einen Teil der Implementierung um.
50. Diese Zeile setzt einen Teil der Implementierung um.
51. Diese Zeile setzt einen Teil der Implementierung um.
52. Diese Zeile setzt einen Teil der Implementierung um.
53. Diese Zeile setzt einen Teil der Implementierung um.
54. Diese Zeile setzt einen Teil der Implementierung um.
55. Diese Zeile setzt einen Teil der Implementierung um.
56. Diese Zeile setzt einen Teil der Implementierung um.
57. Diese Zeile steuert den bedingten Ablauf.
58. Diese Zeile setzt einen Teil der Implementierung um.
59. Diese Zeile gibt einen Wert an den Aufrufer zurueck.
60. Diese Zeile ist absichtlich leer.
61. Diese Zeile ist absichtlich leer.
62. Diese Zeile startet eine Funktionsdefinition.
63. Diese Zeile steuert den bedingten Ablauf.
64. Diese Zeile setzt einen Teil der Implementierung um.
65. Diese Zeile ist absichtlich leer.
66. Diese Zeile ist absichtlich leer.
67. Diese Zeile startet eine Funktionsdefinition.
68. Diese Zeile startet eine Schleife.
69. Diese Zeile steuert den bedingten Ablauf.
70. Diese Zeile gibt einen Wert an den Aufrufer zurueck.
71. Diese Zeile gibt einen Wert an den Aufrufer zurueck.
72. Diese Zeile ist absichtlich leer.
73. Diese Zeile ist absichtlich leer.
74. Diese Zeile startet eine Funktionsdefinition.
75. Diese Zeile startet eine Schleife.
76. Diese Zeile setzt einen Teil der Implementierung um.
77. Diese Zeile setzt einen Teil der Implementierung um.
78. Diese Zeile ist absichtlich leer.
79. Diese Zeile ist absichtlich leer.
80. Diese Zeile startet eine Funktionsdefinition.
81. Diese Zeile setzt einen Teil der Implementierung um.
82. Diese Zeile steuert den bedingten Ablauf.
83. Diese Zeile setzt einen Teil der Implementierung um.
84. Diese Zeile steuert den bedingten Ablauf.
85. Diese Zeile setzt einen Teil der Implementierung um.
86. Diese Zeile setzt einen Teil der Implementierung um.
87. Diese Zeile setzt einen Teil der Implementierung um.
88. Diese Zeile ist absichtlich leer.
89. Diese Zeile ist absichtlich leer.
90. Diese Zeile startet eine Funktionsdefinition.
91. Diese Zeile setzt einen Teil der Implementierung um.
92. Diese Zeile setzt einen Teil der Implementierung um.
93. Diese Zeile gibt einen Wert an den Aufrufer zurueck.
94. Diese Zeile setzt einen Teil der Implementierung um.
95. Diese Zeile setzt einen Teil der Implementierung um.
96. Diese Zeile setzt einen Teil der Implementierung um.
97. Diese Zeile setzt einen Teil der Implementierung um.
98. Diese Zeile setzt einen Teil der Implementierung um.
99. Diese Zeile setzt einen Teil der Implementierung um.
100. Diese Zeile setzt einen Teil der Implementierung um.
101. Diese Zeile setzt einen Teil der Implementierung um.
102. Diese Zeile ist absichtlich leer.
103. Diese Zeile ist absichtlich leer.
104. Diese Zeile definiert einen Dekorator fuer die naechste Funktion.
105. Diese Zeile startet eine Funktionsdefinition.
106. Diese Zeile setzt einen Teil der Implementierung um.
107. Diese Zeile setzt einen Teil der Implementierung um.
108. Diese Zeile setzt einen Teil der Implementierung um.
109. Diese Zeile setzt einen Teil der Implementierung um.
110. Diese Zeile setzt einen Teil der Implementierung um.
111. Diese Zeile setzt einen Teil der Implementierung um.
112. Diese Zeile setzt einen Teil der Implementierung um.
113. Diese Zeile setzt einen Teil der Implementierung um.
114. Diese Zeile setzt einen Teil der Implementierung um.
115. Diese Zeile setzt einen Teil der Implementierung um.
116. Diese Zeile setzt einen Teil der Implementierung um.
117. Diese Zeile setzt einen Teil der Implementierung um.
118. Diese Zeile setzt einen Teil der Implementierung um.
119. Diese Zeile setzt einen Teil der Implementierung um.
120. Diese Zeile setzt einen Teil der Implementierung um.
121. Diese Zeile setzt einen Teil der Implementierung um.
122. Diese Zeile setzt einen Teil der Implementierung um.
123. Diese Zeile setzt einen Teil der Implementierung um.
124. Diese Zeile setzt einen Teil der Implementierung um.
125. Diese Zeile setzt einen Teil der Implementierung um.
126. Diese Zeile setzt einen Teil der Implementierung um.
127. Diese Zeile setzt einen Teil der Implementierung um.
128. Diese Zeile setzt einen Teil der Implementierung um.
129. Diese Zeile setzt einen Teil der Implementierung um.
130. Diese Zeile setzt einen Teil der Implementierung um.
131. Diese Zeile setzt einen Teil der Implementierung um.
132. Diese Zeile setzt einen Teil der Implementierung um.
133. Diese Zeile setzt einen Teil der Implementierung um.
134. Diese Zeile setzt einen Teil der Implementierung um.
135. Diese Zeile steuert den bedingten Ablauf.
136. Diese Zeile setzt einen Teil der Implementierung um.
137. Diese Zeile setzt einen Teil der Implementierung um.
138. Diese Zeile steuert den bedingten Ablauf.
139. Diese Zeile setzt einen Teil der Implementierung um.
140. Diese Zeile steuert den bedingten Ablauf.
141. Diese Zeile setzt einen Teil der Implementierung um.
142. Diese Zeile steuert den bedingten Ablauf.
143. Diese Zeile setzt einen Teil der Implementierung um.
144. Diese Zeile setzt einen Teil der Implementierung um.
145. Diese Zeile setzt einen Teil der Implementierung um.
146. Diese Zeile setzt einen Teil der Implementierung um.
147. Diese Zeile setzt einen Teil der Implementierung um.
148. Diese Zeile setzt einen Teil der Implementierung um.
149. Diese Zeile setzt einen Teil der Implementierung um.
150. Diese Zeile setzt einen Teil der Implementierung um.
151. Diese Zeile steuert den bedingten Ablauf.
152. Diese Zeile setzt einen Teil der Implementierung um.
153. Diese Zeile steuert den bedingten Ablauf.
154. Diese Zeile setzt einen Teil der Implementierung um.
155. Diese Zeile steuert den bedingten Ablauf.
156. Diese Zeile setzt einen Teil der Implementierung um.
157. Diese Zeile setzt einen Teil der Implementierung um.
158. Diese Zeile setzt einen Teil der Implementierung um.
159. Diese Zeile setzt einen Teil der Implementierung um.
160. Diese Zeile setzt einen Teil der Implementierung um.
161. Diese Zeile setzt einen Teil der Implementierung um.
162. Diese Zeile setzt einen Teil der Implementierung um.
163. Diese Zeile setzt einen Teil der Implementierung um.
164. Diese Zeile setzt einen Teil der Implementierung um.
165. Diese Zeile setzt einen Teil der Implementierung um.
166. Diese Zeile setzt einen Teil der Implementierung um.
167. Diese Zeile setzt einen Teil der Implementierung um.
168. Diese Zeile setzt einen Teil der Implementierung um.
169. Diese Zeile setzt einen Teil der Implementierung um.
170. Diese Zeile setzt einen Teil der Implementierung um.
171. Diese Zeile setzt einen Teil der Implementierung um.
172. Diese Zeile setzt einen Teil der Implementierung um.
173. Diese Zeile steuert den bedingten Ablauf.
174. Diese Zeile gibt einen Wert an den Aufrufer zurueck.
175. Diese Zeile gibt einen Wert an den Aufrufer zurueck.
176. Diese Zeile ist absichtlich leer.
177. Diese Zeile ist absichtlich leer.
178. Diese Zeile definiert einen Dekorator fuer die naechste Funktion.
179. Diese Zeile startet eine Funktionsdefinition.
180. Diese Zeile gibt einen Wert an den Aufrufer zurueck.
181. Diese Zeile setzt einen Teil der Implementierung um.
182. Diese Zeile setzt einen Teil der Implementierung um.
183. Diese Zeile setzt einen Teil der Implementierung um.
184. Diese Zeile ist absichtlich leer.
185. Diese Zeile ist absichtlich leer.
186. Diese Zeile definiert einen Dekorator fuer die naechste Funktion.
187. Diese Zeile startet eine Funktionsdefinition.
188. Diese Zeile setzt einen Teil der Implementierung um.
189. Diese Zeile setzt einen Teil der Implementierung um.
190. Diese Zeile setzt einen Teil der Implementierung um.
191. Diese Zeile setzt einen Teil der Implementierung um.
192. Diese Zeile setzt einen Teil der Implementierung um.
193. Diese Zeile setzt einen Teil der Implementierung um.
194. Diese Zeile setzt einen Teil der Implementierung um.
195. Diese Zeile setzt einen Teil der Implementierung um.
196. Diese Zeile setzt einen Teil der Implementierung um.
197. Diese Zeile setzt einen Teil der Implementierung um.
198. Diese Zeile setzt einen Teil der Implementierung um.
199. Diese Zeile setzt einen Teil der Implementierung um.
200. Diese Zeile setzt einen Teil der Implementierung um.
201. Diese Zeile setzt einen Teil der Implementierung um.
202. Diese Zeile setzt einen Teil der Implementierung um.
203. Diese Zeile steuert den bedingten Ablauf.
204. Diese Zeile setzt einen Teil der Implementierung um.
205. Diese Zeile setzt einen Teil der Implementierung um.
206. Diese Zeile setzt einen Teil der Implementierung um.
207. Diese Zeile setzt einen Teil der Implementierung um.
208. Diese Zeile setzt einen Teil der Implementierung um.
209. Diese Zeile setzt einen Teil der Implementierung um.
210. Diese Zeile setzt einen Teil der Implementierung um.
211. Diese Zeile setzt einen Teil der Implementierung um.
212. Diese Zeile setzt einen Teil der Implementierung um.
213. Diese Zeile setzt einen Teil der Implementierung um.
214. Diese Zeile setzt einen Teil der Implementierung um.
215. Diese Zeile setzt einen Teil der Implementierung um.
216. Diese Zeile setzt einen Teil der Implementierung um.
217. Diese Zeile setzt einen Teil der Implementierung um.
218. Diese Zeile setzt einen Teil der Implementierung um.
219. Diese Zeile steuert den bedingten Ablauf.
220. Diese Zeile setzt einen Teil der Implementierung um.
221. Diese Zeile gehoert zur Fehlerbehandlung.
222. Diese Zeile setzt einen Teil der Implementierung um.
223. Diese Zeile gehoert zur Fehlerbehandlung.
224. Diese Zeile setzt einen Teil der Implementierung um.
225. Diese Zeile setzt einen Teil der Implementierung um.
226. Diese Zeile setzt einen Teil der Implementierung um.
227. Diese Zeile setzt einen Teil der Implementierung um.
228. Diese Zeile setzt einen Teil der Implementierung um.
229. Diese Zeile setzt einen Teil der Implementierung um.
230. Diese Zeile setzt einen Teil der Implementierung um.
231. Diese Zeile setzt einen Teil der Implementierung um.
232. Diese Zeile setzt einen Teil der Implementierung um.
233. Diese Zeile setzt einen Teil der Implementierung um.
234. Diese Zeile setzt einen Teil der Implementierung um.
235. Diese Zeile gibt einen Wert an den Aufrufer zurueck.
236. Diese Zeile ist absichtlich leer.
237. Diese Zeile ist absichtlich leer.
238. Diese Zeile definiert einen Dekorator fuer die naechste Funktion.
239. Diese Zeile startet eine Funktionsdefinition.
240. Diese Zeile setzt einen Teil der Implementierung um.
241. Diese Zeile setzt einen Teil der Implementierung um.
242. Diese Zeile setzt einen Teil der Implementierung um.
243. Diese Zeile setzt einen Teil der Implementierung um.
244. Diese Zeile setzt einen Teil der Implementierung um.
245. Diese Zeile setzt einen Teil der Implementierung um.
246. Diese Zeile setzt einen Teil der Implementierung um.
247. Diese Zeile setzt einen Teil der Implementierung um.
248. Diese Zeile setzt einen Teil der Implementierung um.
249. Diese Zeile setzt einen Teil der Implementierung um.
250. Diese Zeile steuert den bedingten Ablauf.
251. Diese Zeile setzt einen Teil der Implementierung um.
252. Diese Zeile setzt einen Teil der Implementierung um.
253. Diese Zeile setzt einen Teil der Implementierung um.
254. Diese Zeile gibt einen Wert an den Aufrufer zurueck.
255. Diese Zeile setzt einen Teil der Implementierung um.
256. Diese Zeile setzt einen Teil der Implementierung um.
257. Diese Zeile setzt einen Teil der Implementierung um.
258. Diese Zeile setzt einen Teil der Implementierung um.
259. Diese Zeile setzt einen Teil der Implementierung um.
260. Diese Zeile setzt einen Teil der Implementierung um.
261. Diese Zeile setzt einen Teil der Implementierung um.
262. Diese Zeile setzt einen Teil der Implementierung um.
263. Diese Zeile setzt einen Teil der Implementierung um.
264. Diese Zeile setzt einen Teil der Implementierung um.
265. Diese Zeile setzt einen Teil der Implementierung um.
266. Diese Zeile ist absichtlich leer.
267. Diese Zeile ist absichtlich leer.
268. Diese Zeile definiert einen Dekorator fuer die naechste Funktion.
269. Diese Zeile startet eine Funktionsdefinition.
270. Diese Zeile setzt einen Teil der Implementierung um.
271. Diese Zeile setzt einen Teil der Implementierung um.
272. Diese Zeile setzt einen Teil der Implementierung um.
273. Diese Zeile setzt einen Teil der Implementierung um.
274. Diese Zeile setzt einen Teil der Implementierung um.
275. Diese Zeile setzt einen Teil der Implementierung um.
276. Diese Zeile setzt einen Teil der Implementierung um.
277. Diese Zeile setzt einen Teil der Implementierung um.
278. Diese Zeile setzt einen Teil der Implementierung um.
279. Diese Zeile startet eine Schleife.
280. Diese Zeile setzt einen Teil der Implementierung um.
281. Diese Zeile gibt einen Wert an den Aufrufer zurueck.
282. Diese Zeile setzt einen Teil der Implementierung um.
283. Diese Zeile setzt einen Teil der Implementierung um.
284. Diese Zeile setzt einen Teil der Implementierung um.
285. Diese Zeile setzt einen Teil der Implementierung um.
286. Diese Zeile setzt einen Teil der Implementierung um.
287. Diese Zeile setzt einen Teil der Implementierung um.
288. Diese Zeile setzt einen Teil der Implementierung um.
289. Diese Zeile setzt einen Teil der Implementierung um.
290. Diese Zeile setzt einen Teil der Implementierung um.
291. Diese Zeile setzt einen Teil der Implementierung um.
292. Diese Zeile ist absichtlich leer.
293. Diese Zeile ist absichtlich leer.
294. Diese Zeile definiert einen Dekorator fuer die naechste Funktion.
295. Diese Zeile startet eine Funktionsdefinition.
296. Diese Zeile setzt einen Teil der Implementierung um.
297. Diese Zeile setzt einen Teil der Implementierung um.
298. Diese Zeile setzt einen Teil der Implementierung um.
299. Diese Zeile setzt einen Teil der Implementierung um.
300. Diese Zeile setzt einen Teil der Implementierung um.
301. Diese Zeile setzt einen Teil der Implementierung um.
302. Diese Zeile setzt einen Teil der Implementierung um.
303. Diese Zeile setzt einen Teil der Implementierung um.
304. Diese Zeile setzt einen Teil der Implementierung um.
305. Diese Zeile setzt einen Teil der Implementierung um.
306. Diese Zeile setzt einen Teil der Implementierung um.
307. Diese Zeile setzt einen Teil der Implementierung um.
308. Diese Zeile setzt einen Teil der Implementierung um.
309. Diese Zeile setzt einen Teil der Implementierung um.
310. Diese Zeile setzt einen Teil der Implementierung um.
311. Diese Zeile setzt einen Teil der Implementierung um.
312. Diese Zeile setzt einen Teil der Implementierung um.
313. Diese Zeile setzt einen Teil der Implementierung um.
314. Diese Zeile setzt einen Teil der Implementierung um.
315. Diese Zeile setzt einen Teil der Implementierung um.
316. Diese Zeile setzt einen Teil der Implementierung um.
317. Diese Zeile setzt einen Teil der Implementierung um.
318. Diese Zeile setzt einen Teil der Implementierung um.
319. Diese Zeile steuert den bedingten Ablauf.
320. Diese Zeile setzt einen Teil der Implementierung um.
321. Diese Zeile gehoert zur Fehlerbehandlung.
322. Diese Zeile setzt einen Teil der Implementierung um.
323. Diese Zeile gehoert zur Fehlerbehandlung.
324. Diese Zeile setzt einen Teil der Implementierung um.
325. Diese Zeile setzt einen Teil der Implementierung um.
326. Diese Zeile setzt einen Teil der Implementierung um.
327. Diese Zeile setzt einen Teil der Implementierung um.
328. Diese Zeile setzt einen Teil der Implementierung um.
329. Diese Zeile setzt einen Teil der Implementierung um.
330. Diese Zeile setzt einen Teil der Implementierung um.
331. Diese Zeile setzt einen Teil der Implementierung um.
332. Diese Zeile setzt einen Teil der Implementierung um.
333. Diese Zeile setzt einen Teil der Implementierung um.
334. Diese Zeile setzt einen Teil der Implementierung um.
335. Diese Zeile setzt einen Teil der Implementierung um.
336. Diese Zeile gibt einen Wert an den Aufrufer zurueck.
337. Diese Zeile ist absichtlich leer.
338. Diese Zeile ist absichtlich leer.
339. Diese Zeile definiert einen Dekorator fuer die naechste Funktion.
340. Diese Zeile startet eine Funktionsdefinition.
341. Diese Zeile setzt einen Teil der Implementierung um.
342. Diese Zeile setzt einen Teil der Implementierung um.
343. Diese Zeile setzt einen Teil der Implementierung um.
344. Diese Zeile setzt einen Teil der Implementierung um.
345. Diese Zeile setzt einen Teil der Implementierung um.
346. Diese Zeile setzt einen Teil der Implementierung um.
347. Diese Zeile setzt einen Teil der Implementierung um.
348. Diese Zeile setzt einen Teil der Implementierung um.
349. Diese Zeile gibt einen Wert an den Aufrufer zurueck.
350. Diese Zeile ist absichtlich leer.
351. Diese Zeile ist absichtlich leer.
352. Diese Zeile definiert einen Dekorator fuer die naechste Funktion.
353. Diese Zeile startet eine Funktionsdefinition.
354. Diese Zeile setzt einen Teil der Implementierung um.
355. Diese Zeile setzt einen Teil der Implementierung um.
356. Diese Zeile setzt einen Teil der Implementierung um.
357. Diese Zeile setzt einen Teil der Implementierung um.
358. Diese Zeile setzt einen Teil der Implementierung um.
359. Diese Zeile setzt einen Teil der Implementierung um.
360. Diese Zeile setzt einen Teil der Implementierung um.
361. Diese Zeile steuert den bedingten Ablauf.
362. Diese Zeile setzt einen Teil der Implementierung um.
363. Diese Zeile steuert den bedingten Ablauf.
364. Diese Zeile setzt einen Teil der Implementierung um.
365. Diese Zeile setzt einen Teil der Implementierung um.
366. Diese Zeile steuert den bedingten Ablauf.
367. Diese Zeile setzt einen Teil der Implementierung um.
368. Diese Zeile setzt einen Teil der Implementierung um.
369. Diese Zeile steuert den bedingten Ablauf.
370. Diese Zeile setzt einen Teil der Implementierung um.
371. Diese Zeile setzt einen Teil der Implementierung um.
372. Diese Zeile gibt einen Wert an den Aufrufer zurueck.
373. Diese Zeile ist absichtlich leer.
374. Diese Zeile ist absichtlich leer.
375. Diese Zeile definiert einen Dekorator fuer die naechste Funktion.
376. Diese Zeile startet eine Funktionsdefinition.
377. Diese Zeile setzt einen Teil der Implementierung um.
378. Diese Zeile setzt einen Teil der Implementierung um.
379. Diese Zeile setzt einen Teil der Implementierung um.
380. Diese Zeile setzt einen Teil der Implementierung um.
381. Diese Zeile setzt einen Teil der Implementierung um.
382. Diese Zeile steuert den bedingten Ablauf.
383. Diese Zeile setzt einen Teil der Implementierung um.
384. Diese Zeile steuert den bedingten Ablauf.
385. Diese Zeile setzt einen Teil der Implementierung um.
386. Diese Zeile setzt einen Teil der Implementierung um.
387. Diese Zeile setzt einen Teil der Implementierung um.
388. Diese Zeile setzt einen Teil der Implementierung um.
389. Diese Zeile gibt einen Wert an den Aufrufer zurueck.
390. Diese Zeile ist absichtlich leer.
391. Diese Zeile ist absichtlich leer.
392. Diese Zeile definiert einen Dekorator fuer die naechste Funktion.
393. Diese Zeile startet eine Funktionsdefinition.
394. Diese Zeile setzt einen Teil der Implementierung um.
395. Diese Zeile setzt einen Teil der Implementierung um.
396. Diese Zeile setzt einen Teil der Implementierung um.
397. Diese Zeile setzt einen Teil der Implementierung um.
398. Diese Zeile setzt einen Teil der Implementierung um.
399. Diese Zeile setzt einen Teil der Implementierung um.
400. Diese Zeile steuert den bedingten Ablauf.
401. Diese Zeile setzt einen Teil der Implementierung um.
402. Diese Zeile setzt einen Teil der Implementierung um.
403. Diese Zeile setzt einen Teil der Implementierung um.
404. Diese Zeile setzt einen Teil der Implementierung um.
405. Diese Zeile setzt einen Teil der Implementierung um.
406. Diese Zeile steuert den bedingten Ablauf.
407. Diese Zeile setzt einen Teil der Implementierung um.
408. Diese Zeile setzt einen Teil der Implementierung um.
409. Diese Zeile steuert den bedingten Ablauf.
410. Diese Zeile setzt einen Teil der Implementierung um.
411. Diese Zeile setzt einen Teil der Implementierung um.
412. Diese Zeile setzt einen Teil der Implementierung um.
413. Diese Zeile steuert den bedingten Ablauf.
414. Diese Zeile gibt einen Wert an den Aufrufer zurueck.
415. Diese Zeile setzt einen Teil der Implementierung um.
416. Diese Zeile setzt einen Teil der Implementierung um.
417. Diese Zeile setzt einen Teil der Implementierung um.
418. Diese Zeile gibt einen Wert an den Aufrufer zurueck.
419. Diese Zeile ist absichtlich leer.
420. Diese Zeile ist absichtlich leer.
421. Diese Zeile definiert einen Dekorator fuer die naechste Funktion.
422. Diese Zeile startet eine Funktionsdefinition.
423. Diese Zeile setzt einen Teil der Implementierung um.
424. Diese Zeile setzt einen Teil der Implementierung um.
425. Diese Zeile setzt einen Teil der Implementierung um.
426. Diese Zeile setzt einen Teil der Implementierung um.
427. Diese Zeile setzt einen Teil der Implementierung um.
428. Diese Zeile setzt einen Teil der Implementierung um.
429. Diese Zeile setzt einen Teil der Implementierung um.
430. Diese Zeile setzt einen Teil der Implementierung um.
431. Diese Zeile setzt einen Teil der Implementierung um.
432. Diese Zeile setzt einen Teil der Implementierung um.
433. Diese Zeile setzt einen Teil der Implementierung um.
434. Diese Zeile gibt einen Wert an den Aufrufer zurueck.
435. Diese Zeile setzt einen Teil der Implementierung um.
436. Diese Zeile setzt einen Teil der Implementierung um.
437. Diese Zeile setzt einen Teil der Implementierung um.
438. Diese Zeile ist absichtlich leer.
439. Diese Zeile ist absichtlich leer.
440. Diese Zeile definiert einen Dekorator fuer die naechste Funktion.
441. Diese Zeile startet eine Funktionsdefinition.
442. Diese Zeile setzt einen Teil der Implementierung um.
443. Diese Zeile setzt einen Teil der Implementierung um.
444. Diese Zeile setzt einen Teil der Implementierung um.
445. Diese Zeile setzt einen Teil der Implementierung um.
446. Diese Zeile setzt einen Teil der Implementierung um.
447. Diese Zeile steuert den bedingten Ablauf.
448. Diese Zeile setzt einen Teil der Implementierung um.
449. Diese Zeile setzt einen Teil der Implementierung um.
450. Diese Zeile gibt einen Wert an den Aufrufer zurueck.
451. Diese Zeile setzt einen Teil der Implementierung um.
452. Diese Zeile setzt einen Teil der Implementierung um.
453. Diese Zeile setzt einen Teil der Implementierung um.
454. Diese Zeile ist absichtlich leer.
455. Diese Zeile ist absichtlich leer.
456. Diese Zeile definiert einen Dekorator fuer die naechste Funktion.
457. Diese Zeile startet eine Funktionsdefinition.
458. Diese Zeile setzt einen Teil der Implementierung um.
459. Diese Zeile setzt einen Teil der Implementierung um.
460. Diese Zeile setzt einen Teil der Implementierung um.
461. Diese Zeile setzt einen Teil der Implementierung um.
462. Diese Zeile setzt einen Teil der Implementierung um.
463. Diese Zeile setzt einen Teil der Implementierung um.
464. Diese Zeile setzt einen Teil der Implementierung um.
465. Diese Zeile setzt einen Teil der Implementierung um.
466. Diese Zeile setzt einen Teil der Implementierung um.
467. Diese Zeile setzt einen Teil der Implementierung um.
468. Diese Zeile setzt einen Teil der Implementierung um.
469. Diese Zeile gehoert zur Fehlerbehandlung.
470. Diese Zeile setzt einen Teil der Implementierung um.
471. Diese Zeile gehoert zur Fehlerbehandlung.
472. Diese Zeile setzt einen Teil der Implementierung um.
473. Diese Zeile setzt einen Teil der Implementierung um.
474. Diese Zeile setzt einen Teil der Implementierung um.
475. Diese Zeile steuert den bedingten Ablauf.
476. Diese Zeile setzt einen Teil der Implementierung um.
477. Diese Zeile setzt einen Teil der Implementierung um.
478. Diese Zeile setzt einen Teil der Implementierung um.
479. Diese Zeile setzt einen Teil der Implementierung um.
480. Diese Zeile setzt einen Teil der Implementierung um.
481. Diese Zeile setzt einen Teil der Implementierung um.
482. Diese Zeile setzt einen Teil der Implementierung um.
483. Diese Zeile setzt einen Teil der Implementierung um.
484. Diese Zeile setzt einen Teil der Implementierung um.
485. Diese Zeile setzt einen Teil der Implementierung um.
486. Diese Zeile setzt einen Teil der Implementierung um.
487. Diese Zeile steuert den bedingten Ablauf.
488. Diese Zeile setzt einen Teil der Implementierung um.
489. Diese Zeile setzt einen Teil der Implementierung um.
490. Diese Zeile steuert den bedingten Ablauf.
491. Diese Zeile gibt einen Wert an den Aufrufer zurueck.
492. Diese Zeile gibt einen Wert an den Aufrufer zurueck.
493. Diese Zeile ist absichtlich leer.
494. Diese Zeile ist absichtlich leer.
495. Diese Zeile definiert einen Dekorator fuer die naechste Funktion.
496. Diese Zeile startet eine Funktionsdefinition.
497. Diese Zeile setzt einen Teil der Implementierung um.
498. Diese Zeile steuert den bedingten Ablauf.
499. Diese Zeile setzt einen Teil der Implementierung um.
500. Diese Zeile gibt einen Wert an den Aufrufer zurueck.
501. Diese Zeile ist absichtlich leer.
502. Diese Zeile ist absichtlich leer.
503. Diese Zeile definiert einen Dekorator fuer die naechste Funktion.
504. Diese Zeile startet eine Funktionsdefinition.
505. Diese Zeile gehoert zur Fehlerbehandlung.
506. Diese Zeile setzt einen Teil der Implementierung um.
507. Diese Zeile gehoert zur Fehlerbehandlung.
508. Diese Zeile setzt einen Teil der Implementierung um.
509. Diese Zeile steuert den bedingten Ablauf.
510. Diese Zeile setzt einen Teil der Implementierung um.
511. Diese Zeile gibt einen Wert an den Aufrufer zurueck.
512. Diese Zeile ist absichtlich leer.
513. Diese Zeile ist absichtlich leer.
514. Diese Zeile definiert einen Dekorator fuer die naechste Funktion.
515. Diese Zeile startet eine Funktionsdefinition.
516. Diese Zeile setzt einen Teil der Implementierung um.
517. Diese Zeile setzt einen Teil der Implementierung um.
518. Diese Zeile setzt einen Teil der Implementierung um.
519. Diese Zeile setzt einen Teil der Implementierung um.
520. Diese Zeile setzt einen Teil der Implementierung um.
521. Diese Zeile steuert den bedingten Ablauf.
522. Diese Zeile setzt einen Teil der Implementierung um.
523. Diese Zeile setzt einen Teil der Implementierung um.
524. Diese Zeile setzt einen Teil der Implementierung um.
525. Diese Zeile setzt einen Teil der Implementierung um.
526. Diese Zeile setzt einen Teil der Implementierung um.
527. Diese Zeile setzt einen Teil der Implementierung um.
528. Diese Zeile setzt einen Teil der Implementierung um.
529. Diese Zeile gibt einen Wert an den Aufrufer zurueck.
530. Diese Zeile ist absichtlich leer.
531. Diese Zeile ist absichtlich leer.
532. Diese Zeile definiert einen Dekorator fuer die naechste Funktion.
533. Diese Zeile startet eine Funktionsdefinition.
534. Diese Zeile setzt einen Teil der Implementierung um.
535. Diese Zeile setzt einen Teil der Implementierung um.
536. Diese Zeile setzt einen Teil der Implementierung um.
537. Diese Zeile setzt einen Teil der Implementierung um.
538. Diese Zeile setzt einen Teil der Implementierung um.
539. Diese Zeile setzt einen Teil der Implementierung um.
540. Diese Zeile steuert den bedingten Ablauf.
541. Diese Zeile setzt einen Teil der Implementierung um.
542. Diese Zeile setzt einen Teil der Implementierung um.
543. Diese Zeile setzt einen Teil der Implementierung um.
544. Diese Zeile setzt einen Teil der Implementierung um.
545. Diese Zeile setzt einen Teil der Implementierung um.
546. Diese Zeile setzt einen Teil der Implementierung um.
547. Diese Zeile setzt einen Teil der Implementierung um.
548. Diese Zeile setzt einen Teil der Implementierung um.
549. Diese Zeile steuert den bedingten Ablauf.
550. Diese Zeile gibt einen Wert an den Aufrufer zurueck.
551. Diese Zeile gibt einen Wert an den Aufrufer zurueck.
552. Diese Zeile ist absichtlich leer.
553. Diese Zeile ist absichtlich leer.
554. Diese Zeile definiert einen Dekorator fuer die naechste Funktion.
555. Diese Zeile startet eine Funktionsdefinition.
556. Diese Zeile setzt einen Teil der Implementierung um.
557. Diese Zeile setzt einen Teil der Implementierung um.
558. Diese Zeile setzt einen Teil der Implementierung um.
559. Diese Zeile setzt einen Teil der Implementierung um.
560. Diese Zeile setzt einen Teil der Implementierung um.
561. Diese Zeile setzt einen Teil der Implementierung um.
562. Diese Zeile steuert den bedingten Ablauf.
563. Diese Zeile setzt einen Teil der Implementierung um.
564. Diese Zeile setzt einen Teil der Implementierung um.
565. Diese Zeile setzt einen Teil der Implementierung um.
566. Diese Zeile setzt einen Teil der Implementierung um.
567. Diese Zeile setzt einen Teil der Implementierung um.
568. Diese Zeile steuert den bedingten Ablauf.
569. Diese Zeile gibt einen Wert an den Aufrufer zurueck.
570. Diese Zeile gibt einen Wert an den Aufrufer zurueck.
571. Diese Zeile ist absichtlich leer.
572. Diese Zeile ist absichtlich leer.
573. Diese Zeile definiert einen Dekorator fuer die naechste Funktion.
574. Diese Zeile startet eine Funktionsdefinition.
575. Diese Zeile setzt einen Teil der Implementierung um.
576. Diese Zeile setzt einen Teil der Implementierung um.
577. Diese Zeile setzt einen Teil der Implementierung um.
578. Diese Zeile setzt einen Teil der Implementierung um.
579. Diese Zeile setzt einen Teil der Implementierung um.
580. Diese Zeile setzt einen Teil der Implementierung um.
581. Diese Zeile setzt einen Teil der Implementierung um.
582. Diese Zeile setzt einen Teil der Implementierung um.
583. Diese Zeile setzt einen Teil der Implementierung um.
584. Diese Zeile setzt einen Teil der Implementierung um.
585. Diese Zeile gibt einen Wert an den Aufrufer zurueck.

## app/templates/recipe_detail.html
```html
{% extends "base.html" %}
{% block content %}
<article class="panel">
  <h1>{{ recipe.title }}</h1>
  <p>{{ recipe.description }}</p>
  <p class="meta">{{ recipe.category }} | {{ recipe.difficulty }} | {{ recipe.prep_time_minutes }} min</p>
  <p class="meta">Average rating: {{ "%.2f"|format(avg_rating) }} ({{ review_count }} reviews)</p>
  <div class="actions">
    <a href="/recipes/{{ recipe.id }}/pdf" target="_blank">PDF herunterladen</a>
    {% if current_user and (current_user.id == recipe.creator_id or current_user.role == "admin") %}
    <a href="/recipes/{{ recipe.id }}/edit">Edit</a>
    <form method="post" action="/recipes/{{ recipe.id }}/delete" class="inline">
      <button type="submit">Delete</button>
    </form>
    {% endif %}
  </div>
  <div id="favorite-box">
    {% include "partials/favorite_button.html" %}
  </div>
</article>
{% include "partials/recipe_images.html" %}
<section class="panel">
  <h2>Ingredients</h2>
  <ul>
    {% for link in recipe.recipe_ingredients %}
    <li>{{ link.ingredient.name }} {{ link.quantity_text }} {% if link.grams %}({{ link.grams }} g){% endif %}</li>
    {% else %}
    <li>No ingredients stored.</li>
    {% endfor %}
  </ul>
</section>
<section class="panel">
  <h2>Instructions</h2>
  {% for paragraph in recipe.instructions.splitlines() %}
  {% if paragraph.strip() %}<p>{{ paragraph }}</p>{% endif %}
  {% endfor %}
</section>
<section class="panel">
  <h2>Reviews</h2>
  {% if current_user %}
  <form method="post" action="/recipes/{{ recipe.id }}/reviews" class="stack">
    <label>Rating
      <select name="rating">
        <option value="1">1</option>
        <option value="2">2</option>
        <option value="3">3</option>
        <option value="4">4</option>
        <option value="5" selected>5</option>
      </select>
    </label>
    <label>Comment <textarea name="comment" rows="3"></textarea></label>
    <button type="submit">Save review</button>
  </form>
  {% endif %}
  {% for review in recipe.reviews %}
  <article class="card">
    <p><strong>{{ review.user.email }}</strong> rated {{ review.rating }}/5</p>
    <p>{{ review.comment }}</p>
    {% if current_user and (current_user.id == review.user_id or current_user.role == "admin") %}
    <form method="post" action="/reviews/{{ review.id }}/delete">
      <button type="submit">Delete review</button>
    </form>
    {% endif %}
  </article>
  {% else %}
  <p>No reviews yet.</p>
  {% endfor %}
</section>
{% endblock %}
```
ZEILEN-ERKLAERUNG
1. Diese Zeile enthaelt Jinja-Template-Logik.
2. Diese Zeile enthaelt Jinja-Template-Logik.
3. Diese Zeile setzt einen Teil der Implementierung um.
4. Diese Zeile setzt einen Teil der Implementierung um.
5. Diese Zeile setzt einen Teil der Implementierung um.
6. Diese Zeile setzt einen Teil der Implementierung um.
7. Diese Zeile setzt einen Teil der Implementierung um.
8. Diese Zeile setzt einen Teil der Implementierung um.
9. Diese Zeile setzt einen Teil der Implementierung um.
10. Diese Zeile enthaelt Jinja-Template-Logik.
11. Diese Zeile setzt einen Teil der Implementierung um.
12. Diese Zeile setzt einen Teil der Implementierung um.
13. Diese Zeile setzt einen Teil der Implementierung um.
14. Diese Zeile setzt einen Teil der Implementierung um.
15. Diese Zeile enthaelt Jinja-Template-Logik.
16. Diese Zeile setzt einen Teil der Implementierung um.
17. Diese Zeile setzt einen Teil der Implementierung um.
18. Diese Zeile enthaelt Jinja-Template-Logik.
19. Diese Zeile setzt einen Teil der Implementierung um.
20. Diese Zeile setzt einen Teil der Implementierung um.
21. Diese Zeile enthaelt Jinja-Template-Logik.
22. Diese Zeile setzt einen Teil der Implementierung um.
23. Diese Zeile setzt einen Teil der Implementierung um.
24. Diese Zeile setzt einen Teil der Implementierung um.
25. Diese Zeile enthaelt Jinja-Template-Logik.
26. Diese Zeile setzt einen Teil der Implementierung um.
27. Diese Zeile enthaelt Jinja-Template-Logik.
28. Diese Zeile setzt einen Teil der Implementierung um.
29. Diese Zeile enthaelt Jinja-Template-Logik.
30. Diese Zeile setzt einen Teil der Implementierung um.
31. Diese Zeile setzt einen Teil der Implementierung um.
32. Diese Zeile setzt einen Teil der Implementierung um.
33. Diese Zeile setzt einen Teil der Implementierung um.
34. Diese Zeile enthaelt Jinja-Template-Logik.
35. Diese Zeile enthaelt Jinja-Template-Logik.
36. Diese Zeile enthaelt Jinja-Template-Logik.
37. Diese Zeile setzt einen Teil der Implementierung um.
38. Diese Zeile setzt einen Teil der Implementierung um.
39. Diese Zeile setzt einen Teil der Implementierung um.
40. Diese Zeile enthaelt Jinja-Template-Logik.
41. Diese Zeile setzt einen Teil der Implementierung um.
42. Diese Zeile setzt einen Teil der Implementierung um.
43. Diese Zeile setzt einen Teil der Implementierung um.
44. Diese Zeile setzt einen Teil der Implementierung um.
45. Diese Zeile setzt einen Teil der Implementierung um.
46. Diese Zeile setzt einen Teil der Implementierung um.
47. Diese Zeile setzt einen Teil der Implementierung um.
48. Diese Zeile setzt einen Teil der Implementierung um.
49. Diese Zeile setzt einen Teil der Implementierung um.
50. Diese Zeile setzt einen Teil der Implementierung um.
51. Diese Zeile setzt einen Teil der Implementierung um.
52. Diese Zeile setzt einen Teil der Implementierung um.
53. Diese Zeile setzt einen Teil der Implementierung um.
54. Diese Zeile enthaelt Jinja-Template-Logik.
55. Diese Zeile enthaelt Jinja-Template-Logik.
56. Diese Zeile setzt einen Teil der Implementierung um.
57. Diese Zeile setzt einen Teil der Implementierung um.
58. Diese Zeile setzt einen Teil der Implementierung um.
59. Diese Zeile enthaelt Jinja-Template-Logik.
60. Diese Zeile setzt einen Teil der Implementierung um.
61. Diese Zeile setzt einen Teil der Implementierung um.
62. Diese Zeile setzt einen Teil der Implementierung um.
63. Diese Zeile enthaelt Jinja-Template-Logik.
64. Diese Zeile setzt einen Teil der Implementierung um.
65. Diese Zeile enthaelt Jinja-Template-Logik.
66. Diese Zeile setzt einen Teil der Implementierung um.
67. Diese Zeile enthaelt Jinja-Template-Logik.
68. Diese Zeile setzt einen Teil der Implementierung um.
69. Diese Zeile enthaelt Jinja-Template-Logik.

## app/templates/partials/recipe_images.html
```html
<section class="panel" id="recipe-images-section">
  <h2>Images</h2>
  {% if primary_image %}
  <img src="/images/{{ primary_image.id }}" alt="{{ recipe.title }}" class="hero-image">
  {% elif recipe.title_image_url or recipe.source_image_url %}
  <img src="/external-image?url={{ (recipe.title_image_url or recipe.source_image_url)|urlencode }}" alt="{{ recipe.title }}" class="hero-image">
  {% endif %}
  {% if current_user and (current_user.id == recipe.creator_id or current_user.role == "admin") %}
  <form
    method="post"
    action="/recipes/{{ recipe.id }}/images"
    enctype="multipart/form-data"
    hx-post="/recipes/{{ recipe.id }}/images"
    hx-encoding="multipart/form-data"
    hx-target="#recipe-images-section"
    hx-swap="outerHTML"
    class="stack"
  >
    <label>Neue Bilddatei
      <input type="file" name="file" accept="image/png,image/jpeg,image/webp" required>
    </label>
    <label class="inline">
      <input type="checkbox" name="set_primary" value="true">
      Als Hauptbild setzen
    </label>
    <button type="submit">Bild hochladen</button>
  </form>
  {% endif %}
  <div class="cards">
    {% for image in recipe.images %}
    <article class="card">
      <img src="/images/{{ image.id }}" alt="{{ image.filename }}" class="thumb">
      <p>{{ image.filename }}</p>
      {% if image.is_primary %}
      <p class="meta">Hauptbild</p>
      {% endif %}
      {% if current_user and (current_user.id == recipe.creator_id or current_user.role == "admin") %}
      <div class="actions">
        {% if not image.is_primary %}
        <form
          method="post"
          action="/images/{{ image.id }}/set-primary"
          hx-post="/images/{{ image.id }}/set-primary"
          hx-target="#recipe-images-section"
          hx-swap="outerHTML"
        >
          <button type="submit">Als Hauptbild</button>
        </form>
        {% endif %}
        <form
          method="post"
          action="/images/{{ image.id }}/delete"
          hx-post="/images/{{ image.id }}/delete"
          hx-target="#recipe-images-section"
          hx-swap="outerHTML"
        >
          <button type="submit">Löschen</button>
        </form>
      </div>
      {% endif %}
    </article>
    {% else %}
    <p>Noch keine Bilder vorhanden.</p>
    {% endfor %}
  </div>
</section>
```
ZEILEN-ERKLAERUNG
1. Diese Zeile setzt einen Teil der Implementierung um.
2. Diese Zeile setzt einen Teil der Implementierung um.
3. Diese Zeile enthaelt Jinja-Template-Logik.
4. Diese Zeile setzt einen Teil der Implementierung um.
5. Diese Zeile enthaelt Jinja-Template-Logik.
6. Diese Zeile setzt einen Teil der Implementierung um.
7. Diese Zeile enthaelt Jinja-Template-Logik.
8. Diese Zeile enthaelt Jinja-Template-Logik.
9. Diese Zeile setzt einen Teil der Implementierung um.
10. Diese Zeile setzt einen Teil der Implementierung um.
11. Diese Zeile setzt einen Teil der Implementierung um.
12. Diese Zeile setzt einen Teil der Implementierung um.
13. Diese Zeile setzt einen Teil der Implementierung um.
14. Diese Zeile setzt einen Teil der Implementierung um.
15. Diese Zeile setzt einen Teil der Implementierung um.
16. Diese Zeile setzt einen Teil der Implementierung um.
17. Diese Zeile setzt einen Teil der Implementierung um.
18. Diese Zeile setzt einen Teil der Implementierung um.
19. Diese Zeile setzt einen Teil der Implementierung um.
20. Diese Zeile setzt einen Teil der Implementierung um.
21. Diese Zeile setzt einen Teil der Implementierung um.
22. Diese Zeile setzt einen Teil der Implementierung um.
23. Diese Zeile setzt einen Teil der Implementierung um.
24. Diese Zeile setzt einen Teil der Implementierung um.
25. Diese Zeile setzt einen Teil der Implementierung um.
26. Diese Zeile setzt einen Teil der Implementierung um.
27. Diese Zeile setzt einen Teil der Implementierung um.
28. Diese Zeile enthaelt Jinja-Template-Logik.
29. Diese Zeile setzt einen Teil der Implementierung um.
30. Diese Zeile enthaelt Jinja-Template-Logik.
31. Diese Zeile setzt einen Teil der Implementierung um.
32. Diese Zeile setzt einen Teil der Implementierung um.
33. Diese Zeile setzt einen Teil der Implementierung um.
34. Diese Zeile enthaelt Jinja-Template-Logik.
35. Diese Zeile setzt einen Teil der Implementierung um.
36. Diese Zeile enthaelt Jinja-Template-Logik.
37. Diese Zeile enthaelt Jinja-Template-Logik.
38. Diese Zeile setzt einen Teil der Implementierung um.
39. Diese Zeile enthaelt Jinja-Template-Logik.
40. Diese Zeile setzt einen Teil der Implementierung um.
41. Diese Zeile setzt einen Teil der Implementierung um.
42. Diese Zeile setzt einen Teil der Implementierung um.
43. Diese Zeile setzt einen Teil der Implementierung um.
44. Diese Zeile setzt einen Teil der Implementierung um.
45. Diese Zeile setzt einen Teil der Implementierung um.
46. Diese Zeile setzt einen Teil der Implementierung um.
47. Diese Zeile setzt einen Teil der Implementierung um.
48. Diese Zeile setzt einen Teil der Implementierung um.
49. Diese Zeile enthaelt Jinja-Template-Logik.
50. Diese Zeile setzt einen Teil der Implementierung um.
51. Diese Zeile setzt einen Teil der Implementierung um.
52. Diese Zeile setzt einen Teil der Implementierung um.
53. Diese Zeile setzt einen Teil der Implementierung um.
54. Diese Zeile setzt einen Teil der Implementierung um.
55. Diese Zeile setzt einen Teil der Implementierung um.
56. Diese Zeile setzt einen Teil der Implementierung um.
57. Diese Zeile setzt einen Teil der Implementierung um.
58. Diese Zeile setzt einen Teil der Implementierung um.
59. Diese Zeile setzt einen Teil der Implementierung um.
60. Diese Zeile enthaelt Jinja-Template-Logik.
61. Diese Zeile setzt einen Teil der Implementierung um.
62. Diese Zeile enthaelt Jinja-Template-Logik.
63. Diese Zeile setzt einen Teil der Implementierung um.
64. Diese Zeile enthaelt Jinja-Template-Logik.
65. Diese Zeile setzt einen Teil der Implementierung um.
66. Diese Zeile setzt einen Teil der Implementierung um.

## alembic/versions/20260303_0004_recipe_images_primary.py
```python
"""add recipe image primary flag

Revision ID: 20260303_0004
Revises: 20260303_0003
Create Date: 2026-03-03 16:10:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20260303_0004"
down_revision: Union[str, None] = "20260303_0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("recipe_images", sa.Column("is_primary", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.execute(
        """
        UPDATE recipe_images
        SET is_primary = 1
        WHERE id IN (
          SELECT MIN(id) FROM recipe_images GROUP BY recipe_id
        )
        """
    )


def downgrade() -> None:
    op.drop_column("recipe_images", "is_primary")
```
ZEILEN-ERKLAERUNG
1. Diese Zeile setzt einen Teil der Implementierung um.
2. Diese Zeile ist absichtlich leer.
3. Diese Zeile setzt einen Teil der Implementierung um.
4. Diese Zeile setzt einen Teil der Implementierung um.
5. Diese Zeile setzt einen Teil der Implementierung um.
6. Diese Zeile setzt einen Teil der Implementierung um.
7. Diese Zeile ist absichtlich leer.
8. Diese Zeile importiert eine benoetigte Abhaengigkeit.
9. Diese Zeile ist absichtlich leer.
10. Diese Zeile importiert eine benoetigte Abhaengigkeit.
11. Diese Zeile importiert eine benoetigte Abhaengigkeit.
12. Diese Zeile ist absichtlich leer.
13. Diese Zeile ist ein erlaeuternder Kommentar.
14. Diese Zeile setzt einen Teil der Implementierung um.
15. Diese Zeile setzt einen Teil der Implementierung um.
16. Diese Zeile setzt einen Teil der Implementierung um.
17. Diese Zeile setzt einen Teil der Implementierung um.
18. Diese Zeile ist absichtlich leer.
19. Diese Zeile ist absichtlich leer.
20. Diese Zeile startet eine Funktionsdefinition.
21. Diese Zeile setzt einen Teil der Implementierung um.
22. Diese Zeile setzt einen Teil der Implementierung um.
23. Diese Zeile setzt einen Teil der Implementierung um.
24. Diese Zeile setzt einen Teil der Implementierung um.
25. Diese Zeile setzt einen Teil der Implementierung um.
26. Diese Zeile setzt einen Teil der Implementierung um.
27. Diese Zeile setzt einen Teil der Implementierung um.
28. Diese Zeile setzt einen Teil der Implementierung um.
29. Diese Zeile setzt einen Teil der Implementierung um.
30. Diese Zeile setzt einen Teil der Implementierung um.
31. Diese Zeile ist absichtlich leer.
32. Diese Zeile ist absichtlich leer.
33. Diese Zeile startet eine Funktionsdefinition.
34. Diese Zeile setzt einen Teil der Implementierung um.
