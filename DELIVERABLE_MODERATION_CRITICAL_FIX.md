# Deliverable: Kritischer Moderations-Fix

## Betroffene Dateien
- `app/models.py`
- `alembic/versions/20260303_0006_add_recipe_is_published.py`
- `app/services.py`
- `app/csv_import.py`
- `app/routers/recipes.py`
- `app/templates/base.html`
- `app/i18n/de.py`
- `app/moderation_repair.py`
- `scripts/moderation_repair.py`
- `scripts/seed_test_accounts_and_recipes.py`
- `requirements.txt`
- `tests/conftest.py`
- `tests/test_moderation_workflow.py`
- `README_MODERATION.md`

## app/models.py
```python
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, LargeBinary, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


SUBMISSION_STATUS_ENUM = Enum(
    "pending",
    "approved",
    "rejected",
    name="submission_status",
    native_enum=False,
)


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
    submissions: Mapped[list["RecipeSubmission"]] = relationship(
        back_populates="submitter_user",
        cascade="all, delete-orphan",
        foreign_keys="RecipeSubmission.submitter_user_id",
    )
    reviewed_submissions: Mapped[list["RecipeSubmission"]] = relationship(
        back_populates="reviewed_by_admin",
        foreign_keys="RecipeSubmission.reviewed_by_admin_id",
    )


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
    is_published: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
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


class RecipeSubmission(Base):
    __tablename__ = "recipe_submissions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    submitter_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    submitter_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    difficulty: Mapped[str] = mapped_column(String(30), nullable=False, default="medium", index=True)
    prep_time_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    servings_text: Mapped[str | None] = mapped_column(String(120), nullable=True)
    instructions: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(SUBMISSION_STATUS_ENUM, nullable=False, default="pending", server_default="pending", index=True)
    admin_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    reviewed_by_admin_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)

    submitter_user: Mapped["User"] = relationship(
        back_populates="submissions",
        foreign_keys=[submitter_user_id],
    )
    reviewed_by_admin: Mapped["User"] = relationship(
        back_populates="reviewed_submissions",
        foreign_keys=[reviewed_by_admin_id],
    )
    ingredients: Mapped[list["SubmissionIngredient"]] = relationship(
        back_populates="submission",
        cascade="all, delete-orphan",
        order_by="SubmissionIngredient.id",
    )
    images: Mapped[list["SubmissionImage"]] = relationship(
        back_populates="submission",
        cascade="all, delete-orphan",
        order_by="SubmissionImage.created_at",
    )


class SubmissionIngredient(Base):
    __tablename__ = "submission_ingredients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    submission_id: Mapped[int] = mapped_column(ForeignKey("recipe_submissions.id", ondelete="CASCADE"), nullable=False, index=True)
    ingredient_name: Mapped[str] = mapped_column(String(200), nullable=False)
    quantity_text: Mapped[str] = mapped_column(String(120), nullable=False, default="")
    grams: Mapped[int | None] = mapped_column(Integer, nullable=True)
    ingredient_name_normalized: Mapped[str | None] = mapped_column(String(200), nullable=True, index=True)

    submission: Mapped["RecipeSubmission"] = relationship(back_populates="ingredients")


class SubmissionImage(Base):
    __tablename__ = "submission_images"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    submission_id: Mapped[int] = mapped_column(ForeignKey("recipe_submissions.id", ondelete="CASCADE"), nullable=False, index=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str] = mapped_column(String(50), nullable=False)
    data: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    submission: Mapped["RecipeSubmission"] = relationship(back_populates="images")


class AppMeta(Base):
    __tablename__ = "app_meta"

    key: Mapped[str] = mapped_column(String(120), primary_key=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)
```
ZEILEN-ERKL?RUNG
1. Diese Zeile definiert den Inhalt 'from datetime import datetime, timezone'.
2. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
3. Diese Zeile definiert den Inhalt 'from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, LargeBinary, Strin...'.
4. Diese Zeile definiert den Inhalt 'from sqlalchemy.orm import Mapped, mapped_column, relationship'.
5. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
6. Diese Zeile definiert den Inhalt 'from app.database import Base'.
7. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
8. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
9. Diese Zeile definiert den Inhalt 'def utc_now() -> datetime:'.
10. Diese Zeile definiert den Inhalt 'return datetime.now(timezone.utc)'.
11. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
12. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
13. Diese Zeile definiert den Inhalt 'SUBMISSION_STATUS_ENUM = Enum('.
14. Diese Zeile definiert den Inhalt '"pending",'.
15. Diese Zeile definiert den Inhalt '"approved",'.
16. Diese Zeile definiert den Inhalt '"rejected",'.
17. Diese Zeile definiert den Inhalt 'name="submission_status",'.
18. Diese Zeile definiert den Inhalt 'native_enum=False,'.
19. Diese Zeile definiert den Inhalt ')'.
20. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
21. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
22. Diese Zeile definiert den Inhalt 'class User(Base):'.
23. Diese Zeile definiert den Inhalt '__tablename__ = "users"'.
24. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
25. Diese Zeile definiert den Inhalt 'id: Mapped[int] = mapped_column(Integer, primary_key=True)'.
26. Diese Zeile definiert den Inhalt 'email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)'.
27. Diese Zeile definiert den Inhalt 'hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)'.
28. Diese Zeile definiert den Inhalt 'role: Mapped[str] = mapped_column(String(20), default="user", nullable=False)'.
29. Diese Zeile definiert den Inhalt 'created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, ...'.
30. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
31. Diese Zeile definiert den Inhalt 'recipes: Mapped[list["Recipe"]] = relationship(back_populates="creator", cascade="all, ...'.
32. Diese Zeile definiert den Inhalt 'reviews: Mapped[list["Review"]] = relationship(back_populates="user", cascade="all, del...'.
33. Diese Zeile definiert den Inhalt 'favorites: Mapped[list["Favorite"]] = relationship(back_populates="user", cascade="all,...'.
34. Diese Zeile definiert den Inhalt 'submissions: Mapped[list["RecipeSubmission"]] = relationship('.
35. Diese Zeile definiert den Inhalt 'back_populates="submitter_user",'.
36. Diese Zeile definiert den Inhalt 'cascade="all, delete-orphan",'.
37. Diese Zeile definiert den Inhalt 'foreign_keys="RecipeSubmission.submitter_user_id",'.
38. Diese Zeile definiert den Inhalt ')'.
39. Diese Zeile definiert den Inhalt 'reviewed_submissions: Mapped[list["RecipeSubmission"]] = relationship('.
40. Diese Zeile definiert den Inhalt 'back_populates="reviewed_by_admin",'.
41. Diese Zeile definiert den Inhalt 'foreign_keys="RecipeSubmission.reviewed_by_admin_id",'.
42. Diese Zeile definiert den Inhalt ')'.
43. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
44. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
45. Diese Zeile definiert den Inhalt 'class Recipe(Base):'.
46. Diese Zeile definiert den Inhalt '__tablename__ = "recipes"'.
47. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
48. Diese Zeile definiert den Inhalt 'id: Mapped[int] = mapped_column(Integer, primary_key=True)'.
49. Diese Zeile definiert den Inhalt 'title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)'.
50. Diese Zeile definiert den Inhalt 'title_image_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)'.
51. Diese Zeile definiert den Inhalt 'source: Mapped[str] = mapped_column(String(50), nullable=False, default="user", index=T...'.
52. Diese Zeile definiert den Inhalt 'source_uuid: Mapped[str | None] = mapped_column(String(120), nullable=True, unique=True...'.
53. Diese Zeile definiert den Inhalt 'source_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)'.
54. Diese Zeile definiert den Inhalt 'source_image_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)'.
55. Diese Zeile definiert den Inhalt 'servings_text: Mapped[str | None] = mapped_column(String(120), nullable=True)'.
56. Diese Zeile definiert den Inhalt 'total_time_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)'.
57. Diese Zeile definiert den Inhalt 'is_published: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index...'.
58. Diese Zeile definiert den Inhalt 'description: Mapped[str] = mapped_column(Text, nullable=False)'.
59. Diese Zeile definiert den Inhalt 'instructions: Mapped[str] = mapped_column(Text, nullable=False)'.
60. Diese Zeile definiert den Inhalt 'category: Mapped[str] = mapped_column(String(120), nullable=False, index=True)'.
61. Diese Zeile definiert den Inhalt 'prep_time_minutes: Mapped[int] = mapped_column(Integer, nullable=False, index=True)'.
62. Diese Zeile definiert den Inhalt 'difficulty: Mapped[str] = mapped_column(String(30), nullable=False, index=True)'.
63. Diese Zeile definiert den Inhalt 'creator_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nul...'.
64. Diese Zeile definiert den Inhalt 'created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, ...'.
65. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
66. Diese Zeile definiert den Inhalt 'creator: Mapped["User"] = relationship(back_populates="recipes")'.
67. Diese Zeile definiert den Inhalt 'recipe_ingredients: Mapped[list["RecipeIngredient"]] = relationship('.
68. Diese Zeile definiert den Inhalt 'back_populates="recipe",'.
69. Diese Zeile definiert den Inhalt 'cascade="all, delete-orphan",'.
70. Diese Zeile definiert den Inhalt ')'.
71. Diese Zeile definiert den Inhalt 'reviews: Mapped[list["Review"]] = relationship(back_populates="recipe", cascade="all, d...'.
72. Diese Zeile definiert den Inhalt 'favorites: Mapped[list["Favorite"]] = relationship(back_populates="recipe", cascade="al...'.
73. Diese Zeile definiert den Inhalt 'images: Mapped[list["RecipeImage"]] = relationship('.
74. Diese Zeile definiert den Inhalt 'back_populates="recipe",'.
75. Diese Zeile definiert den Inhalt 'cascade="all, delete-orphan",'.
76. Diese Zeile definiert den Inhalt 'order_by="RecipeImage.created_at",'.
77. Diese Zeile definiert den Inhalt ')'.
78. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
79. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
80. Diese Zeile definiert den Inhalt 'class Ingredient(Base):'.
81. Diese Zeile definiert den Inhalt '__tablename__ = "ingredients"'.
82. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
83. Diese Zeile definiert den Inhalt 'id: Mapped[int] = mapped_column(Integer, primary_key=True)'.
84. Diese Zeile definiert den Inhalt 'name: Mapped[str] = mapped_column(String(200), unique=True, nullable=False, index=True)'.
85. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
86. Diese Zeile definiert den Inhalt 'recipe_links: Mapped[list["RecipeIngredient"]] = relationship('.
87. Diese Zeile definiert den Inhalt 'back_populates="ingredient",'.
88. Diese Zeile definiert den Inhalt 'cascade="all, delete-orphan",'.
89. Diese Zeile definiert den Inhalt ')'.
90. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
91. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
92. Diese Zeile definiert den Inhalt 'class RecipeIngredient(Base):'.
93. Diese Zeile definiert den Inhalt '__tablename__ = "recipe_ingredients"'.
94. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
95. Diese Zeile definiert den Inhalt 'recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id", ondelete="CASCADE"), pr...'.
96. Diese Zeile definiert den Inhalt 'ingredient_id: Mapped[int] = mapped_column(ForeignKey("ingredients.id", ondelete="CASCA...'.
97. Diese Zeile definiert den Inhalt 'quantity_text: Mapped[str] = mapped_column(String(120), default="", nullable=False)'.
98. Diese Zeile definiert den Inhalt 'grams: Mapped[int | None] = mapped_column(Integer, nullable=True)'.
99. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
100. Diese Zeile definiert den Inhalt 'recipe: Mapped["Recipe"] = relationship(back_populates="recipe_ingredients")'.
101. Diese Zeile definiert den Inhalt 'ingredient: Mapped["Ingredient"] = relationship(back_populates="recipe_links")'.
102. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
103. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
104. Diese Zeile definiert den Inhalt 'class Review(Base):'.
105. Diese Zeile definiert den Inhalt '__tablename__ = "reviews"'.
106. Diese Zeile definiert den Inhalt '__table_args__ = (UniqueConstraint("user_id", "recipe_id", name="uq_reviews_user_recipe...'.
107. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
108. Diese Zeile definiert den Inhalt 'id: Mapped[int] = mapped_column(Integer, primary_key=True)'.
109. Diese Zeile definiert den Inhalt 'recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id", ondelete="CASCADE"), nu...'.
110. Diese Zeile definiert den Inhalt 'user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullab...'.
111. Diese Zeile definiert den Inhalt 'rating: Mapped[int] = mapped_column(Integer, nullable=False)'.
112. Diese Zeile definiert den Inhalt 'comment: Mapped[str] = mapped_column(Text, default="", nullable=False)'.
113. Diese Zeile definiert den Inhalt 'created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, ...'.
114. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
115. Diese Zeile definiert den Inhalt 'recipe: Mapped["Recipe"] = relationship(back_populates="reviews")'.
116. Diese Zeile definiert den Inhalt 'user: Mapped["User"] = relationship(back_populates="reviews")'.
117. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
118. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
119. Diese Zeile definiert den Inhalt 'class Favorite(Base):'.
120. Diese Zeile definiert den Inhalt '__tablename__ = "favorites"'.
121. Diese Zeile definiert den Inhalt '__table_args__ = (UniqueConstraint("user_id", "recipe_id", name="uq_favorites_user_reci...'.
122. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
123. Diese Zeile definiert den Inhalt 'user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primar...'.
124. Diese Zeile definiert den Inhalt 'recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id", ondelete="CASCADE"), pr...'.
125. Diese Zeile definiert den Inhalt 'created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, ...'.
126. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
127. Diese Zeile definiert den Inhalt 'user: Mapped["User"] = relationship(back_populates="favorites")'.
128. Diese Zeile definiert den Inhalt 'recipe: Mapped["Recipe"] = relationship(back_populates="favorites")'.
129. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
130. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
131. Diese Zeile definiert den Inhalt 'class RecipeImage(Base):'.
132. Diese Zeile definiert den Inhalt '__tablename__ = "recipe_images"'.
133. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
134. Diese Zeile definiert den Inhalt 'id: Mapped[int] = mapped_column(Integer, primary_key=True)'.
135. Diese Zeile definiert den Inhalt 'recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id", ondelete="CASCADE"), nu...'.
136. Diese Zeile definiert den Inhalt 'filename: Mapped[str] = mapped_column(String(255), nullable=False)'.
137. Diese Zeile definiert den Inhalt 'content_type: Mapped[str] = mapped_column(String(50), nullable=False)'.
138. Diese Zeile definiert den Inhalt 'data: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)'.
139. Diese Zeile definiert den Inhalt 'is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)'.
140. Diese Zeile definiert den Inhalt 'created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, ...'.
141. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
142. Diese Zeile definiert den Inhalt 'recipe: Mapped["Recipe"] = relationship(back_populates="images")'.
143. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
144. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
145. Diese Zeile definiert den Inhalt 'class RecipeSubmission(Base):'.
146. Diese Zeile definiert den Inhalt '__tablename__ = "recipe_submissions"'.
147. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
148. Diese Zeile definiert den Inhalt 'id: Mapped[int] = mapped_column(Integer, primary_key=True)'.
149. Diese Zeile definiert den Inhalt 'submitter_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="...'.
150. Diese Zeile definiert den Inhalt 'submitter_email: Mapped[str | None] = mapped_column(String(255), nullable=True)'.
151. Diese Zeile definiert den Inhalt 'title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)'.
152. Diese Zeile definiert den Inhalt 'description: Mapped[str] = mapped_column(Text, nullable=False)'.
153. Diese Zeile definiert den Inhalt 'category: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)'.
154. Diese Zeile definiert den Inhalt 'difficulty: Mapped[str] = mapped_column(String(30), nullable=False, default="medium", i...'.
155. Diese Zeile definiert den Inhalt 'prep_time_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)'.
156. Diese Zeile definiert den Inhalt 'servings_text: Mapped[str | None] = mapped_column(String(120), nullable=True)'.
157. Diese Zeile definiert den Inhalt 'instructions: Mapped[str] = mapped_column(Text, nullable=False)'.
158. Diese Zeile definiert den Inhalt 'status: Mapped[str] = mapped_column(SUBMISSION_STATUS_ENUM, nullable=False, default="pe...'.
159. Diese Zeile definiert den Inhalt 'admin_note: Mapped[str | None] = mapped_column(Text, nullable=True)'.
160. Diese Zeile definiert den Inhalt 'reviewed_by_admin_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelet...'.
161. Diese Zeile definiert den Inhalt 'reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=...'.
162. Diese Zeile definiert den Inhalt 'created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, ...'.
163. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
164. Diese Zeile definiert den Inhalt 'submitter_user: Mapped["User"] = relationship('.
165. Diese Zeile definiert den Inhalt 'back_populates="submissions",'.
166. Diese Zeile definiert den Inhalt 'foreign_keys=[submitter_user_id],'.
167. Diese Zeile definiert den Inhalt ')'.
168. Diese Zeile definiert den Inhalt 'reviewed_by_admin: Mapped["User"] = relationship('.
169. Diese Zeile definiert den Inhalt 'back_populates="reviewed_submissions",'.
170. Diese Zeile definiert den Inhalt 'foreign_keys=[reviewed_by_admin_id],'.
171. Diese Zeile definiert den Inhalt ')'.
172. Diese Zeile definiert den Inhalt 'ingredients: Mapped[list["SubmissionIngredient"]] = relationship('.
173. Diese Zeile definiert den Inhalt 'back_populates="submission",'.
174. Diese Zeile definiert den Inhalt 'cascade="all, delete-orphan",'.
175. Diese Zeile definiert den Inhalt 'order_by="SubmissionIngredient.id",'.
176. Diese Zeile definiert den Inhalt ')'.
177. Diese Zeile definiert den Inhalt 'images: Mapped[list["SubmissionImage"]] = relationship('.
178. Diese Zeile definiert den Inhalt 'back_populates="submission",'.
179. Diese Zeile definiert den Inhalt 'cascade="all, delete-orphan",'.
180. Diese Zeile definiert den Inhalt 'order_by="SubmissionImage.created_at",'.
181. Diese Zeile definiert den Inhalt ')'.
182. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
183. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
184. Diese Zeile definiert den Inhalt 'class SubmissionIngredient(Base):'.
185. Diese Zeile definiert den Inhalt '__tablename__ = "submission_ingredients"'.
186. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
187. Diese Zeile definiert den Inhalt 'id: Mapped[int] = mapped_column(Integer, primary_key=True)'.
188. Diese Zeile definiert den Inhalt 'submission_id: Mapped[int] = mapped_column(ForeignKey("recipe_submissions.id", ondelete...'.
189. Diese Zeile definiert den Inhalt 'ingredient_name: Mapped[str] = mapped_column(String(200), nullable=False)'.
190. Diese Zeile definiert den Inhalt 'quantity_text: Mapped[str] = mapped_column(String(120), nullable=False, default="")'.
191. Diese Zeile definiert den Inhalt 'grams: Mapped[int | None] = mapped_column(Integer, nullable=True)'.
192. Diese Zeile definiert den Inhalt 'ingredient_name_normalized: Mapped[str | None] = mapped_column(String(200), nullable=Tr...'.
193. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
194. Diese Zeile definiert den Inhalt 'submission: Mapped["RecipeSubmission"] = relationship(back_populates="ingredients")'.
195. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
196. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
197. Diese Zeile definiert den Inhalt 'class SubmissionImage(Base):'.
198. Diese Zeile definiert den Inhalt '__tablename__ = "submission_images"'.
199. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
200. Diese Zeile definiert den Inhalt 'id: Mapped[int] = mapped_column(Integer, primary_key=True)'.
201. Diese Zeile definiert den Inhalt 'submission_id: Mapped[int] = mapped_column(ForeignKey("recipe_submissions.id", ondelete...'.
202. Diese Zeile definiert den Inhalt 'filename: Mapped[str] = mapped_column(String(255), nullable=False)'.
203. Diese Zeile definiert den Inhalt 'content_type: Mapped[str] = mapped_column(String(50), nullable=False)'.
204. Diese Zeile definiert den Inhalt 'data: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)'.
205. Diese Zeile definiert den Inhalt 'is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)'.
206. Diese Zeile definiert den Inhalt 'created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, ...'.
207. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
208. Diese Zeile definiert den Inhalt 'submission: Mapped["RecipeSubmission"] = relationship(back_populates="images")'.
209. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
210. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
211. Diese Zeile definiert den Inhalt 'class AppMeta(Base):'.
212. Diese Zeile definiert den Inhalt '__tablename__ = "app_meta"'.
213. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
214. Diese Zeile definiert den Inhalt 'key: Mapped[str] = mapped_column(String(120), primary_key=True)'.
215. Diese Zeile definiert den Inhalt 'value: Mapped[str] = mapped_column(Text, nullable=False)'.

## alembic/versions/20260303_0006_add_recipe_is_published.py
```python
"""add recipe is_published flag for moderation-safe visibility

Revision ID: 20260303_0006
Revises: 20260303_0005
Create Date: 2026-03-03 19:05:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20260303_0006"
down_revision: Union[str, None] = "20260303_0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "recipes",
        sa.Column("is_published", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.create_index("ix_recipes_is_published", "recipes", ["is_published"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_recipes_is_published", table_name="recipes")
    op.drop_column("recipes", "is_published")
```
ZEILEN-ERKL?RUNG
1. Diese Zeile definiert den Inhalt '"""add recipe is_published flag for moderation-safe visibility'.
2. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
3. Diese Zeile definiert den Inhalt 'Revision ID: 20260303_0006'.
4. Diese Zeile definiert den Inhalt 'Revises: 20260303_0005'.
5. Diese Zeile definiert den Inhalt 'Create Date: 2026-03-03 19:05:00'.
6. Diese Zeile definiert den Inhalt '"""'.
7. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
8. Diese Zeile definiert den Inhalt 'from typing import Sequence, Union'.
9. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
10. Diese Zeile definiert den Inhalt 'from alembic import op'.
11. Diese Zeile definiert den Inhalt 'import sqlalchemy as sa'.
12. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
13. Diese Zeile definiert den Inhalt '# revision identifiers, used by Alembic.'.
14. Diese Zeile definiert den Inhalt 'revision: str = "20260303_0006"'.
15. Diese Zeile definiert den Inhalt 'down_revision: Union[str, None] = "20260303_0005"'.
16. Diese Zeile definiert den Inhalt 'branch_labels: Union[str, Sequence[str], None] = None'.
17. Diese Zeile definiert den Inhalt 'depends_on: Union[str, Sequence[str], None] = None'.
18. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
19. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
20. Diese Zeile definiert den Inhalt 'def upgrade() -> None:'.
21. Diese Zeile definiert den Inhalt 'op.add_column('.
22. Diese Zeile definiert den Inhalt '"recipes",'.
23. Diese Zeile definiert den Inhalt 'sa.Column("is_published", sa.Boolean(), nullable=False, server_default=sa.true()),'.
24. Diese Zeile definiert den Inhalt ')'.
25. Diese Zeile definiert den Inhalt 'op.create_index("ix_recipes_is_published", "recipes", ["is_published"], unique=False)'.
26. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
27. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
28. Diese Zeile definiert den Inhalt 'def downgrade() -> None:'.
29. Diese Zeile definiert den Inhalt 'op.drop_index("ix_recipes_is_published", table_name="recipes")'.
30. Diese Zeile definiert den Inhalt 'op.drop_column("recipes", "is_published")'.

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
from app.models import (
    AppMeta,
    Ingredient,
    Recipe,
    RecipeImage,
    RecipeIngredient,
    RecipeSubmission,
    SubmissionImage,
    SubmissionIngredient,
    User,
)

settings = get_settings()

ALLOWED_DIFFICULTIES = {"easy", "medium", "hard"}
DEFAULT_CATEGORY = "Unkategorisiert"
IMPORT_MODE = Literal["insert_only", "update_existing"]
SUBMISSION_STATUS = Literal["pending", "approved", "rejected"]


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


def build_category_index(db: Session, only_published: bool = False) -> dict[str, list[str]]:
    stmt = select(Recipe.category)
    if only_published:
        stmt = stmt.where(Recipe.is_published.is_(True))
    raw_categories = db.scalars(stmt).all()
    variants: dict[str, set[str]] = {}
    for raw in raw_categories:
        raw_value = str(raw or "")
        normalized = normalize_category(raw_value, allow_empty=True)
        key = normalized or DEFAULT_CATEGORY
        variants.setdefault(key, set()).update({raw_value, key})
    return {key: sorted(values) for key, values in variants.items()}


def get_distinct_categories(db: Session, only_published: bool = False) -> list[str]:
    categories = sorted(build_category_index(db, only_published=only_published).keys(), key=str.casefold)
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


def replace_submission_ingredients(
    db: Session,
    submission: RecipeSubmission,
    ingredient_entries: list[dict[str, Any]],
) -> None:
    submission.ingredients.clear()
    merged_entries: dict[str, dict[str, Any]] = {}
    for entry in ingredient_entries:
        name = str(entry.get("name") or "").strip()
        if not name:
            continue
        key = normalize_ingredient_name(name)
        quantity_text = str(entry.get("quantity_text") or "").strip()[:120]
        grams = parse_optional_int(entry.get("grams"))
        if key not in merged_entries:
            merged_entries[key] = {"name": name[:200], "quantity_text": quantity_text, "grams": grams}
            continue
        current = merged_entries[key]
        if quantity_text:
            if current["quantity_text"]:
                current["quantity_text"] = f"{current['quantity_text']} | {quantity_text}"[:120]
            else:
                current["quantity_text"] = quantity_text
        if current["grams"] is None and grams is not None:
            current["grams"] = grams
    for merged in merged_entries.values():
        db.add(
            SubmissionIngredient(
                submission=submission,
                ingredient_name=merged["name"],
                quantity_text=merged["quantity_text"],
                grams=merged["grams"],
                ingredient_name_normalized=normalize_ingredient_name(merged["name"]),
            )
        )


def build_submission_ingredients_text(ingredients: list[SubmissionIngredient]) -> str:
    lines: list[str] = []
    for ingredient in ingredients:
        name = ingredient.ingredient_name.strip()
        if not name:
            continue
        if ingredient.grams is not None:
            lines.append(f"{name}|{ingredient.quantity_text}|{ingredient.grams}")
            continue
        if ingredient.quantity_text:
            lines.append(f"{name}|{ingredient.quantity_text}")
            continue
        lines.append(name)
    return "\n".join(lines)


def get_submission_primary_image(submission: RecipeSubmission) -> SubmissionImage | None:
    for image in submission.images:
        if image.is_primary:
            return image
    return submission.images[0] if submission.images else None


def publish_submission_as_recipe(db: Session, submission: RecipeSubmission, admin_id: int) -> Recipe:
    source_uuid = f"submission:{submission.id}"
    existing = db.scalar(select(Recipe).where(Recipe.source_uuid == source_uuid))
    if existing:
        raise ValueError("Submission has already been published.")
    recipe = Recipe(
        title=submission.title.strip()[:255],
        description=submission.description.strip(),
        instructions=submission.instructions.strip(),
        category=normalize_category(submission.category),
        prep_time_minutes=max(int(submission.prep_time_minutes or 30), 1),
        difficulty=sanitize_difficulty(submission.difficulty),
        creator_id=admin_id,
        source="submission",
        source_uuid=source_uuid,
        source_url=None,
        source_image_url=None,
        title_image_url=None,
        servings_text=(submission.servings_text or "").strip()[:120] or None,
        total_time_minutes=None,
        is_published=True,
    )
    db.add(recipe)
    db.flush()
    for item in submission.ingredients:
        ingredient_name = item.ingredient_name.strip()
        if not ingredient_name:
            continue
        ingredient = get_or_create_ingredient(db, ingredient_name)
        db.add(
            RecipeIngredient(
                recipe_id=recipe.id,
                ingredient_id=ingredient.id,
                quantity_text=(item.quantity_text or "").strip()[:120],
                grams=item.grams,
            )
        )
    any_primary = False
    for image in submission.images:
        db.add(
            RecipeImage(
                recipe_id=recipe.id,
                filename=image.filename,
                content_type=image.content_type,
                data=image.data,
                is_primary=image.is_primary,
            )
        )
        if image.is_primary:
            any_primary = True
    if submission.images and not any_primary:
        first_recipe_image = db.scalar(
            select(RecipeImage).where(RecipeImage.recipe_id == recipe.id).order_by(RecipeImage.id.asc())
        )
        if first_recipe_image:
            first_recipe_image.is_primary = True
    return recipe


def get_submission_status_stats(db: Session) -> dict[str, int]:
    rows = db.execute(
        select(RecipeSubmission.status, func.count(RecipeSubmission.id)).group_by(RecipeSubmission.status)
    ).all()
    base = {"pending": 0, "approved": 0, "rejected": 0}
    for status, count in rows:
        base[str(status)] = int(count)
    return base


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
                    is_published=True,
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
ZEILEN-ERKL?RUNG
1. Diese Zeile definiert den Inhalt 'import csv'.
2. Diese Zeile definiert den Inhalt 'import html'.
3. Diese Zeile definiert den Inhalt 'import io'.
4. Diese Zeile definiert den Inhalt 'import json'.
5. Diese Zeile definiert den Inhalt 'import re'.
6. Diese Zeile definiert den Inhalt 'from collections import Counter'.
7. Diese Zeile definiert den Inhalt 'from dataclasses import dataclass, field'.
8. Diese Zeile definiert den Inhalt 'from functools import lru_cache'.
9. Diese Zeile definiert den Inhalt 'from pathlib import Path'.
10. Diese Zeile definiert den Inhalt 'from typing import Any, Literal'.
11. Diese Zeile definiert den Inhalt 'from urllib.parse import unquote, urlparse'.
12. Diese Zeile definiert den Inhalt 'from urllib.request import Request, urlopen'.
13. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
14. Diese Zeile definiert den Inhalt 'from PIL import Image, UnidentifiedImageError'.
15. Diese Zeile definiert den Inhalt 'from reportlab.lib.pagesizes import A4'.
16. Diese Zeile definiert den Inhalt 'from reportlab.lib.utils import ImageReader'.
17. Diese Zeile definiert den Inhalt 'from reportlab.pdfgen import canvas'.
18. Diese Zeile definiert den Inhalt 'from sqlalchemy import func, select'.
19. Diese Zeile definiert den Inhalt 'from sqlalchemy.orm import Session'.
20. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
21. Diese Zeile definiert den Inhalt 'from app.config import get_settings'.
22. Diese Zeile definiert den Inhalt 'from app.models import ('.
23. Diese Zeile definiert den Inhalt 'AppMeta,'.
24. Diese Zeile definiert den Inhalt 'Ingredient,'.
25. Diese Zeile definiert den Inhalt 'Recipe,'.
26. Diese Zeile definiert den Inhalt 'RecipeImage,'.
27. Diese Zeile definiert den Inhalt 'RecipeIngredient,'.
28. Diese Zeile definiert den Inhalt 'RecipeSubmission,'.
29. Diese Zeile definiert den Inhalt 'SubmissionImage,'.
30. Diese Zeile definiert den Inhalt 'SubmissionIngredient,'.
31. Diese Zeile definiert den Inhalt 'User,'.
32. Diese Zeile definiert den Inhalt ')'.
33. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
34. Diese Zeile definiert den Inhalt 'settings = get_settings()'.
35. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
36. Diese Zeile definiert den Inhalt 'ALLOWED_DIFFICULTIES = {"easy", "medium", "hard"}'.
37. Diese Zeile definiert den Inhalt 'DEFAULT_CATEGORY = "Unkategorisiert"'.
38. Diese Zeile definiert den Inhalt 'IMPORT_MODE = Literal["insert_only", "update_existing"]'.
39. Diese Zeile definiert den Inhalt 'SUBMISSION_STATUS = Literal["pending", "approved", "rejected"]'.
40. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
41. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
42. Diese Zeile definiert den Inhalt '@dataclass'.
43. Diese Zeile definiert den Inhalt 'class CSVImportReport:'.
44. Diese Zeile definiert den Inhalt 'inserted: int = 0'.
45. Diese Zeile definiert den Inhalt 'updated: int = 0'.
46. Diese Zeile definiert den Inhalt 'skipped: int = 0'.
47. Diese Zeile definiert den Inhalt 'errors: list[str] = field(default_factory=list)'.
48. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
49. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
50. Diese Zeile definiert den Inhalt 'def parse_ingredient_text(raw: str) -> list[dict[str, Any]]:'.
51. Diese Zeile definiert den Inhalt 'items: list[dict[str, Any]] = []'.
52. Diese Zeile definiert den Inhalt 'for line in raw.splitlines():'.
53. Diese Zeile definiert den Inhalt 'normalized = line.strip()'.
54. Diese Zeile definiert den Inhalt 'if not normalized:'.
55. Diese Zeile definiert den Inhalt 'continue'.
56. Diese Zeile definiert den Inhalt 'parts = [part.strip() for part in normalized.split("|")]'.
57. Diese Zeile definiert den Inhalt 'if len(parts) == 1:'.
58. Diese Zeile definiert den Inhalt 'items.append({"name": parts[0], "quantity_text": "", "grams": None})'.
59. Diese Zeile definiert den Inhalt 'continue'.
60. Diese Zeile definiert den Inhalt 'if len(parts) == 2:'.
61. Diese Zeile definiert den Inhalt 'items.append({"name": parts[0], "quantity_text": parts[1], "grams": None})'.
62. Diese Zeile definiert den Inhalt 'continue'.
63. Diese Zeile definiert den Inhalt 'grams = parse_optional_int(parts[2])'.
64. Diese Zeile definiert den Inhalt 'items.append({"name": parts[0], "quantity_text": parts[1], "grams": grams})'.
65. Diese Zeile definiert den Inhalt 'return items'.
66. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
67. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
68. Diese Zeile definiert den Inhalt 'def parse_optional_int(value: Any) -> int | None:'.
69. Diese Zeile definiert den Inhalt 'if value is None:'.
70. Diese Zeile definiert den Inhalt 'return None'.
71. Diese Zeile definiert den Inhalt 'if isinstance(value, int):'.
72. Diese Zeile definiert den Inhalt 'return value'.
73. Diese Zeile definiert den Inhalt 'text = str(value).strip()'.
74. Diese Zeile definiert den Inhalt 'if not text:'.
75. Diese Zeile definiert den Inhalt 'return None'.
76. Diese Zeile definiert den Inhalt 'match = re.search(r"\d+", text)'.
77. Diese Zeile definiert den Inhalt 'return int(match.group(0)) if match else None'.
78. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
79. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
80. Diese Zeile definiert den Inhalt 'def sanitize_difficulty(value: str) -> str:'.
81. Diese Zeile definiert den Inhalt 'normalized = value.strip().lower()'.
82. Diese Zeile definiert den Inhalt 'german_map = {"leicht": "easy", "mittel": "medium", "schwer": "hard"}'.
83. Diese Zeile definiert den Inhalt 'normalized = german_map.get(normalized, normalized)'.
84. Diese Zeile definiert den Inhalt 'if normalized not in ALLOWED_DIFFICULTIES:'.
85. Diese Zeile definiert den Inhalt 'return "medium"'.
86. Diese Zeile definiert den Inhalt 'return normalized'.
87. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
88. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
89. Diese Zeile definiert den Inhalt 'def normalize_category(value: Any, fallback: str = DEFAULT_CATEGORY, allow_empty: bool ...'.
90. Diese Zeile definiert den Inhalt 'text = str(value or "").replace("_", " ")'.
91. Diese Zeile definiert den Inhalt 'text = re.sub(r"\s+", " ", text).strip()'.
92. Diese Zeile definiert den Inhalt 'if not text:'.
93. Diese Zeile definiert den Inhalt 'return "" if allow_empty else fallback'.
94. Diese Zeile definiert den Inhalt 'if text.casefold() in {"general", "allgemein", "uncategorized", "unkategorisiert"}:'.
95. Diese Zeile definiert den Inhalt 'return fallback'.
96. Diese Zeile definiert den Inhalt 'return text.title()[:120]'.
97. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
98. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
99. Diese Zeile definiert den Inhalt 'def build_category_index(db: Session, only_published: bool = False) -> dict[str, list[s...'.
100. Diese Zeile definiert den Inhalt 'stmt = select(Recipe.category)'.
101. Diese Zeile definiert den Inhalt 'if only_published:'.
102. Diese Zeile definiert den Inhalt 'stmt = stmt.where(Recipe.is_published.is_(True))'.
103. Diese Zeile definiert den Inhalt 'raw_categories = db.scalars(stmt).all()'.
104. Diese Zeile definiert den Inhalt 'variants: dict[str, set[str]] = {}'.
105. Diese Zeile definiert den Inhalt 'for raw in raw_categories:'.
106. Diese Zeile definiert den Inhalt 'raw_value = str(raw or "")'.
107. Diese Zeile definiert den Inhalt 'normalized = normalize_category(raw_value, allow_empty=True)'.
108. Diese Zeile definiert den Inhalt 'key = normalized or DEFAULT_CATEGORY'.
109. Diese Zeile definiert den Inhalt 'variants.setdefault(key, set()).update({raw_value, key})'.
110. Diese Zeile definiert den Inhalt 'return {key: sorted(values) for key, values in variants.items()}'.
111. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
112. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
113. Diese Zeile definiert den Inhalt 'def get_distinct_categories(db: Session, only_published: bool = False) -> list[str]:'.
114. Diese Zeile definiert den Inhalt 'categories = sorted(build_category_index(db, only_published=only_published).keys(), key...'.
115. Diese Zeile definiert den Inhalt 'if not categories:'.
116. Diese Zeile definiert den Inhalt 'return [DEFAULT_CATEGORY]'.
117. Diese Zeile definiert den Inhalt 'return categories'.
118. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
119. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
120. Diese Zeile definiert den Inhalt 'def get_category_stats(db: Session, limit: int = 10) -> tuple[int, list[tuple[str, int]]]:'.
121. Diese Zeile definiert den Inhalt 'raw_categories = db.scalars(select(Recipe.category)).all()'.
122. Diese Zeile definiert den Inhalt 'counter = Counter(normalize_category(value) for value in raw_categories)'.
123. Diese Zeile definiert den Inhalt 'if not counter:'.
124. Diese Zeile definiert den Inhalt 'counter = Counter({DEFAULT_CATEGORY: 0})'.
125. Diese Zeile definiert den Inhalt 'top_categories = sorted(counter.items(), key=lambda item: (-item[1], item[0].casefold()...'.
126. Diese Zeile definiert den Inhalt 'return len(counter), top_categories'.
127. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
128. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
129. Diese Zeile definiert den Inhalt 'def normalize_ingredient_name(name: str) -> str:'.
130. Diese Zeile definiert den Inhalt 'return re.sub(r"\s+", " ", name.strip().lower())'.
131. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
132. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
133. Diese Zeile definiert den Inhalt 'def parse_list_like(raw_value: Any) -> list[str]:'.
134. Diese Zeile definiert den Inhalt 'if isinstance(raw_value, list):'.
135. Diese Zeile definiert den Inhalt 'return [str(item).strip() for item in raw_value if str(item).strip()]'.
136. Diese Zeile definiert den Inhalt 'if raw_value is None:'.
137. Diese Zeile definiert den Inhalt 'return []'.
138. Diese Zeile definiert den Inhalt 'value = str(raw_value).strip()'.
139. Diese Zeile definiert den Inhalt 'if not value:'.
140. Diese Zeile definiert den Inhalt 'return []'.
141. Diese Zeile definiert den Inhalt 'if value.startswith("[") and value.endswith("]"):'.
142. Diese Zeile definiert den Inhalt 'try:'.
143. Diese Zeile definiert den Inhalt 'loaded = json.loads(value)'.
144. Diese Zeile definiert den Inhalt 'except json.JSONDecodeError:'.
145. Diese Zeile definiert den Inhalt 'loaded = None'.
146. Diese Zeile definiert den Inhalt 'if isinstance(loaded, list):'.
147. Diese Zeile definiert den Inhalt 'return [str(item).strip() for item in loaded if str(item).strip()]'.
148. Diese Zeile definiert den Inhalt 'separator = "\n" if "\n" in value else ","'.
149. Diese Zeile definiert den Inhalt 'return [item.strip().strip('"') for item in value.split(separator) if item.strip()]'.
150. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
151. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
152. Diese Zeile definiert den Inhalt 'def parse_text_block(raw_value: Any) -> str:'.
153. Diese Zeile definiert den Inhalt 'parts = parse_list_like(raw_value)'.
154. Diese Zeile definiert den Inhalt 'if parts:'.
155. Diese Zeile definiert den Inhalt 'return "\n".join(parts)'.
156. Diese Zeile definiert den Inhalt 'return str(raw_value or "").strip()'.
157. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
158. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
159. Diese Zeile definiert den Inhalt 'def get_or_create_ingredient(db: Session, name: str) -> Ingredient:'.
160. Diese Zeile definiert den Inhalt 'normalized = normalize_ingredient_name(name)'.
161. Diese Zeile definiert den Inhalt 'ingredient = db.scalar(select(Ingredient).where(Ingredient.name == normalized))'.
162. Diese Zeile definiert den Inhalt 'if ingredient:'.
163. Diese Zeile definiert den Inhalt 'return ingredient'.
164. Diese Zeile definiert den Inhalt 'ingredient = Ingredient(name=normalized)'.
165. Diese Zeile definiert den Inhalt 'db.add(ingredient)'.
166. Diese Zeile definiert den Inhalt 'db.flush()'.
167. Diese Zeile definiert den Inhalt 'return ingredient'.
168. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
169. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
170. Diese Zeile definiert den Inhalt 'def replace_recipe_ingredients(db: Session, recipe: Recipe, ingredient_entries: list[di...'.
171. Diese Zeile definiert den Inhalt 'recipe.recipe_ingredients.clear()'.
172. Diese Zeile definiert den Inhalt 'merged_entries: dict[str, dict[str, Any]] = {}'.
173. Diese Zeile definiert den Inhalt 'for entry in ingredient_entries:'.
174. Diese Zeile definiert den Inhalt 'name = str(entry.get("name") or "").strip()'.
175. Diese Zeile definiert den Inhalt 'if not name:'.
176. Diese Zeile definiert den Inhalt 'continue'.
177. Diese Zeile definiert den Inhalt 'key = normalize_ingredient_name(name)'.
178. Diese Zeile definiert den Inhalt 'quantity_text = str(entry.get("quantity_text") or "").strip()'.
179. Diese Zeile definiert den Inhalt 'grams = parse_optional_int(entry.get("grams"))'.
180. Diese Zeile definiert den Inhalt 'if key not in merged_entries:'.
181. Diese Zeile definiert den Inhalt 'merged_entries[key] = {"name": name, "quantity_text": quantity_text, "grams": grams}'.
182. Diese Zeile definiert den Inhalt 'continue'.
183. Diese Zeile definiert den Inhalt 'current = merged_entries[key]'.
184. Diese Zeile definiert den Inhalt 'if quantity_text:'.
185. Diese Zeile definiert den Inhalt 'if current["quantity_text"]:'.
186. Diese Zeile definiert den Inhalt 'current["quantity_text"] = f"{current['quantity_text']} | {quantity_text}"'.
187. Diese Zeile definiert den Inhalt 'else:'.
188. Diese Zeile definiert den Inhalt 'current["quantity_text"] = quantity_text'.
189. Diese Zeile definiert den Inhalt 'if current["grams"] is None and grams is not None:'.
190. Diese Zeile definiert den Inhalt 'current["grams"] = grams'.
191. Diese Zeile definiert den Inhalt 'for merged in merged_entries.values():'.
192. Diese Zeile definiert den Inhalt 'ingredient = get_or_create_ingredient(db, merged["name"])'.
193. Diese Zeile definiert den Inhalt 'db.add('.
194. Diese Zeile definiert den Inhalt 'RecipeIngredient('.
195. Diese Zeile definiert den Inhalt 'recipe=recipe,'.
196. Diese Zeile definiert den Inhalt 'ingredient=ingredient,'.
197. Diese Zeile definiert den Inhalt 'quantity_text=merged["quantity_text"],'.
198. Diese Zeile definiert den Inhalt 'grams=merged["grams"],'.
199. Diese Zeile definiert den Inhalt ')'.
200. Diese Zeile definiert den Inhalt ')'.
201. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
202. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
203. Diese Zeile definiert den Inhalt 'def replace_submission_ingredients('.
204. Diese Zeile definiert den Inhalt 'db: Session,'.
205. Diese Zeile definiert den Inhalt 'submission: RecipeSubmission,'.
206. Diese Zeile definiert den Inhalt 'ingredient_entries: list[dict[str, Any]],'.
207. Diese Zeile definiert den Inhalt ') -> None:'.
208. Diese Zeile definiert den Inhalt 'submission.ingredients.clear()'.
209. Diese Zeile definiert den Inhalt 'merged_entries: dict[str, dict[str, Any]] = {}'.
210. Diese Zeile definiert den Inhalt 'for entry in ingredient_entries:'.
211. Diese Zeile definiert den Inhalt 'name = str(entry.get("name") or "").strip()'.
212. Diese Zeile definiert den Inhalt 'if not name:'.
213. Diese Zeile definiert den Inhalt 'continue'.
214. Diese Zeile definiert den Inhalt 'key = normalize_ingredient_name(name)'.
215. Diese Zeile definiert den Inhalt 'quantity_text = str(entry.get("quantity_text") or "").strip()[:120]'.
216. Diese Zeile definiert den Inhalt 'grams = parse_optional_int(entry.get("grams"))'.
217. Diese Zeile definiert den Inhalt 'if key not in merged_entries:'.
218. Diese Zeile definiert den Inhalt 'merged_entries[key] = {"name": name[:200], "quantity_text": quantity_text, "grams": grams}'.
219. Diese Zeile definiert den Inhalt 'continue'.
220. Diese Zeile definiert den Inhalt 'current = merged_entries[key]'.
221. Diese Zeile definiert den Inhalt 'if quantity_text:'.
222. Diese Zeile definiert den Inhalt 'if current["quantity_text"]:'.
223. Diese Zeile definiert den Inhalt 'current["quantity_text"] = f"{current['quantity_text']} | {quantity_text}"[:120]'.
224. Diese Zeile definiert den Inhalt 'else:'.
225. Diese Zeile definiert den Inhalt 'current["quantity_text"] = quantity_text'.
226. Diese Zeile definiert den Inhalt 'if current["grams"] is None and grams is not None:'.
227. Diese Zeile definiert den Inhalt 'current["grams"] = grams'.
228. Diese Zeile definiert den Inhalt 'for merged in merged_entries.values():'.
229. Diese Zeile definiert den Inhalt 'db.add('.
230. Diese Zeile definiert den Inhalt 'SubmissionIngredient('.
231. Diese Zeile definiert den Inhalt 'submission=submission,'.
232. Diese Zeile definiert den Inhalt 'ingredient_name=merged["name"],'.
233. Diese Zeile definiert den Inhalt 'quantity_text=merged["quantity_text"],'.
234. Diese Zeile definiert den Inhalt 'grams=merged["grams"],'.
235. Diese Zeile definiert den Inhalt 'ingredient_name_normalized=normalize_ingredient_name(merged["name"]),'.
236. Diese Zeile definiert den Inhalt ')'.
237. Diese Zeile definiert den Inhalt ')'.
238. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
239. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
240. Diese Zeile definiert den Inhalt 'def build_submission_ingredients_text(ingredients: list[SubmissionIngredient]) -> str:'.
241. Diese Zeile definiert den Inhalt 'lines: list[str] = []'.
242. Diese Zeile definiert den Inhalt 'for ingredient in ingredients:'.
243. Diese Zeile definiert den Inhalt 'name = ingredient.ingredient_name.strip()'.
244. Diese Zeile definiert den Inhalt 'if not name:'.
245. Diese Zeile definiert den Inhalt 'continue'.
246. Diese Zeile definiert den Inhalt 'if ingredient.grams is not None:'.
247. Diese Zeile definiert den Inhalt 'lines.append(f"{name}|{ingredient.quantity_text}|{ingredient.grams}")'.
248. Diese Zeile definiert den Inhalt 'continue'.
249. Diese Zeile definiert den Inhalt 'if ingredient.quantity_text:'.
250. Diese Zeile definiert den Inhalt 'lines.append(f"{name}|{ingredient.quantity_text}")'.
251. Diese Zeile definiert den Inhalt 'continue'.
252. Diese Zeile definiert den Inhalt 'lines.append(name)'.
253. Diese Zeile definiert den Inhalt 'return "\n".join(lines)'.
254. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
255. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
256. Diese Zeile definiert den Inhalt 'def get_submission_primary_image(submission: RecipeSubmission) -> SubmissionImage | None:'.
257. Diese Zeile definiert den Inhalt 'for image in submission.images:'.
258. Diese Zeile definiert den Inhalt 'if image.is_primary:'.
259. Diese Zeile definiert den Inhalt 'return image'.
260. Diese Zeile definiert den Inhalt 'return submission.images[0] if submission.images else None'.
261. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
262. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
263. Diese Zeile definiert den Inhalt 'def publish_submission_as_recipe(db: Session, submission: RecipeSubmission, admin_id: i...'.
264. Diese Zeile definiert den Inhalt 'source_uuid = f"submission:{submission.id}"'.
265. Diese Zeile definiert den Inhalt 'existing = db.scalar(select(Recipe).where(Recipe.source_uuid == source_uuid))'.
266. Diese Zeile definiert den Inhalt 'if existing:'.
267. Diese Zeile definiert den Inhalt 'raise ValueError("Submission has already been published.")'.
268. Diese Zeile definiert den Inhalt 'recipe = Recipe('.
269. Diese Zeile definiert den Inhalt 'title=submission.title.strip()[:255],'.
270. Diese Zeile definiert den Inhalt 'description=submission.description.strip(),'.
271. Diese Zeile definiert den Inhalt 'instructions=submission.instructions.strip(),'.
272. Diese Zeile definiert den Inhalt 'category=normalize_category(submission.category),'.
273. Diese Zeile definiert den Inhalt 'prep_time_minutes=max(int(submission.prep_time_minutes or 30), 1),'.
274. Diese Zeile definiert den Inhalt 'difficulty=sanitize_difficulty(submission.difficulty),'.
275. Diese Zeile definiert den Inhalt 'creator_id=admin_id,'.
276. Diese Zeile definiert den Inhalt 'source="submission",'.
277. Diese Zeile definiert den Inhalt 'source_uuid=source_uuid,'.
278. Diese Zeile definiert den Inhalt 'source_url=None,'.
279. Diese Zeile definiert den Inhalt 'source_image_url=None,'.
280. Diese Zeile definiert den Inhalt 'title_image_url=None,'.
281. Diese Zeile definiert den Inhalt 'servings_text=(submission.servings_text or "").strip()[:120] or None,'.
282. Diese Zeile definiert den Inhalt 'total_time_minutes=None,'.
283. Diese Zeile definiert den Inhalt 'is_published=True,'.
284. Diese Zeile definiert den Inhalt ')'.
285. Diese Zeile definiert den Inhalt 'db.add(recipe)'.
286. Diese Zeile definiert den Inhalt 'db.flush()'.
287. Diese Zeile definiert den Inhalt 'for item in submission.ingredients:'.
288. Diese Zeile definiert den Inhalt 'ingredient_name = item.ingredient_name.strip()'.
289. Diese Zeile definiert den Inhalt 'if not ingredient_name:'.
290. Diese Zeile definiert den Inhalt 'continue'.
291. Diese Zeile definiert den Inhalt 'ingredient = get_or_create_ingredient(db, ingredient_name)'.
292. Diese Zeile definiert den Inhalt 'db.add('.
293. Diese Zeile definiert den Inhalt 'RecipeIngredient('.
294. Diese Zeile definiert den Inhalt 'recipe_id=recipe.id,'.
295. Diese Zeile definiert den Inhalt 'ingredient_id=ingredient.id,'.
296. Diese Zeile definiert den Inhalt 'quantity_text=(item.quantity_text or "").strip()[:120],'.
297. Diese Zeile definiert den Inhalt 'grams=item.grams,'.
298. Diese Zeile definiert den Inhalt ')'.
299. Diese Zeile definiert den Inhalt ')'.
300. Diese Zeile definiert den Inhalt 'any_primary = False'.
301. Diese Zeile definiert den Inhalt 'for image in submission.images:'.
302. Diese Zeile definiert den Inhalt 'db.add('.
303. Diese Zeile definiert den Inhalt 'RecipeImage('.
304. Diese Zeile definiert den Inhalt 'recipe_id=recipe.id,'.
305. Diese Zeile definiert den Inhalt 'filename=image.filename,'.
306. Diese Zeile definiert den Inhalt 'content_type=image.content_type,'.
307. Diese Zeile definiert den Inhalt 'data=image.data,'.
308. Diese Zeile definiert den Inhalt 'is_primary=image.is_primary,'.
309. Diese Zeile definiert den Inhalt ')'.
310. Diese Zeile definiert den Inhalt ')'.
311. Diese Zeile definiert den Inhalt 'if image.is_primary:'.
312. Diese Zeile definiert den Inhalt 'any_primary = True'.
313. Diese Zeile definiert den Inhalt 'if submission.images and not any_primary:'.
314. Diese Zeile definiert den Inhalt 'first_recipe_image = db.scalar('.
315. Diese Zeile definiert den Inhalt 'select(RecipeImage).where(RecipeImage.recipe_id == recipe.id).order_by(RecipeImage.id.a...'.
316. Diese Zeile definiert den Inhalt ')'.
317. Diese Zeile definiert den Inhalt 'if first_recipe_image:'.
318. Diese Zeile definiert den Inhalt 'first_recipe_image.is_primary = True'.
319. Diese Zeile definiert den Inhalt 'return recipe'.
320. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
321. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
322. Diese Zeile definiert den Inhalt 'def get_submission_status_stats(db: Session) -> dict[str, int]:'.
323. Diese Zeile definiert den Inhalt 'rows = db.execute('.
324. Diese Zeile definiert den Inhalt 'select(RecipeSubmission.status, func.count(RecipeSubmission.id)).group_by(RecipeSubmiss...'.
325. Diese Zeile definiert den Inhalt ').all()'.
326. Diese Zeile definiert den Inhalt 'base = {"pending": 0, "approved": 0, "rejected": 0}'.
327. Diese Zeile definiert den Inhalt 'for status, count in rows:'.
328. Diese Zeile definiert den Inhalt 'base[str(status)] = int(count)'.
329. Diese Zeile definiert den Inhalt 'return base'.
330. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
331. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
332. Diese Zeile definiert den Inhalt 'def validate_upload(content_type: str, file_size_bytes: int, file_bytes: bytes | None =...'.
333. Diese Zeile definiert den Inhalt 'if content_type not in settings.allowed_image_types:'.
334. Diese Zeile definiert den Inhalt 'raise ValueError(f"Unsupported MIME type '{content_type}'.")'.
335. Diese Zeile definiert den Inhalt 'max_bytes = settings.max_upload_mb * 1024 * 1024'.
336. Diese Zeile definiert den Inhalt 'if file_size_bytes > max_bytes:'.
337. Diese Zeile definiert den Inhalt 'raise ValueError(f"Image too large. Max size is {settings.max_upload_mb} MB.")'.
338. Diese Zeile definiert den Inhalt 'if file_bytes is not None:'.
339. Diese Zeile definiert den Inhalt 'try:'.
340. Diese Zeile definiert den Inhalt 'with Image.open(io.BytesIO(file_bytes)) as image:'.
341. Diese Zeile definiert den Inhalt 'image.verify()'.
342. Diese Zeile definiert den Inhalt 'except (UnidentifiedImageError, OSError) as exc:'.
343. Diese Zeile definiert den Inhalt 'raise ValueError("Uploaded file is not a valid image.") from exc'.
344. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
345. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
346. Diese Zeile definiert den Inhalt '@lru_cache(maxsize=4096)'.
347. Diese Zeile definiert den Inhalt 'def resolve_title_image_url(image_url: str) -> str | None:'.
348. Diese Zeile definiert den Inhalt 'cleaned = image_url.strip()'.
349. Diese Zeile definiert den Inhalt 'if not cleaned:'.
350. Diese Zeile definiert den Inhalt 'return None'.
351. Diese Zeile definiert den Inhalt 'lower = cleaned.lower()'.
352. Diese Zeile definiert den Inhalt 'if "kein_bild" in lower:'.
353. Diese Zeile definiert den Inhalt 'return None'.
354. Diese Zeile definiert den Inhalt 'if lower.endswith((".jpg", ".jpeg", ".png", ".webp")) and "/wiki/" not in lower:'.
355. Diese Zeile definiert den Inhalt 'return cleaned'.
356. Diese Zeile definiert den Inhalt 'parsed = urlparse(cleaned)'.
357. Diese Zeile definiert den Inhalt 'host = parsed.netloc.lower()'.
358. Diese Zeile definiert den Inhalt 'path = unquote(parsed.path).lower()'.
359. Diese Zeile definiert den Inhalt 'if "kochwiki.org" in host and "/wiki/" in parsed.path and "datei" in path:'.
360. Diese Zeile definiert den Inhalt 'request = Request(cleaned, headers={"User-Agent": "MealMate/1.0"})'.
361. Diese Zeile definiert den Inhalt 'with urlopen(request, timeout=12) as response:'.
362. Diese Zeile definiert den Inhalt 'html_text = response.read(300_000).decode("utf-8", errors="ignore")'.
363. Diese Zeile definiert den Inhalt 'match = re.search('.
364. Diese Zeile definiert den Inhalt 'r'<meta\s+property=["\']og:image["\']\s+content=["\']([^"\']+)["\']','.
365. Diese Zeile definiert den Inhalt 'html_text,'.
366. Diese Zeile definiert den Inhalt 'flags=re.IGNORECASE,'.
367. Diese Zeile definiert den Inhalt ')'.
368. Diese Zeile definiert den Inhalt 'if match:'.
369. Diese Zeile definiert den Inhalt 'return html.unescape(match.group(1))'.
370. Diese Zeile definiert den Inhalt 'return cleaned'.
371. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
372. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
373. Diese Zeile definiert den Inhalt 'def extract_token(raw_header: str | None) -> str | None:'.
374. Diese Zeile definiert den Inhalt 'if not raw_header:'.
375. Diese Zeile definiert den Inhalt 'return None'.
376. Diese Zeile definiert den Inhalt 'prefix = "Bearer "'.
377. Diese Zeile definiert den Inhalt 'if raw_header.startswith(prefix):'.
378. Diese Zeile definiert den Inhalt 'return raw_header[len(prefix) :].strip()'.
379. Diese Zeile definiert den Inhalt 'return raw_header.strip()'.
380. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
381. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
382. Diese Zeile definiert den Inhalt 'def can_manage_recipe(current_user: User, recipe: Recipe) -> bool:'.
383. Diese Zeile definiert den Inhalt 'return current_user.role == "admin" or recipe.creator_id == current_user.id'.
384. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
385. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
386. Diese Zeile definiert den Inhalt 'def get_meta_value(db: Session, key: str) -> str | None:'.
387. Diese Zeile definiert den Inhalt 'meta = db.scalar(select(AppMeta).where(AppMeta.key == key))'.
388. Diese Zeile definiert den Inhalt 'return meta.value if meta else None'.
389. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
390. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
391. Diese Zeile definiert den Inhalt 'def set_meta_value(db: Session, key: str, value: str) -> None:'.
392. Diese Zeile definiert den Inhalt 'meta = db.scalar(select(AppMeta).where(AppMeta.key == key))'.
393. Diese Zeile definiert den Inhalt 'if not meta:'.
394. Diese Zeile definiert den Inhalt 'db.add(AppMeta(key=key, value=value))'.
395. Diese Zeile definiert den Inhalt 'return'.
396. Diese Zeile definiert den Inhalt 'meta.value = value'.
397. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
398. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
399. Diese Zeile definiert den Inhalt 'def is_meta_true(db: Session, key: str) -> bool:'.
400. Diese Zeile definiert den Inhalt 'return get_meta_value(db, key) == "1"'.
401. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
402. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
403. Diese Zeile definiert den Inhalt 'def normalize_columns(row: dict[str, Any]) -> dict[str, Any]:'.
404. Diese Zeile definiert den Inhalt 'return {str(key).strip().lower(): value for key, value in row.items()}'.
405. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
406. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
407. Diese Zeile definiert den Inhalt 'def read_kochwiki_csv(csv_path: str | Path) -> list[dict[str, Any]]:'.
408. Diese Zeile definiert den Inhalt 'path = Path(csv_path)'.
409. Diese Zeile definiert den Inhalt 'if not path.exists():'.
410. Diese Zeile definiert den Inhalt 'raise FileNotFoundError(f"CSV file not found: {path}")'.
411. Diese Zeile definiert den Inhalt 'data = path.read_bytes()'.
412. Diese Zeile definiert den Inhalt 'return read_kochwiki_csv_bytes(data)'.
413. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
414. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
415. Diese Zeile definiert den Inhalt 'def _read_csv_rows(text: str, delimiter: str) -> list[dict[str, Any]]:'.
416. Diese Zeile definiert den Inhalt 'reader = csv.DictReader(io.StringIO(text), delimiter=delimiter)'.
417. Diese Zeile definiert den Inhalt 'return [normalize_columns(row) for row in reader]'.
418. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
419. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
420. Diese Zeile definiert den Inhalt 'def read_kochwiki_csv_bytes(csv_bytes: bytes) -> list[dict[str, Any]]:'.
421. Diese Zeile definiert den Inhalt 'text = csv_bytes.decode("utf-8-sig", errors="replace")'.
422. Diese Zeile definiert den Inhalt 'sample_lines = [line for line in text.splitlines() if line.strip()][:5]'.
423. Diese Zeile definiert den Inhalt 'sample = "\n".join(sample_lines)'.
424. Diese Zeile definiert den Inhalt 'delimiter = ";" if sample.count(";") >= sample.count(",") else ","'.
425. Diese Zeile definiert den Inhalt 'rows = _read_csv_rows(text, delimiter)'.
426. Diese Zeile definiert den Inhalt 'if delimiter == ";" and rows and len(rows[0]) <= 1:'.
427. Diese Zeile definiert den Inhalt 'fallback_rows = _read_csv_rows(text, ",")'.
428. Diese Zeile definiert den Inhalt 'if fallback_rows and len(fallback_rows[0]) > 1:'.
429. Diese Zeile definiert den Inhalt 'rows = fallback_rows'.
430. Diese Zeile definiert den Inhalt 'return rows'.
431. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
432. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
433. Diese Zeile definiert den Inhalt 'def _pick_value(row: dict[str, Any], keys: tuple[str, ...]) -> Any:'.
434. Diese Zeile definiert den Inhalt 'for key in keys:'.
435. Diese Zeile definiert den Inhalt 'value = row.get(key)'.
436. Diese Zeile definiert den Inhalt 'if value not in (None, ""):'.
437. Diese Zeile definiert den Inhalt 'return value'.
438. Diese Zeile definiert den Inhalt 'return None'.
439. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
440. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
441. Diese Zeile definiert den Inhalt 'def _clean_title(value: Any) -> str:'.
442. Diese Zeile definiert den Inhalt 'title = re.sub(r"\s+", " ", str(value or "").strip())'.
443. Diese Zeile definiert den Inhalt 'return title[:255]'.
444. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
445. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
446. Diese Zeile definiert den Inhalt 'def _normalize_title_for_match(title: str) -> str:'.
447. Diese Zeile definiert den Inhalt 'return re.sub(r"\s+", " ", title.strip().lower())'.
448. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
449. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
450. Diese Zeile definiert den Inhalt 'def _parse_source_image_url(raw_value: Any) -> str | None:'.
451. Diese Zeile definiert den Inhalt 'candidate = str(raw_value or "").strip()'.
452. Diese Zeile definiert den Inhalt 'if not candidate:'.
453. Diese Zeile definiert den Inhalt 'return None'.
454. Diese Zeile definiert den Inhalt 'if "kein_bild" in candidate.lower():'.
455. Diese Zeile definiert den Inhalt 'return None'.
456. Diese Zeile definiert den Inhalt 'return candidate[:1024]'.
457. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
458. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
459. Diese Zeile definiert den Inhalt 'def _parse_kochwiki_ingredients(raw_value: Any) -> list[dict[str, Any]]:'.
460. Diese Zeile definiert den Inhalt 'entries = []'.
461. Diese Zeile definiert den Inhalt 'for item in parse_list_like(raw_value):'.
462. Diese Zeile definiert den Inhalt 'cleaned = re.sub(r"\s+", " ", item.strip())'.
463. Diese Zeile definiert den Inhalt 'if not cleaned:'.
464. Diese Zeile definiert den Inhalt 'continue'.
465. Diese Zeile definiert den Inhalt 'match = re.match(r"^\s*([\d.,/\-]+\s*[A-Za-z%]*)\s+(.+)$", cleaned)'.
466. Diese Zeile definiert den Inhalt 'if match:'.
467. Diese Zeile definiert den Inhalt 'quantity_text = match.group(1).strip()'.
468. Diese Zeile definiert den Inhalt 'name = match.group(2).strip()'.
469. Diese Zeile definiert den Inhalt 'else:'.
470. Diese Zeile definiert den Inhalt 'quantity_text = ""'.
471. Diese Zeile definiert den Inhalt 'name = cleaned'.
472. Diese Zeile definiert den Inhalt 'entries.append({"name": name, "quantity_text": quantity_text, "grams": parse_optional_i...'.
473. Diese Zeile definiert den Inhalt 'return entries'.
474. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
475. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
476. Diese Zeile definiert den Inhalt 'def _build_category(row: dict[str, Any]) -> str:'.
477. Diese Zeile definiert den Inhalt 'categories = parse_list_like(row.get("kategorien"))'.
478. Diese Zeile definiert den Inhalt 'if categories:'.
479. Diese Zeile definiert den Inhalt 'return normalize_category(categories[0])'.
480. Diese Zeile definiert den Inhalt 'for key in ("mahlzeit", "landkuche", "landkueche", "category"):'.
481. Diese Zeile definiert den Inhalt 'value = str(row.get(key) or "").strip()'.
482. Diese Zeile definiert den Inhalt 'if value:'.
483. Diese Zeile definiert den Inhalt 'return normalize_category(value)'.
484. Diese Zeile definiert den Inhalt 'return DEFAULT_CATEGORY'.
485. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
486. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
487. Diese Zeile definiert den Inhalt 'def _build_instructions(row: dict[str, Any]) -> str:'.
488. Diese Zeile definiert den Inhalt 'instructions = parse_text_block(row.get("zubereitung") or row.get("instructions") or ro...'.
489. Diese Zeile definiert den Inhalt 'return instructions or "No instructions provided."'.
490. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
491. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
492. Diese Zeile definiert den Inhalt 'def _build_description(row: dict[str, Any]) -> str:'.
493. Diese Zeile definiert den Inhalt 'description = str(row.get("beschreibung") or row.get("description") or "").strip()'.
494. Diese Zeile definiert den Inhalt 'return description or "Imported from KochWiki."'.
495. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
496. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
497. Diese Zeile definiert den Inhalt 'def _find_existing_recipe('.
498. Diese Zeile definiert den Inhalt 'db: Session,'.
499. Diese Zeile definiert den Inhalt 'source_uuid: str | None,'.
500. Diese Zeile definiert den Inhalt 'title_normalized: str,'.
501. Diese Zeile definiert den Inhalt 'source_url: str | None,'.
502. Diese Zeile definiert den Inhalt ') -> Recipe | None:'.
503. Diese Zeile definiert den Inhalt 'if source_uuid:'.
504. Diese Zeile definiert den Inhalt 'recipe = db.scalar(select(Recipe).where(Recipe.source_uuid == source_uuid))'.
505. Diese Zeile definiert den Inhalt 'if recipe:'.
506. Diese Zeile definiert den Inhalt 'return recipe'.
507. Diese Zeile definiert den Inhalt 'if source_url:'.
508. Diese Zeile definiert den Inhalt 'return db.scalar('.
509. Diese Zeile definiert den Inhalt 'select(Recipe).where('.
510. Diese Zeile definiert den Inhalt 'func.lower(Recipe.title) == title_normalized,'.
511. Diese Zeile definiert den Inhalt 'Recipe.source_url == source_url,'.
512. Diese Zeile definiert den Inhalt ')'.
513. Diese Zeile definiert den Inhalt ')'.
514. Diese Zeile definiert den Inhalt 'return None'.
515. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
516. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
517. Diese Zeile definiert den Inhalt 'def _apply_update_fields(recipe: Recipe, payload: dict[str, Any]) -> None:'.
518. Diese Zeile definiert den Inhalt 'recipe.description = payload["description"]'.
519. Diese Zeile definiert den Inhalt 'recipe.instructions = payload["instructions"]'.
520. Diese Zeile definiert den Inhalt 'recipe.category = payload["category"]'.
521. Diese Zeile definiert den Inhalt 'recipe.total_time_minutes = payload["total_time_minutes"]'.
522. Diese Zeile definiert den Inhalt 'recipe.prep_time_minutes = payload["prep_time_minutes"]'.
523. Diese Zeile definiert den Inhalt 'recipe.difficulty = payload["difficulty"]'.
524. Diese Zeile definiert den Inhalt 'recipe.servings_text = payload["servings_text"]'.
525. Diese Zeile definiert den Inhalt 'if payload["source_url"] and not recipe.source_url:'.
526. Diese Zeile definiert den Inhalt 'recipe.source_url = payload["source_url"]'.
527. Diese Zeile definiert den Inhalt 'if payload["source_uuid"] and not recipe.source_uuid:'.
528. Diese Zeile definiert den Inhalt 'recipe.source_uuid = payload["source_uuid"]'.
529. Diese Zeile definiert den Inhalt 'if payload["source_image_url"]:'.
530. Diese Zeile definiert den Inhalt 'recipe.source_image_url = payload["source_image_url"]'.
531. Diese Zeile definiert den Inhalt 'recipe.title_image_url = payload["source_image_url"]'.
532. Diese Zeile definiert den Inhalt 'recipe.source = recipe.source or "kochwiki"'.
533. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
534. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
535. Diese Zeile definiert den Inhalt 'def _download_image_if_enabled(db: Session, recipe: Recipe, source_image_url: str | Non...'.
536. Diese Zeile definiert den Inhalt 'if not settings.import_download_images or not source_image_url:'.
537. Diese Zeile definiert den Inhalt 'return'.
538. Diese Zeile definiert den Inhalt 'resolved_url = resolve_title_image_url(source_image_url)'.
539. Diese Zeile definiert den Inhalt 'if not resolved_url:'.
540. Diese Zeile definiert den Inhalt 'return'.
541. Diese Zeile definiert den Inhalt 'request = Request(resolved_url, headers={"User-Agent": "MealMate/1.0"})'.
542. Diese Zeile definiert den Inhalt 'with urlopen(request, timeout=12) as response:'.
543. Diese Zeile definiert den Inhalt 'content_type = str(response.headers.get("Content-Type") or "").split(";")[0].strip().lo...'.
544. Diese Zeile definiert den Inhalt 'data = response.read(settings.max_upload_mb * 1024 * 1024 + 1)'.
545. Diese Zeile definiert den Inhalt 'validate_upload(content_type, len(data), data)'.
546. Diese Zeile definiert den Inhalt 'filename = Path(urlparse(resolved_url).path).name or "import-image"'.
547. Diese Zeile definiert den Inhalt 'db.add('.
548. Diese Zeile definiert den Inhalt 'RecipeImage('.
549. Diese Zeile definiert den Inhalt 'recipe_id=recipe.id,'.
550. Diese Zeile definiert den Inhalt 'filename=filename[:255],'.
551. Diese Zeile definiert den Inhalt 'content_type=content_type,'.
552. Diese Zeile definiert den Inhalt 'data=data,'.
553. Diese Zeile definiert den Inhalt ')'.
554. Diese Zeile definiert den Inhalt ')'.
555. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
556. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
557. Diese Zeile definiert den Inhalt 'def _prepare_kochwiki_payload(row: dict[str, Any]) -> dict[str, Any]:'.
558. Diese Zeile definiert den Inhalt 'title = _clean_title(row.get("titel") or row.get("title") or row.get("name"))'.
559. Diese Zeile definiert den Inhalt 'if not title:'.
560. Diese Zeile definiert den Inhalt 'raise ValueError("missing title")'.
561. Diese Zeile definiert den Inhalt 'source_url = str(row.get("quelle_url") or row.get("source_url") or "").strip()[:1024] o...'.
562. Diese Zeile definiert den Inhalt 'source_uuid = str(row.get("rezept_uuid") or row.get("source_uuid") or "").strip()[:120]...'.
563. Diese Zeile definiert den Inhalt 'source_image_url = _parse_source_image_url(row.get("titelbild") or row.get("source_imag...'.
564. Diese Zeile definiert den Inhalt 'prep_time_minutes = parse_optional_int(row.get("zeit_prep_min"))'.
565. Diese Zeile definiert den Inhalt 'if prep_time_minutes is None:'.
566. Diese Zeile definiert den Inhalt 'prep_time_minutes = parse_optional_int(row.get("arbeitszeit")) or 30'.
567. Diese Zeile definiert den Inhalt 'total_time_minutes = parse_optional_int(row.get("zeit_total_min"))'.
568. Diese Zeile definiert den Inhalt 'if total_time_minutes is None:'.
569. Diese Zeile definiert den Inhalt 'total_time_minutes = parse_optional_int(row.get("arbeitszeit"))'.
570. Diese Zeile definiert den Inhalt 'servings_text = str(row.get("portionen_text") or row.get("portionen") or "").strip()[:1...'.
571. Diese Zeile definiert den Inhalt 'payload = {'.
572. Diese Zeile definiert den Inhalt '"title": title,'.
573. Diese Zeile definiert den Inhalt '"title_normalized": _normalize_title_for_match(title),'.
574. Diese Zeile definiert den Inhalt '"source": "kochwiki",'.
575. Diese Zeile definiert den Inhalt '"source_uuid": source_uuid,'.
576. Diese Zeile definiert den Inhalt '"source_url": source_url,'.
577. Diese Zeile definiert den Inhalt '"source_image_url": source_image_url,'.
578. Diese Zeile definiert den Inhalt '"description": _build_description(row),'.
579. Diese Zeile definiert den Inhalt '"instructions": _build_instructions(row),'.
580. Diese Zeile definiert den Inhalt '"category": _build_category(row),'.
581. Diese Zeile definiert den Inhalt '"prep_time_minutes": prep_time_minutes,'.
582. Diese Zeile definiert den Inhalt '"difficulty": sanitize_difficulty(str(row.get("schwierigkeit") or row.get("difficulty")...'.
583. Diese Zeile definiert den Inhalt '"servings_text": servings_text,'.
584. Diese Zeile definiert den Inhalt '"total_time_minutes": total_time_minutes,'.
585. Diese Zeile definiert den Inhalt '"ingredients": _parse_kochwiki_ingredients(row.get("zutaten")),'.
586. Diese Zeile definiert den Inhalt '}'.
587. Diese Zeile definiert den Inhalt 'return payload'.
588. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
589. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
590. Diese Zeile definiert den Inhalt 'def import_kochwiki_csv('.
591. Diese Zeile definiert den Inhalt 'db: Session,'.
592. Diese Zeile definiert den Inhalt 'csv_source: str | Path | bytes,'.
593. Diese Zeile definiert den Inhalt 'creator_id: int,'.
594. Diese Zeile definiert den Inhalt 'mode: IMPORT_MODE = "insert_only",'.
595. Diese Zeile definiert den Inhalt 'batch_size: int = 200,'.
596. Diese Zeile definiert den Inhalt 'autocommit: bool = True,'.
597. Diese Zeile definiert den Inhalt ') -> CSVImportReport:'.
598. Diese Zeile definiert den Inhalt 'if mode not in {"insert_only", "update_existing"}:'.
599. Diese Zeile definiert den Inhalt 'raise ValueError("mode must be 'insert_only' or 'update_existing'")'.
600. Diese Zeile definiert den Inhalt 'rows = read_kochwiki_csv_bytes(csv_source) if isinstance(csv_source, bytes) else read_k...'.
601. Diese Zeile definiert den Inhalt 'report = CSVImportReport()'.
602. Diese Zeile definiert den Inhalt 'pending_writes = 0'.
603. Diese Zeile definiert den Inhalt 'for row_index, row in enumerate(rows, start=2):'.
604. Diese Zeile definiert den Inhalt 'try:'.
605. Diese Zeile definiert den Inhalt 'payload = _prepare_kochwiki_payload(row)'.
606. Diese Zeile definiert den Inhalt 'with db.begin_nested():'.
607. Diese Zeile definiert den Inhalt 'existing = _find_existing_recipe('.
608. Diese Zeile definiert den Inhalt 'db,'.
609. Diese Zeile definiert den Inhalt 'payload["source_uuid"],'.
610. Diese Zeile definiert den Inhalt 'payload["title_normalized"],'.
611. Diese Zeile definiert den Inhalt 'payload["source_url"],'.
612. Diese Zeile definiert den Inhalt ')'.
613. Diese Zeile definiert den Inhalt 'if existing and mode == "insert_only":'.
614. Diese Zeile definiert den Inhalt 'report.skipped += 1'.
615. Diese Zeile definiert den Inhalt 'continue'.
616. Diese Zeile definiert den Inhalt 'if existing and mode == "update_existing":'.
617. Diese Zeile definiert den Inhalt '_apply_update_fields(existing, payload)'.
618. Diese Zeile definiert den Inhalt 'replace_recipe_ingredients(db, existing, payload["ingredients"])'.
619. Diese Zeile definiert den Inhalt 'db.add(existing)'.
620. Diese Zeile definiert den Inhalt 'report.updated += 1'.
621. Diese Zeile definiert den Inhalt 'pending_writes += 1'.
622. Diese Zeile definiert den Inhalt 'continue'.
623. Diese Zeile definiert den Inhalt 'recipe = Recipe('.
624. Diese Zeile definiert den Inhalt 'title=payload["title"],'.
625. Diese Zeile definiert den Inhalt 'title_image_url=payload["source_image_url"],'.
626. Diese Zeile definiert den Inhalt 'source=payload["source"],'.
627. Diese Zeile definiert den Inhalt 'source_uuid=payload["source_uuid"],'.
628. Diese Zeile definiert den Inhalt 'source_url=payload["source_url"],'.
629. Diese Zeile definiert den Inhalt 'source_image_url=payload["source_image_url"],'.
630. Diese Zeile definiert den Inhalt 'servings_text=payload["servings_text"],'.
631. Diese Zeile definiert den Inhalt 'total_time_minutes=payload["total_time_minutes"],'.
632. Diese Zeile definiert den Inhalt 'is_published=True,'.
633. Diese Zeile definiert den Inhalt 'description=payload["description"],'.
634. Diese Zeile definiert den Inhalt 'instructions=payload["instructions"],'.
635. Diese Zeile definiert den Inhalt 'category=payload["category"],'.
636. Diese Zeile definiert den Inhalt 'prep_time_minutes=payload["prep_time_minutes"],'.
637. Diese Zeile definiert den Inhalt 'difficulty=payload["difficulty"],'.
638. Diese Zeile definiert den Inhalt 'creator_id=creator_id,'.
639. Diese Zeile definiert den Inhalt ')'.
640. Diese Zeile definiert den Inhalt 'db.add(recipe)'.
641. Diese Zeile definiert den Inhalt 'db.flush()'.
642. Diese Zeile definiert den Inhalt 'replace_recipe_ingredients(db, recipe, payload["ingredients"])'.
643. Diese Zeile definiert den Inhalt '_download_image_if_enabled(db, recipe, payload["source_image_url"])'.
644. Diese Zeile definiert den Inhalt 'report.inserted += 1'.
645. Diese Zeile definiert den Inhalt 'pending_writes += 1'.
646. Diese Zeile definiert den Inhalt 'if pending_writes >= batch_size:'.
647. Diese Zeile definiert den Inhalt 'if autocommit:'.
648. Diese Zeile definiert den Inhalt 'db.commit()'.
649. Diese Zeile definiert den Inhalt 'else:'.
650. Diese Zeile definiert den Inhalt 'db.flush()'.
651. Diese Zeile definiert den Inhalt 'pending_writes = 0'.
652. Diese Zeile definiert den Inhalt 'except Exception as exc:'.
653. Diese Zeile definiert den Inhalt 'report.skipped += 1'.
654. Diese Zeile definiert den Inhalt 'report.errors.append(f"Row {row_index}: {exc}")'.
655. Diese Zeile definiert den Inhalt 'if pending_writes > 0:'.
656. Diese Zeile definiert den Inhalt 'if autocommit:'.
657. Diese Zeile definiert den Inhalt 'db.commit()'.
658. Diese Zeile definiert den Inhalt 'else:'.
659. Diese Zeile definiert den Inhalt 'db.flush()'.
660. Diese Zeile definiert den Inhalt 'return report'.
661. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
662. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
663. Diese Zeile definiert den Inhalt 'def build_recipe_pdf(recipe: Recipe, avg_rating: float, review_count: int) -> bytes:'.
664. Diese Zeile definiert den Inhalt 'buffer = io.BytesIO()'.
665. Diese Zeile definiert den Inhalt 'pdf = canvas.Canvas(buffer, pagesize=A4)'.
666. Diese Zeile definiert den Inhalt 'width, height = A4'.
667. Diese Zeile definiert den Inhalt 'top = height - 50'.
668. Diese Zeile definiert den Inhalt 'if recipe.images:'.
669. Diese Zeile definiert den Inhalt 'image = recipe.images[0]'.
670. Diese Zeile definiert den Inhalt 'image_reader = ImageReader(io.BytesIO(image.data))'.
671. Diese Zeile definiert den Inhalt 'pdf.drawImage(image_reader, 50, top - 120, width=120, height=90, preserveAspectRatio=Tr...'.
672. Diese Zeile definiert den Inhalt 'top -= 130'.
673. Diese Zeile definiert den Inhalt 'pdf.setFont("Helvetica-Bold", 18)'.
674. Diese Zeile definiert den Inhalt 'pdf.drawString(50, top, recipe.title)'.
675. Diese Zeile definiert den Inhalt 'top -= 24'.
676. Diese Zeile definiert den Inhalt 'pdf.setFont("Helvetica", 11)'.
677. Diese Zeile definiert den Inhalt 'meta = f"Category: {recipe.category} | Difficulty: {recipe.difficulty} | Prep: {recipe....'.
678. Diese Zeile definiert den Inhalt 'pdf.drawString(50, top, meta)'.
679. Diese Zeile definiert den Inhalt 'top -= 18'.
680. Diese Zeile definiert den Inhalt 'rating_line = f"Average rating: {avg_rating:.2f} ({review_count} reviews)"'.
681. Diese Zeile definiert den Inhalt 'pdf.drawString(50, top, rating_line)'.
682. Diese Zeile definiert den Inhalt 'top -= 26'.
683. Diese Zeile definiert den Inhalt 'pdf.setFont("Helvetica-Bold", 13)'.
684. Diese Zeile definiert den Inhalt 'pdf.drawString(50, top, "Ingredients")'.
685. Diese Zeile definiert den Inhalt 'top -= 18'.
686. Diese Zeile definiert den Inhalt 'pdf.setFont("Helvetica", 11)'.
687. Diese Zeile definiert den Inhalt 'for link in recipe.recipe_ingredients:'.
688. Diese Zeile definiert den Inhalt 'line = f"- {link.ingredient.name} {link.quantity_text}".strip()'.
689. Diese Zeile definiert den Inhalt 'if link.grams:'.
690. Diese Zeile definiert den Inhalt 'line = f"{line} ({link.grams} g)"'.
691. Diese Zeile definiert den Inhalt 'top = draw_wrapped_line(pdf, line, 50, top, width - 100)'.
692. Diese Zeile definiert den Inhalt 'if top < 100:'.
693. Diese Zeile definiert den Inhalt 'pdf.showPage()'.
694. Diese Zeile definiert den Inhalt 'top = height - 50'.
695. Diese Zeile definiert den Inhalt 'pdf.setFont("Helvetica", 11)'.
696. Diese Zeile definiert den Inhalt 'top -= 6'.
697. Diese Zeile definiert den Inhalt 'pdf.setFont("Helvetica-Bold", 13)'.
698. Diese Zeile definiert den Inhalt 'pdf.drawString(50, top, "Instructions")'.
699. Diese Zeile definiert den Inhalt 'top -= 18'.
700. Diese Zeile definiert den Inhalt 'pdf.setFont("Helvetica", 11)'.
701. Diese Zeile definiert den Inhalt 'for paragraph in [piece.strip() for piece in recipe.instructions.splitlines() if piece....'.
702. Diese Zeile definiert den Inhalt 'top = draw_wrapped_line(pdf, paragraph, 50, top, width - 100)'.
703. Diese Zeile definiert den Inhalt 'top -= 4'.
704. Diese Zeile definiert den Inhalt 'if top < 80:'.
705. Diese Zeile definiert den Inhalt 'pdf.showPage()'.
706. Diese Zeile definiert den Inhalt 'top = height - 50'.
707. Diese Zeile definiert den Inhalt 'pdf.setFont("Helvetica", 11)'.
708. Diese Zeile definiert den Inhalt 'pdf.save()'.
709. Diese Zeile definiert den Inhalt 'buffer.seek(0)'.
710. Diese Zeile definiert den Inhalt 'return buffer.getvalue()'.
711. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
712. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
713. Diese Zeile definiert den Inhalt 'def draw_wrapped_line(pdf: canvas.Canvas, text: str, x: int, y: int, max_width: int) ->...'.
714. Diese Zeile definiert den Inhalt 'words = text.split()'.
715. Diese Zeile definiert den Inhalt 'current = ""'.
716. Diese Zeile definiert den Inhalt 'for word in words:'.
717. Diese Zeile definiert den Inhalt 'trial = f"{current} {word}".strip()'.
718. Diese Zeile definiert den Inhalt 'if pdf.stringWidth(trial, "Helvetica", 11) <= max_width:'.
719. Diese Zeile definiert den Inhalt 'current = trial'.
720. Diese Zeile definiert den Inhalt 'continue'.
721. Diese Zeile definiert den Inhalt 'pdf.drawString(x, y, current)'.
722. Diese Zeile definiert den Inhalt 'y -= 14'.
723. Diese Zeile definiert den Inhalt 'current = word'.
724. Diese Zeile definiert den Inhalt 'if current:'.
725. Diese Zeile definiert den Inhalt 'pdf.drawString(x, y, current)'.
726. Diese Zeile definiert den Inhalt 'y -= 14'.
727. Diese Zeile definiert den Inhalt 'return y'.
728. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
729. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
730. Diese Zeile definiert den Inhalt 'def readable_file_size(size_bytes: int) -> str:'.
731. Diese Zeile definiert den Inhalt 'return f"{size_bytes / (1024 * 1024):.2f} MB"'.

## app/csv_import.py
```python
import csv
import hashlib
import io
import json
import re
from dataclasses import dataclass, field
from typing import Any, Literal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Recipe
from app.services import (
    DEFAULT_CATEGORY,
    get_or_create_ingredient,
    normalize_category,
    normalize_ingredient_name,
    parse_ingredient_text,
    parse_list_like,
    parse_optional_int,
    replace_recipe_ingredients,
    sanitize_difficulty,
)

ADMIN_IMPORT_MODE = Literal["insert_only", "update_existing"]

CANONICAL_CSV_COLUMNS = [
    "title",
    "instructions",
    "description",
    "category",
    "difficulty",
    "prep_time_minutes",
    "servings_text",
    "ingredients",
    "image_url",
    "source_uuid",
]


@dataclass
class AdminCSVPreviewRow:
    row_number: int
    title: str
    category: str
    difficulty: str
    prep_time_minutes: str
    source_uuid: str
    status: str
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass
class AdminCSVImportReport:
    mode: ADMIN_IMPORT_MODE
    dry_run: bool
    inserted: int = 0
    updated: int = 0
    skipped: int = 0
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    preview_rows: list[AdminCSVPreviewRow] = field(default_factory=list)
    total_rows: int = 0
    fatal_error_rows: int = 0
    delimiter: str = ";"
    encoding: str = "utf-8-sig"


@dataclass
class _PreparedRow:
    row_number: int
    title: str
    title_normalized: str
    description: str
    instructions: str
    instruction_hash: str
    category: str
    category_normalized: str
    difficulty: str
    prep_time_minutes: int
    servings_text: str | None
    ingredients: list[dict[str, Any]]
    image_url: str | None
    source_uuid: str | None
    skip_reason: str | None = None


def _normalize_header(name: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "_", str(name or "").strip().lower())
    return normalized.strip("_")


def _normalize_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "").strip())


def _normalize_text_lower(value: Any) -> str:
    return _normalize_text(value).lower()


def _instruction_hash(value: str) -> str:
    normalized = _normalize_text_lower(value)
    return hashlib.sha1(normalized.encode("utf-8")).hexdigest()[:16]


def _detect_delimiter(text: str) -> str:
    sample_lines = [line for line in text.splitlines() if line.strip()][:5]
    sample = "\n".join(sample_lines)
    return ";" if sample.count(";") >= sample.count(",") else ","


def _parse_csv_rows(csv_bytes: bytes) -> tuple[list[dict[str, str]], str]:
    text = csv_bytes.decode("utf-8-sig", errors="replace")
    delimiter = _detect_delimiter(text)
    reader = csv.DictReader(io.StringIO(text), delimiter=delimiter)
    rows: list[dict[str, str]] = []
    for row in reader:
        normalized_row: dict[str, str] = {}
        for key, value in row.items():
            normalized_row[_normalize_header(key)] = _normalize_text(value)
        rows.append(normalized_row)
    if delimiter == ";" and rows and len(rows[0]) <= 1:
        fallback_reader = csv.DictReader(io.StringIO(text), delimiter=",")
        fallback_rows: list[dict[str, str]] = []
        for row in fallback_reader:
            normalized_row = {}
            for key, value in row.items():
                normalized_row[_normalize_header(key)] = _normalize_text(value)
            fallback_rows.append(normalized_row)
        if fallback_rows and len(fallback_rows[0]) > 1:
            return fallback_rows, ","
    return rows, delimiter


def _pick_value(row: dict[str, str], *keys: str) -> str:
    for key in keys:
        value = row.get(key, "")
        if value:
            return value
    return ""


def _parse_admin_ingredients(raw_value: str) -> list[dict[str, Any]]:
    cleaned = str(raw_value or "").strip()
    if not cleaned:
        return []
    if cleaned.startswith("[") and cleaned.endswith("]"):
        try:
            loaded = json.loads(cleaned)
        except json.JSONDecodeError:
            loaded = None
        if isinstance(loaded, list):
            tokens = [str(item).strip() for item in loaded if str(item).strip()]
        else:
            tokens = parse_list_like(cleaned)
    elif "\n" in cleaned:
        return parse_ingredient_text(cleaned)
    elif " | " in cleaned:
        tokens = [token.strip() for token in cleaned.split(" | ") if token.strip()]
    else:
        tokens = [token.strip() for token in parse_list_like(cleaned) if token.strip()]
    entries: list[dict[str, Any]] = []
    for token in tokens:
        match = re.match(r"^\s*([\d.,/\-]+\s*[A-Za-z%]*)\s+(.+)$", token)
        if match:
            quantity_text = match.group(1).strip()
            name = match.group(2).strip()
        else:
            quantity_text = ""
            name = token.strip()
        if not name:
            continue
        entries.append(
            {
                "name": name[:200],
                "quantity_text": quantity_text[:120],
                "grams": parse_optional_int(token),
            }
        )
    return entries


def _find_existing_recipe_for_admin(db: Session, payload: _PreparedRow) -> Recipe | None:
    if payload.source_uuid:
        existing = db.scalar(select(Recipe).where(Recipe.source_uuid == payload.source_uuid))
        if existing:
            return existing
    candidates = db.scalars(
        select(Recipe).where(
            func.lower(Recipe.title) == payload.title_normalized,
            func.lower(Recipe.category) == payload.category_normalized,
        )
    ).all()
    for recipe in candidates:
        if _instruction_hash(recipe.instructions) == payload.instruction_hash:
            return recipe
    return None


def _prepare_rows(
    rows: list[dict[str, str]],
    mode: ADMIN_IMPORT_MODE,
    preview_limit: int,
) -> tuple[list[_PreparedRow], AdminCSVImportReport]:
    report = AdminCSVImportReport(mode=mode, dry_run=True)
    prepared_rows: list[_PreparedRow] = []
    seen_source_uuid: set[str] = set()
    seen_fallback: set[tuple[str, str, str]] = set()
    for index, row in enumerate(rows, start=2):
        report.total_rows += 1
        row_errors: list[str] = []
        row_warnings: list[str] = []
        title_raw = _pick_value(row, "title", "name")
        instructions_raw = _pick_value(row, "instructions", "steps")
        if not title_raw:
            row_errors.append("title fehlt")
        if not instructions_raw:
            row_errors.append("instructions fehlt")
        title = _normalize_text(title_raw)[:255]
        title_normalized = _normalize_text_lower(title)
        instructions = instructions_raw.strip()
        instruction_hash = _instruction_hash(instructions)
        description = _pick_value(row, "description") or "Importiert ueber Admin CSV."
        category = normalize_category(_pick_value(row, "category") or DEFAULT_CATEGORY)
        category_normalized = _normalize_text_lower(category)
        difficulty_raw = _pick_value(row, "difficulty")
        difficulty = sanitize_difficulty(difficulty_raw or "medium")
        if difficulty_raw and difficulty not in {"easy", "medium", "hard"}:
            row_warnings.append(f"difficulty '{difficulty_raw}' wurde auf '{difficulty}' gesetzt")
        prep_time_raw = _pick_value(row, "prep_time_minutes")
        prep_time_minutes = 30
        if prep_time_raw:
            parsed_prep = parse_optional_int(prep_time_raw)
            if parsed_prep is None or parsed_prep <= 0:
                row_errors.append("prep_time_minutes ist ungueltig")
            else:
                prep_time_minutes = parsed_prep
        servings_text = _pick_value(row, "servings_text")[:120] or None
        image_url_raw = _pick_value(row, "image_url")
        image_url = image_url_raw[:1024] if image_url_raw else None
        if image_url and not (image_url.startswith("http://") or image_url.startswith("https://")):
            row_warnings.append("image_url ist ungueltig und wurde ignoriert")
            image_url = None
        source_uuid = _pick_value(row, "source_uuid")[:120] or None
        ingredients = _parse_admin_ingredients(_pick_value(row, "ingredients"))
        if source_uuid:
            if source_uuid in seen_source_uuid:
                row_warnings.append("doppelte source_uuid in der CSV, Zeile wird uebersprungen")
                skip_reason = "duplicate-source-uuid"
            else:
                seen_source_uuid.add(source_uuid)
                skip_reason = None
        else:
            fallback_key = (title_normalized, category_normalized, instruction_hash)
            if fallback_key in seen_fallback:
                row_warnings.append("doppeltes Rezept in der CSV, Zeile wird uebersprungen")
                skip_reason = "duplicate-fallback-key"
            else:
                seen_fallback.add(fallback_key)
                skip_reason = None
        if row_errors:
            report.fatal_error_rows += 1
            report.errors.extend([f"Zeile {index}: {reason}" for reason in row_errors])
        if row_warnings:
            report.warnings.extend([f"Zeile {index}: {reason}" for reason in row_warnings])
        status = "ok"
        if row_errors:
            status = "error"
        elif skip_reason:
            status = "skip"
        elif row_warnings:
            status = "warning"
        if len(report.preview_rows) < preview_limit:
            report.preview_rows.append(
                AdminCSVPreviewRow(
                    row_number=index,
                    title=title,
                    category=category,
                    difficulty=difficulty,
                    prep_time_minutes=str(prep_time_minutes),
                    source_uuid=source_uuid or "",
                    status=status,
                    errors=row_errors,
                    warnings=row_warnings,
                )
            )
        prepared_rows.append(
            _PreparedRow(
                row_number=index,
                title=title,
                title_normalized=title_normalized,
                description=description.strip(),
                instructions=instructions,
                instruction_hash=instruction_hash,
                category=category,
                category_normalized=category_normalized,
                difficulty=difficulty,
                prep_time_minutes=prep_time_minutes,
                servings_text=servings_text,
                ingredients=ingredients,
                image_url=image_url,
                source_uuid=source_uuid,
                skip_reason=skip_reason,
            )
        )
    return prepared_rows, report


def _create_recipe_from_payload(db: Session, payload: _PreparedRow, creator_id: int) -> Recipe:
    recipe = Recipe(
        title=payload.title,
        description=payload.description,
        instructions=payload.instructions,
        category=payload.category,
        prep_time_minutes=payload.prep_time_minutes,
        difficulty=payload.difficulty,
        creator_id=creator_id,
        source="admin_csv",
        source_uuid=payload.source_uuid,
        source_url=None,
        source_image_url=payload.image_url,
        title_image_url=payload.image_url,
        servings_text=payload.servings_text,
        total_time_minutes=None,
        is_published=True,
    )
    db.add(recipe)
    db.flush()
    if payload.ingredients:
        replace_recipe_ingredients(db, recipe, payload.ingredients)
    return recipe


def _update_recipe_from_payload(db: Session, recipe: Recipe, payload: _PreparedRow) -> None:
    recipe.description = payload.description
    recipe.instructions = payload.instructions
    recipe.category = payload.category
    recipe.prep_time_minutes = payload.prep_time_minutes
    recipe.difficulty = payload.difficulty
    recipe.servings_text = payload.servings_text
    if payload.image_url:
        recipe.title_image_url = payload.image_url
        recipe.source_image_url = payload.image_url
    if payload.source_uuid and not recipe.source_uuid:
        recipe.source_uuid = payload.source_uuid
    if payload.ingredients:
        replace_recipe_ingredients(db, recipe, payload.ingredients)
    db.add(recipe)


def import_admin_csv(
    db: Session,
    csv_bytes: bytes,
    creator_id: int,
    mode: ADMIN_IMPORT_MODE = "insert_only",
    dry_run: bool = True,
    batch_size: int = 200,
    preview_limit: int = 20,
    autocommit: bool = False,
) -> AdminCSVImportReport:
    if mode not in {"insert_only", "update_existing"}:
        raise ValueError("mode must be 'insert_only' or 'update_existing'")
    rows, delimiter = _parse_csv_rows(csv_bytes)
    prepared_rows, report = _prepare_rows(rows, mode, preview_limit)
    report.delimiter = delimiter
    report.dry_run = dry_run
    if report.fatal_error_rows > 0:
        return report
    pending_writes = 0
    for payload in prepared_rows:
        if payload.skip_reason:
            report.skipped += 1
            continue
        existing = _find_existing_recipe_for_admin(db, payload)
        if existing and mode == "insert_only":
            report.skipped += 1
            continue
        if existing and mode == "update_existing":
            if not dry_run:
                _update_recipe_from_payload(db, existing, payload)
                pending_writes += 1
            report.updated += 1
        else:
            if not dry_run:
                _create_recipe_from_payload(db, payload, creator_id)
                pending_writes += 1
            report.inserted += 1
        if not dry_run and pending_writes >= batch_size:
            if autocommit:
                db.commit()
            else:
                db.flush()
            pending_writes = 0
    if not dry_run and pending_writes > 0:
        if autocommit:
            db.commit()
        else:
            db.flush()
    return report


def build_csv_template_bytes() -> bytes:
    buffer = io.StringIO()
    writer = csv.writer(buffer, delimiter=";")
    writer.writerow(CANONICAL_CSV_COLUMNS)
    writer.writerow(
        [
            "Spaghetti Carbonara",
            "Pasta kochen. Speck anbraten. Mit Ei-Kaese-Mischung verruehren.",
            "Klassische Carbonara mit Ei und Pecorino.",
            "Pasta",
            "medium",
            "25",
            "2 Portionen",
            "200g Spaghetti | 120g Guanciale | 2 Eier | 50g Pecorino",
            "https://example.com/carbonara.jpg",
            "admin-demo-001",
        ]
    )
    content = buffer.getvalue()
    return ("\ufeff" + content).encode("utf-8")


def build_csv_example_bytes() -> bytes:
    buffer = io.StringIO()
    writer = csv.writer(buffer, delimiter=";")
    writer.writerow(CANONICAL_CSV_COLUMNS)
    writer.writerow(
        [
            "Linsensuppe",
            "Zwiebeln anschwitzen. Linsen dazugeben. Mit Bruehe kochen.",
            "Herzhafte Suppe fuer kalte Tage.",
            "Suppen",
            "easy",
            "35",
            "4 Portionen",
            "250g Linsen | 1 Zwiebel | 2 Karotten | 1L Gemuesebruehe",
            "",
            "admin-demo-002",
        ]
    )
    writer.writerow(
        [
            "Schneller Obstsalat",
            "Obst schneiden und mit Zitronensaft vermengen.",
            "Frischer Salat mit saisonalem Obst.",
            "Dessert",
            "easy",
            "10",
            "3 Portionen",
            "[\"2 Aepfel\", \"1 Banane\", \"1 Orange\", \"1 TL Zitronensaft\"]",
            "https://example.com/obstsalat.jpg",
            "admin-demo-003",
        ]
    )
    writer.writerow(
        [
            "Ofengemuese",
            "Gemuese schneiden, wuerzen und 30 Minuten backen.",
            "Knackiges Ofengemuese.",
            "Hauptgericht",
            "medium",
            "40",
            "2 Portionen",
            "2 Karotten | 1 Zucchini | 1 Paprika | 2 EL Olivenoel",
            "",
            "",
        ]
    )
    content = buffer.getvalue()
    return ("\ufeff" + content).encode("utf-8")
```
ZEILEN-ERKL?RUNG
1. Diese Zeile definiert den Inhalt 'import csv'.
2. Diese Zeile definiert den Inhalt 'import hashlib'.
3. Diese Zeile definiert den Inhalt 'import io'.
4. Diese Zeile definiert den Inhalt 'import json'.
5. Diese Zeile definiert den Inhalt 'import re'.
6. Diese Zeile definiert den Inhalt 'from dataclasses import dataclass, field'.
7. Diese Zeile definiert den Inhalt 'from typing import Any, Literal'.
8. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
9. Diese Zeile definiert den Inhalt 'from sqlalchemy import func, select'.
10. Diese Zeile definiert den Inhalt 'from sqlalchemy.orm import Session'.
11. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
12. Diese Zeile definiert den Inhalt 'from app.models import Recipe'.
13. Diese Zeile definiert den Inhalt 'from app.services import ('.
14. Diese Zeile definiert den Inhalt 'DEFAULT_CATEGORY,'.
15. Diese Zeile definiert den Inhalt 'get_or_create_ingredient,'.
16. Diese Zeile definiert den Inhalt 'normalize_category,'.
17. Diese Zeile definiert den Inhalt 'normalize_ingredient_name,'.
18. Diese Zeile definiert den Inhalt 'parse_ingredient_text,'.
19. Diese Zeile definiert den Inhalt 'parse_list_like,'.
20. Diese Zeile definiert den Inhalt 'parse_optional_int,'.
21. Diese Zeile definiert den Inhalt 'replace_recipe_ingredients,'.
22. Diese Zeile definiert den Inhalt 'sanitize_difficulty,'.
23. Diese Zeile definiert den Inhalt ')'.
24. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
25. Diese Zeile definiert den Inhalt 'ADMIN_IMPORT_MODE = Literal["insert_only", "update_existing"]'.
26. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
27. Diese Zeile definiert den Inhalt 'CANONICAL_CSV_COLUMNS = ['.
28. Diese Zeile definiert den Inhalt '"title",'.
29. Diese Zeile definiert den Inhalt '"instructions",'.
30. Diese Zeile definiert den Inhalt '"description",'.
31. Diese Zeile definiert den Inhalt '"category",'.
32. Diese Zeile definiert den Inhalt '"difficulty",'.
33. Diese Zeile definiert den Inhalt '"prep_time_minutes",'.
34. Diese Zeile definiert den Inhalt '"servings_text",'.
35. Diese Zeile definiert den Inhalt '"ingredients",'.
36. Diese Zeile definiert den Inhalt '"image_url",'.
37. Diese Zeile definiert den Inhalt '"source_uuid",'.
38. Diese Zeile definiert den Inhalt ']'.
39. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
40. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
41. Diese Zeile definiert den Inhalt '@dataclass'.
42. Diese Zeile definiert den Inhalt 'class AdminCSVPreviewRow:'.
43. Diese Zeile definiert den Inhalt 'row_number: int'.
44. Diese Zeile definiert den Inhalt 'title: str'.
45. Diese Zeile definiert den Inhalt 'category: str'.
46. Diese Zeile definiert den Inhalt 'difficulty: str'.
47. Diese Zeile definiert den Inhalt 'prep_time_minutes: str'.
48. Diese Zeile definiert den Inhalt 'source_uuid: str'.
49. Diese Zeile definiert den Inhalt 'status: str'.
50. Diese Zeile definiert den Inhalt 'errors: list[str] = field(default_factory=list)'.
51. Diese Zeile definiert den Inhalt 'warnings: list[str] = field(default_factory=list)'.
52. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
53. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
54. Diese Zeile definiert den Inhalt '@dataclass'.
55. Diese Zeile definiert den Inhalt 'class AdminCSVImportReport:'.
56. Diese Zeile definiert den Inhalt 'mode: ADMIN_IMPORT_MODE'.
57. Diese Zeile definiert den Inhalt 'dry_run: bool'.
58. Diese Zeile definiert den Inhalt 'inserted: int = 0'.
59. Diese Zeile definiert den Inhalt 'updated: int = 0'.
60. Diese Zeile definiert den Inhalt 'skipped: int = 0'.
61. Diese Zeile definiert den Inhalt 'errors: list[str] = field(default_factory=list)'.
62. Diese Zeile definiert den Inhalt 'warnings: list[str] = field(default_factory=list)'.
63. Diese Zeile definiert den Inhalt 'preview_rows: list[AdminCSVPreviewRow] = field(default_factory=list)'.
64. Diese Zeile definiert den Inhalt 'total_rows: int = 0'.
65. Diese Zeile definiert den Inhalt 'fatal_error_rows: int = 0'.
66. Diese Zeile definiert den Inhalt 'delimiter: str = ";"'.
67. Diese Zeile definiert den Inhalt 'encoding: str = "utf-8-sig"'.
68. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
69. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
70. Diese Zeile definiert den Inhalt '@dataclass'.
71. Diese Zeile definiert den Inhalt 'class _PreparedRow:'.
72. Diese Zeile definiert den Inhalt 'row_number: int'.
73. Diese Zeile definiert den Inhalt 'title: str'.
74. Diese Zeile definiert den Inhalt 'title_normalized: str'.
75. Diese Zeile definiert den Inhalt 'description: str'.
76. Diese Zeile definiert den Inhalt 'instructions: str'.
77. Diese Zeile definiert den Inhalt 'instruction_hash: str'.
78. Diese Zeile definiert den Inhalt 'category: str'.
79. Diese Zeile definiert den Inhalt 'category_normalized: str'.
80. Diese Zeile definiert den Inhalt 'difficulty: str'.
81. Diese Zeile definiert den Inhalt 'prep_time_minutes: int'.
82. Diese Zeile definiert den Inhalt 'servings_text: str | None'.
83. Diese Zeile definiert den Inhalt 'ingredients: list[dict[str, Any]]'.
84. Diese Zeile definiert den Inhalt 'image_url: str | None'.
85. Diese Zeile definiert den Inhalt 'source_uuid: str | None'.
86. Diese Zeile definiert den Inhalt 'skip_reason: str | None = None'.
87. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
88. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
89. Diese Zeile definiert den Inhalt 'def _normalize_header(name: str) -> str:'.
90. Diese Zeile definiert den Inhalt 'normalized = re.sub(r"[^a-z0-9]+", "_", str(name or "").strip().lower())'.
91. Diese Zeile definiert den Inhalt 'return normalized.strip("_")'.
92. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
93. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
94. Diese Zeile definiert den Inhalt 'def _normalize_text(value: Any) -> str:'.
95. Diese Zeile definiert den Inhalt 'return re.sub(r"\s+", " ", str(value or "").strip())'.
96. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
97. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
98. Diese Zeile definiert den Inhalt 'def _normalize_text_lower(value: Any) -> str:'.
99. Diese Zeile definiert den Inhalt 'return _normalize_text(value).lower()'.
100. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
101. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
102. Diese Zeile definiert den Inhalt 'def _instruction_hash(value: str) -> str:'.
103. Diese Zeile definiert den Inhalt 'normalized = _normalize_text_lower(value)'.
104. Diese Zeile definiert den Inhalt 'return hashlib.sha1(normalized.encode("utf-8")).hexdigest()[:16]'.
105. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
106. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
107. Diese Zeile definiert den Inhalt 'def _detect_delimiter(text: str) -> str:'.
108. Diese Zeile definiert den Inhalt 'sample_lines = [line for line in text.splitlines() if line.strip()][:5]'.
109. Diese Zeile definiert den Inhalt 'sample = "\n".join(sample_lines)'.
110. Diese Zeile definiert den Inhalt 'return ";" if sample.count(";") >= sample.count(",") else ","'.
111. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
112. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
113. Diese Zeile definiert den Inhalt 'def _parse_csv_rows(csv_bytes: bytes) -> tuple[list[dict[str, str]], str]:'.
114. Diese Zeile definiert den Inhalt 'text = csv_bytes.decode("utf-8-sig", errors="replace")'.
115. Diese Zeile definiert den Inhalt 'delimiter = _detect_delimiter(text)'.
116. Diese Zeile definiert den Inhalt 'reader = csv.DictReader(io.StringIO(text), delimiter=delimiter)'.
117. Diese Zeile definiert den Inhalt 'rows: list[dict[str, str]] = []'.
118. Diese Zeile definiert den Inhalt 'for row in reader:'.
119. Diese Zeile definiert den Inhalt 'normalized_row: dict[str, str] = {}'.
120. Diese Zeile definiert den Inhalt 'for key, value in row.items():'.
121. Diese Zeile definiert den Inhalt 'normalized_row[_normalize_header(key)] = _normalize_text(value)'.
122. Diese Zeile definiert den Inhalt 'rows.append(normalized_row)'.
123. Diese Zeile definiert den Inhalt 'if delimiter == ";" and rows and len(rows[0]) <= 1:'.
124. Diese Zeile definiert den Inhalt 'fallback_reader = csv.DictReader(io.StringIO(text), delimiter=",")'.
125. Diese Zeile definiert den Inhalt 'fallback_rows: list[dict[str, str]] = []'.
126. Diese Zeile definiert den Inhalt 'for row in fallback_reader:'.
127. Diese Zeile definiert den Inhalt 'normalized_row = {}'.
128. Diese Zeile definiert den Inhalt 'for key, value in row.items():'.
129. Diese Zeile definiert den Inhalt 'normalized_row[_normalize_header(key)] = _normalize_text(value)'.
130. Diese Zeile definiert den Inhalt 'fallback_rows.append(normalized_row)'.
131. Diese Zeile definiert den Inhalt 'if fallback_rows and len(fallback_rows[0]) > 1:'.
132. Diese Zeile definiert den Inhalt 'return fallback_rows, ","'.
133. Diese Zeile definiert den Inhalt 'return rows, delimiter'.
134. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
135. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
136. Diese Zeile definiert den Inhalt 'def _pick_value(row: dict[str, str], *keys: str) -> str:'.
137. Diese Zeile definiert den Inhalt 'for key in keys:'.
138. Diese Zeile definiert den Inhalt 'value = row.get(key, "")'.
139. Diese Zeile definiert den Inhalt 'if value:'.
140. Diese Zeile definiert den Inhalt 'return value'.
141. Diese Zeile definiert den Inhalt 'return ""'.
142. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
143. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
144. Diese Zeile definiert den Inhalt 'def _parse_admin_ingredients(raw_value: str) -> list[dict[str, Any]]:'.
145. Diese Zeile definiert den Inhalt 'cleaned = str(raw_value or "").strip()'.
146. Diese Zeile definiert den Inhalt 'if not cleaned:'.
147. Diese Zeile definiert den Inhalt 'return []'.
148. Diese Zeile definiert den Inhalt 'if cleaned.startswith("[") and cleaned.endswith("]"):'.
149. Diese Zeile definiert den Inhalt 'try:'.
150. Diese Zeile definiert den Inhalt 'loaded = json.loads(cleaned)'.
151. Diese Zeile definiert den Inhalt 'except json.JSONDecodeError:'.
152. Diese Zeile definiert den Inhalt 'loaded = None'.
153. Diese Zeile definiert den Inhalt 'if isinstance(loaded, list):'.
154. Diese Zeile definiert den Inhalt 'tokens = [str(item).strip() for item in loaded if str(item).strip()]'.
155. Diese Zeile definiert den Inhalt 'else:'.
156. Diese Zeile definiert den Inhalt 'tokens = parse_list_like(cleaned)'.
157. Diese Zeile definiert den Inhalt 'elif "\n" in cleaned:'.
158. Diese Zeile definiert den Inhalt 'return parse_ingredient_text(cleaned)'.
159. Diese Zeile definiert den Inhalt 'elif " | " in cleaned:'.
160. Diese Zeile definiert den Inhalt 'tokens = [token.strip() for token in cleaned.split(" | ") if token.strip()]'.
161. Diese Zeile definiert den Inhalt 'else:'.
162. Diese Zeile definiert den Inhalt 'tokens = [token.strip() for token in parse_list_like(cleaned) if token.strip()]'.
163. Diese Zeile definiert den Inhalt 'entries: list[dict[str, Any]] = []'.
164. Diese Zeile definiert den Inhalt 'for token in tokens:'.
165. Diese Zeile definiert den Inhalt 'match = re.match(r"^\s*([\d.,/\-]+\s*[A-Za-z%]*)\s+(.+)$", token)'.
166. Diese Zeile definiert den Inhalt 'if match:'.
167. Diese Zeile definiert den Inhalt 'quantity_text = match.group(1).strip()'.
168. Diese Zeile definiert den Inhalt 'name = match.group(2).strip()'.
169. Diese Zeile definiert den Inhalt 'else:'.
170. Diese Zeile definiert den Inhalt 'quantity_text = ""'.
171. Diese Zeile definiert den Inhalt 'name = token.strip()'.
172. Diese Zeile definiert den Inhalt 'if not name:'.
173. Diese Zeile definiert den Inhalt 'continue'.
174. Diese Zeile definiert den Inhalt 'entries.append('.
175. Diese Zeile definiert den Inhalt '{'.
176. Diese Zeile definiert den Inhalt '"name": name[:200],'.
177. Diese Zeile definiert den Inhalt '"quantity_text": quantity_text[:120],'.
178. Diese Zeile definiert den Inhalt '"grams": parse_optional_int(token),'.
179. Diese Zeile definiert den Inhalt '}'.
180. Diese Zeile definiert den Inhalt ')'.
181. Diese Zeile definiert den Inhalt 'return entries'.
182. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
183. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
184. Diese Zeile definiert den Inhalt 'def _find_existing_recipe_for_admin(db: Session, payload: _PreparedRow) -> Recipe | None:'.
185. Diese Zeile definiert den Inhalt 'if payload.source_uuid:'.
186. Diese Zeile definiert den Inhalt 'existing = db.scalar(select(Recipe).where(Recipe.source_uuid == payload.source_uuid))'.
187. Diese Zeile definiert den Inhalt 'if existing:'.
188. Diese Zeile definiert den Inhalt 'return existing'.
189. Diese Zeile definiert den Inhalt 'candidates = db.scalars('.
190. Diese Zeile definiert den Inhalt 'select(Recipe).where('.
191. Diese Zeile definiert den Inhalt 'func.lower(Recipe.title) == payload.title_normalized,'.
192. Diese Zeile definiert den Inhalt 'func.lower(Recipe.category) == payload.category_normalized,'.
193. Diese Zeile definiert den Inhalt ')'.
194. Diese Zeile definiert den Inhalt ').all()'.
195. Diese Zeile definiert den Inhalt 'for recipe in candidates:'.
196. Diese Zeile definiert den Inhalt 'if _instruction_hash(recipe.instructions) == payload.instruction_hash:'.
197. Diese Zeile definiert den Inhalt 'return recipe'.
198. Diese Zeile definiert den Inhalt 'return None'.
199. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
200. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
201. Diese Zeile definiert den Inhalt 'def _prepare_rows('.
202. Diese Zeile definiert den Inhalt 'rows: list[dict[str, str]],'.
203. Diese Zeile definiert den Inhalt 'mode: ADMIN_IMPORT_MODE,'.
204. Diese Zeile definiert den Inhalt 'preview_limit: int,'.
205. Diese Zeile definiert den Inhalt ') -> tuple[list[_PreparedRow], AdminCSVImportReport]:'.
206. Diese Zeile definiert den Inhalt 'report = AdminCSVImportReport(mode=mode, dry_run=True)'.
207. Diese Zeile definiert den Inhalt 'prepared_rows: list[_PreparedRow] = []'.
208. Diese Zeile definiert den Inhalt 'seen_source_uuid: set[str] = set()'.
209. Diese Zeile definiert den Inhalt 'seen_fallback: set[tuple[str, str, str]] = set()'.
210. Diese Zeile definiert den Inhalt 'for index, row in enumerate(rows, start=2):'.
211. Diese Zeile definiert den Inhalt 'report.total_rows += 1'.
212. Diese Zeile definiert den Inhalt 'row_errors: list[str] = []'.
213. Diese Zeile definiert den Inhalt 'row_warnings: list[str] = []'.
214. Diese Zeile definiert den Inhalt 'title_raw = _pick_value(row, "title", "name")'.
215. Diese Zeile definiert den Inhalt 'instructions_raw = _pick_value(row, "instructions", "steps")'.
216. Diese Zeile definiert den Inhalt 'if not title_raw:'.
217. Diese Zeile definiert den Inhalt 'row_errors.append("title fehlt")'.
218. Diese Zeile definiert den Inhalt 'if not instructions_raw:'.
219. Diese Zeile definiert den Inhalt 'row_errors.append("instructions fehlt")'.
220. Diese Zeile definiert den Inhalt 'title = _normalize_text(title_raw)[:255]'.
221. Diese Zeile definiert den Inhalt 'title_normalized = _normalize_text_lower(title)'.
222. Diese Zeile definiert den Inhalt 'instructions = instructions_raw.strip()'.
223. Diese Zeile definiert den Inhalt 'instruction_hash = _instruction_hash(instructions)'.
224. Diese Zeile definiert den Inhalt 'description = _pick_value(row, "description") or "Importiert ueber Admin CSV."'.
225. Diese Zeile definiert den Inhalt 'category = normalize_category(_pick_value(row, "category") or DEFAULT_CATEGORY)'.
226. Diese Zeile definiert den Inhalt 'category_normalized = _normalize_text_lower(category)'.
227. Diese Zeile definiert den Inhalt 'difficulty_raw = _pick_value(row, "difficulty")'.
228. Diese Zeile definiert den Inhalt 'difficulty = sanitize_difficulty(difficulty_raw or "medium")'.
229. Diese Zeile definiert den Inhalt 'if difficulty_raw and difficulty not in {"easy", "medium", "hard"}:'.
230. Diese Zeile definiert den Inhalt 'row_warnings.append(f"difficulty '{difficulty_raw}' wurde auf '{difficulty}' gesetzt")'.
231. Diese Zeile definiert den Inhalt 'prep_time_raw = _pick_value(row, "prep_time_minutes")'.
232. Diese Zeile definiert den Inhalt 'prep_time_minutes = 30'.
233. Diese Zeile definiert den Inhalt 'if prep_time_raw:'.
234. Diese Zeile definiert den Inhalt 'parsed_prep = parse_optional_int(prep_time_raw)'.
235. Diese Zeile definiert den Inhalt 'if parsed_prep is None or parsed_prep <= 0:'.
236. Diese Zeile definiert den Inhalt 'row_errors.append("prep_time_minutes ist ungueltig")'.
237. Diese Zeile definiert den Inhalt 'else:'.
238. Diese Zeile definiert den Inhalt 'prep_time_minutes = parsed_prep'.
239. Diese Zeile definiert den Inhalt 'servings_text = _pick_value(row, "servings_text")[:120] or None'.
240. Diese Zeile definiert den Inhalt 'image_url_raw = _pick_value(row, "image_url")'.
241. Diese Zeile definiert den Inhalt 'image_url = image_url_raw[:1024] if image_url_raw else None'.
242. Diese Zeile definiert den Inhalt 'if image_url and not (image_url.startswith("http://") or image_url.startswith("https://...'.
243. Diese Zeile definiert den Inhalt 'row_warnings.append("image_url ist ungueltig und wurde ignoriert")'.
244. Diese Zeile definiert den Inhalt 'image_url = None'.
245. Diese Zeile definiert den Inhalt 'source_uuid = _pick_value(row, "source_uuid")[:120] or None'.
246. Diese Zeile definiert den Inhalt 'ingredients = _parse_admin_ingredients(_pick_value(row, "ingredients"))'.
247. Diese Zeile definiert den Inhalt 'if source_uuid:'.
248. Diese Zeile definiert den Inhalt 'if source_uuid in seen_source_uuid:'.
249. Diese Zeile definiert den Inhalt 'row_warnings.append("doppelte source_uuid in der CSV, Zeile wird uebersprungen")'.
250. Diese Zeile definiert den Inhalt 'skip_reason = "duplicate-source-uuid"'.
251. Diese Zeile definiert den Inhalt 'else:'.
252. Diese Zeile definiert den Inhalt 'seen_source_uuid.add(source_uuid)'.
253. Diese Zeile definiert den Inhalt 'skip_reason = None'.
254. Diese Zeile definiert den Inhalt 'else:'.
255. Diese Zeile definiert den Inhalt 'fallback_key = (title_normalized, category_normalized, instruction_hash)'.
256. Diese Zeile definiert den Inhalt 'if fallback_key in seen_fallback:'.
257. Diese Zeile definiert den Inhalt 'row_warnings.append("doppeltes Rezept in der CSV, Zeile wird uebersprungen")'.
258. Diese Zeile definiert den Inhalt 'skip_reason = "duplicate-fallback-key"'.
259. Diese Zeile definiert den Inhalt 'else:'.
260. Diese Zeile definiert den Inhalt 'seen_fallback.add(fallback_key)'.
261. Diese Zeile definiert den Inhalt 'skip_reason = None'.
262. Diese Zeile definiert den Inhalt 'if row_errors:'.
263. Diese Zeile definiert den Inhalt 'report.fatal_error_rows += 1'.
264. Diese Zeile definiert den Inhalt 'report.errors.extend([f"Zeile {index}: {reason}" for reason in row_errors])'.
265. Diese Zeile definiert den Inhalt 'if row_warnings:'.
266. Diese Zeile definiert den Inhalt 'report.warnings.extend([f"Zeile {index}: {reason}" for reason in row_warnings])'.
267. Diese Zeile definiert den Inhalt 'status = "ok"'.
268. Diese Zeile definiert den Inhalt 'if row_errors:'.
269. Diese Zeile definiert den Inhalt 'status = "error"'.
270. Diese Zeile definiert den Inhalt 'elif skip_reason:'.
271. Diese Zeile definiert den Inhalt 'status = "skip"'.
272. Diese Zeile definiert den Inhalt 'elif row_warnings:'.
273. Diese Zeile definiert den Inhalt 'status = "warning"'.
274. Diese Zeile definiert den Inhalt 'if len(report.preview_rows) < preview_limit:'.
275. Diese Zeile definiert den Inhalt 'report.preview_rows.append('.
276. Diese Zeile definiert den Inhalt 'AdminCSVPreviewRow('.
277. Diese Zeile definiert den Inhalt 'row_number=index,'.
278. Diese Zeile definiert den Inhalt 'title=title,'.
279. Diese Zeile definiert den Inhalt 'category=category,'.
280. Diese Zeile definiert den Inhalt 'difficulty=difficulty,'.
281. Diese Zeile definiert den Inhalt 'prep_time_minutes=str(prep_time_minutes),'.
282. Diese Zeile definiert den Inhalt 'source_uuid=source_uuid or "",'.
283. Diese Zeile definiert den Inhalt 'status=status,'.
284. Diese Zeile definiert den Inhalt 'errors=row_errors,'.
285. Diese Zeile definiert den Inhalt 'warnings=row_warnings,'.
286. Diese Zeile definiert den Inhalt ')'.
287. Diese Zeile definiert den Inhalt ')'.
288. Diese Zeile definiert den Inhalt 'prepared_rows.append('.
289. Diese Zeile definiert den Inhalt '_PreparedRow('.
290. Diese Zeile definiert den Inhalt 'row_number=index,'.
291. Diese Zeile definiert den Inhalt 'title=title,'.
292. Diese Zeile definiert den Inhalt 'title_normalized=title_normalized,'.
293. Diese Zeile definiert den Inhalt 'description=description.strip(),'.
294. Diese Zeile definiert den Inhalt 'instructions=instructions,'.
295. Diese Zeile definiert den Inhalt 'instruction_hash=instruction_hash,'.
296. Diese Zeile definiert den Inhalt 'category=category,'.
297. Diese Zeile definiert den Inhalt 'category_normalized=category_normalized,'.
298. Diese Zeile definiert den Inhalt 'difficulty=difficulty,'.
299. Diese Zeile definiert den Inhalt 'prep_time_minutes=prep_time_minutes,'.
300. Diese Zeile definiert den Inhalt 'servings_text=servings_text,'.
301. Diese Zeile definiert den Inhalt 'ingredients=ingredients,'.
302. Diese Zeile definiert den Inhalt 'image_url=image_url,'.
303. Diese Zeile definiert den Inhalt 'source_uuid=source_uuid,'.
304. Diese Zeile definiert den Inhalt 'skip_reason=skip_reason,'.
305. Diese Zeile definiert den Inhalt ')'.
306. Diese Zeile definiert den Inhalt ')'.
307. Diese Zeile definiert den Inhalt 'return prepared_rows, report'.
308. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
309. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
310. Diese Zeile definiert den Inhalt 'def _create_recipe_from_payload(db: Session, payload: _PreparedRow, creator_id: int) ->...'.
311. Diese Zeile definiert den Inhalt 'recipe = Recipe('.
312. Diese Zeile definiert den Inhalt 'title=payload.title,'.
313. Diese Zeile definiert den Inhalt 'description=payload.description,'.
314. Diese Zeile definiert den Inhalt 'instructions=payload.instructions,'.
315. Diese Zeile definiert den Inhalt 'category=payload.category,'.
316. Diese Zeile definiert den Inhalt 'prep_time_minutes=payload.prep_time_minutes,'.
317. Diese Zeile definiert den Inhalt 'difficulty=payload.difficulty,'.
318. Diese Zeile definiert den Inhalt 'creator_id=creator_id,'.
319. Diese Zeile definiert den Inhalt 'source="admin_csv",'.
320. Diese Zeile definiert den Inhalt 'source_uuid=payload.source_uuid,'.
321. Diese Zeile definiert den Inhalt 'source_url=None,'.
322. Diese Zeile definiert den Inhalt 'source_image_url=payload.image_url,'.
323. Diese Zeile definiert den Inhalt 'title_image_url=payload.image_url,'.
324. Diese Zeile definiert den Inhalt 'servings_text=payload.servings_text,'.
325. Diese Zeile definiert den Inhalt 'total_time_minutes=None,'.
326. Diese Zeile definiert den Inhalt 'is_published=True,'.
327. Diese Zeile definiert den Inhalt ')'.
328. Diese Zeile definiert den Inhalt 'db.add(recipe)'.
329. Diese Zeile definiert den Inhalt 'db.flush()'.
330. Diese Zeile definiert den Inhalt 'if payload.ingredients:'.
331. Diese Zeile definiert den Inhalt 'replace_recipe_ingredients(db, recipe, payload.ingredients)'.
332. Diese Zeile definiert den Inhalt 'return recipe'.
333. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
334. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
335. Diese Zeile definiert den Inhalt 'def _update_recipe_from_payload(db: Session, recipe: Recipe, payload: _PreparedRow) -> ...'.
336. Diese Zeile definiert den Inhalt 'recipe.description = payload.description'.
337. Diese Zeile definiert den Inhalt 'recipe.instructions = payload.instructions'.
338. Diese Zeile definiert den Inhalt 'recipe.category = payload.category'.
339. Diese Zeile definiert den Inhalt 'recipe.prep_time_minutes = payload.prep_time_minutes'.
340. Diese Zeile definiert den Inhalt 'recipe.difficulty = payload.difficulty'.
341. Diese Zeile definiert den Inhalt 'recipe.servings_text = payload.servings_text'.
342. Diese Zeile definiert den Inhalt 'if payload.image_url:'.
343. Diese Zeile definiert den Inhalt 'recipe.title_image_url = payload.image_url'.
344. Diese Zeile definiert den Inhalt 'recipe.source_image_url = payload.image_url'.
345. Diese Zeile definiert den Inhalt 'if payload.source_uuid and not recipe.source_uuid:'.
346. Diese Zeile definiert den Inhalt 'recipe.source_uuid = payload.source_uuid'.
347. Diese Zeile definiert den Inhalt 'if payload.ingredients:'.
348. Diese Zeile definiert den Inhalt 'replace_recipe_ingredients(db, recipe, payload.ingredients)'.
349. Diese Zeile definiert den Inhalt 'db.add(recipe)'.
350. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
351. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
352. Diese Zeile definiert den Inhalt 'def import_admin_csv('.
353. Diese Zeile definiert den Inhalt 'db: Session,'.
354. Diese Zeile definiert den Inhalt 'csv_bytes: bytes,'.
355. Diese Zeile definiert den Inhalt 'creator_id: int,'.
356. Diese Zeile definiert den Inhalt 'mode: ADMIN_IMPORT_MODE = "insert_only",'.
357. Diese Zeile definiert den Inhalt 'dry_run: bool = True,'.
358. Diese Zeile definiert den Inhalt 'batch_size: int = 200,'.
359. Diese Zeile definiert den Inhalt 'preview_limit: int = 20,'.
360. Diese Zeile definiert den Inhalt 'autocommit: bool = False,'.
361. Diese Zeile definiert den Inhalt ') -> AdminCSVImportReport:'.
362. Diese Zeile definiert den Inhalt 'if mode not in {"insert_only", "update_existing"}:'.
363. Diese Zeile definiert den Inhalt 'raise ValueError("mode must be 'insert_only' or 'update_existing'")'.
364. Diese Zeile definiert den Inhalt 'rows, delimiter = _parse_csv_rows(csv_bytes)'.
365. Diese Zeile definiert den Inhalt 'prepared_rows, report = _prepare_rows(rows, mode, preview_limit)'.
366. Diese Zeile definiert den Inhalt 'report.delimiter = delimiter'.
367. Diese Zeile definiert den Inhalt 'report.dry_run = dry_run'.
368. Diese Zeile definiert den Inhalt 'if report.fatal_error_rows > 0:'.
369. Diese Zeile definiert den Inhalt 'return report'.
370. Diese Zeile definiert den Inhalt 'pending_writes = 0'.
371. Diese Zeile definiert den Inhalt 'for payload in prepared_rows:'.
372. Diese Zeile definiert den Inhalt 'if payload.skip_reason:'.
373. Diese Zeile definiert den Inhalt 'report.skipped += 1'.
374. Diese Zeile definiert den Inhalt 'continue'.
375. Diese Zeile definiert den Inhalt 'existing = _find_existing_recipe_for_admin(db, payload)'.
376. Diese Zeile definiert den Inhalt 'if existing and mode == "insert_only":'.
377. Diese Zeile definiert den Inhalt 'report.skipped += 1'.
378. Diese Zeile definiert den Inhalt 'continue'.
379. Diese Zeile definiert den Inhalt 'if existing and mode == "update_existing":'.
380. Diese Zeile definiert den Inhalt 'if not dry_run:'.
381. Diese Zeile definiert den Inhalt '_update_recipe_from_payload(db, existing, payload)'.
382. Diese Zeile definiert den Inhalt 'pending_writes += 1'.
383. Diese Zeile definiert den Inhalt 'report.updated += 1'.
384. Diese Zeile definiert den Inhalt 'else:'.
385. Diese Zeile definiert den Inhalt 'if not dry_run:'.
386. Diese Zeile definiert den Inhalt '_create_recipe_from_payload(db, payload, creator_id)'.
387. Diese Zeile definiert den Inhalt 'pending_writes += 1'.
388. Diese Zeile definiert den Inhalt 'report.inserted += 1'.
389. Diese Zeile definiert den Inhalt 'if not dry_run and pending_writes >= batch_size:'.
390. Diese Zeile definiert den Inhalt 'if autocommit:'.
391. Diese Zeile definiert den Inhalt 'db.commit()'.
392. Diese Zeile definiert den Inhalt 'else:'.
393. Diese Zeile definiert den Inhalt 'db.flush()'.
394. Diese Zeile definiert den Inhalt 'pending_writes = 0'.
395. Diese Zeile definiert den Inhalt 'if not dry_run and pending_writes > 0:'.
396. Diese Zeile definiert den Inhalt 'if autocommit:'.
397. Diese Zeile definiert den Inhalt 'db.commit()'.
398. Diese Zeile definiert den Inhalt 'else:'.
399. Diese Zeile definiert den Inhalt 'db.flush()'.
400. Diese Zeile definiert den Inhalt 'return report'.
401. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
402. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
403. Diese Zeile definiert den Inhalt 'def build_csv_template_bytes() -> bytes:'.
404. Diese Zeile definiert den Inhalt 'buffer = io.StringIO()'.
405. Diese Zeile definiert den Inhalt 'writer = csv.writer(buffer, delimiter=";")'.
406. Diese Zeile definiert den Inhalt 'writer.writerow(CANONICAL_CSV_COLUMNS)'.
407. Diese Zeile definiert den Inhalt 'writer.writerow('.
408. Diese Zeile definiert den Inhalt '['.
409. Diese Zeile definiert den Inhalt '"Spaghetti Carbonara",'.
410. Diese Zeile definiert den Inhalt '"Pasta kochen. Speck anbraten. Mit Ei-Kaese-Mischung verruehren.",'.
411. Diese Zeile definiert den Inhalt '"Klassische Carbonara mit Ei und Pecorino.",'.
412. Diese Zeile definiert den Inhalt '"Pasta",'.
413. Diese Zeile definiert den Inhalt '"medium",'.
414. Diese Zeile definiert den Inhalt '"25",'.
415. Diese Zeile definiert den Inhalt '"2 Portionen",'.
416. Diese Zeile definiert den Inhalt '"200g Spaghetti | 120g Guanciale | 2 Eier | 50g Pecorino",'.
417. Diese Zeile definiert den Inhalt '"https://example.com/carbonara.jpg",'.
418. Diese Zeile definiert den Inhalt '"admin-demo-001",'.
419. Diese Zeile definiert den Inhalt ']'.
420. Diese Zeile definiert den Inhalt ')'.
421. Diese Zeile definiert den Inhalt 'content = buffer.getvalue()'.
422. Diese Zeile definiert den Inhalt 'return ("\ufeff" + content).encode("utf-8")'.
423. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
424. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
425. Diese Zeile definiert den Inhalt 'def build_csv_example_bytes() -> bytes:'.
426. Diese Zeile definiert den Inhalt 'buffer = io.StringIO()'.
427. Diese Zeile definiert den Inhalt 'writer = csv.writer(buffer, delimiter=";")'.
428. Diese Zeile definiert den Inhalt 'writer.writerow(CANONICAL_CSV_COLUMNS)'.
429. Diese Zeile definiert den Inhalt 'writer.writerow('.
430. Diese Zeile definiert den Inhalt '['.
431. Diese Zeile definiert den Inhalt '"Linsensuppe",'.
432. Diese Zeile definiert den Inhalt '"Zwiebeln anschwitzen. Linsen dazugeben. Mit Bruehe kochen.",'.
433. Diese Zeile definiert den Inhalt '"Herzhafte Suppe fuer kalte Tage.",'.
434. Diese Zeile definiert den Inhalt '"Suppen",'.
435. Diese Zeile definiert den Inhalt '"easy",'.
436. Diese Zeile definiert den Inhalt '"35",'.
437. Diese Zeile definiert den Inhalt '"4 Portionen",'.
438. Diese Zeile definiert den Inhalt '"250g Linsen | 1 Zwiebel | 2 Karotten | 1L Gemuesebruehe",'.
439. Diese Zeile definiert den Inhalt '"",'.
440. Diese Zeile definiert den Inhalt '"admin-demo-002",'.
441. Diese Zeile definiert den Inhalt ']'.
442. Diese Zeile definiert den Inhalt ')'.
443. Diese Zeile definiert den Inhalt 'writer.writerow('.
444. Diese Zeile definiert den Inhalt '['.
445. Diese Zeile definiert den Inhalt '"Schneller Obstsalat",'.
446. Diese Zeile definiert den Inhalt '"Obst schneiden und mit Zitronensaft vermengen.",'.
447. Diese Zeile definiert den Inhalt '"Frischer Salat mit saisonalem Obst.",'.
448. Diese Zeile definiert den Inhalt '"Dessert",'.
449. Diese Zeile definiert den Inhalt '"easy",'.
450. Diese Zeile definiert den Inhalt '"10",'.
451. Diese Zeile definiert den Inhalt '"3 Portionen",'.
452. Diese Zeile definiert den Inhalt '"[\"2 Aepfel\", \"1 Banane\", \"1 Orange\", \"1 TL Zitronensaft\"]",'.
453. Diese Zeile definiert den Inhalt '"https://example.com/obstsalat.jpg",'.
454. Diese Zeile definiert den Inhalt '"admin-demo-003",'.
455. Diese Zeile definiert den Inhalt ']'.
456. Diese Zeile definiert den Inhalt ')'.
457. Diese Zeile definiert den Inhalt 'writer.writerow('.
458. Diese Zeile definiert den Inhalt '['.
459. Diese Zeile definiert den Inhalt '"Ofengemuese",'.
460. Diese Zeile definiert den Inhalt '"Gemuese schneiden, wuerzen und 30 Minuten backen.",'.
461. Diese Zeile definiert den Inhalt '"Knackiges Ofengemuese.",'.
462. Diese Zeile definiert den Inhalt '"Hauptgericht",'.
463. Diese Zeile definiert den Inhalt '"medium",'.
464. Diese Zeile definiert den Inhalt '"40",'.
465. Diese Zeile definiert den Inhalt '"2 Portionen",'.
466. Diese Zeile definiert den Inhalt '"2 Karotten | 1 Zucchini | 1 Paprika | 2 EL Olivenoel",'.
467. Diese Zeile definiert den Inhalt '"",'.
468. Diese Zeile definiert den Inhalt '"",'.
469. Diese Zeile definiert den Inhalt ']'.
470. Diese Zeile definiert den Inhalt ')'.
471. Diese Zeile definiert den Inhalt 'content = buffer.getvalue()'.
472. Diese Zeile definiert den Inhalt 'return ("\ufeff" + content).encode("utf-8")'.

## app/routers/recipes.py
```python
from io import BytesIO

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status
from fastapi.responses import RedirectResponse, Response, StreamingResponse
from sqlalchemy import and_, desc, func, select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.database import get_db
from app.dependencies import get_admin_user, get_current_user, get_current_user_optional, template_context
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
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    recipe = fetch_recipe_or_404(db, recipe_id)
    ensure_recipe_visible(recipe, current_user)
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
```
ZEILEN-ERKL?RUNG
1. Diese Zeile definiert den Inhalt 'from io import BytesIO'.
2. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
3. Diese Zeile definiert den Inhalt 'from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile,...'.
4. Diese Zeile definiert den Inhalt 'from fastapi.responses import RedirectResponse, Response, StreamingResponse'.
5. Diese Zeile definiert den Inhalt 'from sqlalchemy import and_, desc, func, select'.
6. Diese Zeile definiert den Inhalt 'from sqlalchemy.orm import Session, joinedload, selectinload'.
7. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
8. Diese Zeile definiert den Inhalt 'from app.database import get_db'.
9. Diese Zeile definiert den Inhalt 'from app.dependencies import get_admin_user, get_current_user, get_current_user_optiona...'.
10. Diese Zeile definiert den Inhalt 'from app.image_utils import ImageValidationError, safe_image_filename, validate_image_u...'.
11. Diese Zeile definiert den Inhalt 'from app.models import Favorite, Ingredient, Recipe, RecipeImage, RecipeIngredient, Rev...'.
12. Diese Zeile definiert den Inhalt 'from app.pdf_service import build_recipe_pdf'.
13. Diese Zeile definiert den Inhalt 'from app.rate_limit import key_by_user_or_ip, limiter'.
14. Diese Zeile definiert den Inhalt 'from app.services import ('.
15. Diese Zeile definiert den Inhalt 'DEFAULT_CATEGORY,'.
16. Diese Zeile definiert den Inhalt 'build_category_index,'.
17. Diese Zeile definiert den Inhalt 'can_manage_recipe,'.
18. Diese Zeile definiert den Inhalt 'get_distinct_categories,'.
19. Diese Zeile definiert den Inhalt 'normalize_category,'.
20. Diese Zeile definiert den Inhalt 'parse_ingredient_text,'.
21. Diese Zeile definiert den Inhalt 'replace_recipe_ingredients,'.
22. Diese Zeile definiert den Inhalt 'resolve_title_image_url,'.
23. Diese Zeile definiert den Inhalt 'sanitize_difficulty,'.
24. Diese Zeile definiert den Inhalt ')'.
25. Diese Zeile definiert den Inhalt 'from app.views import redirect, templates'.
26. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
27. Diese Zeile definiert den Inhalt 'router = APIRouter(tags=["recipes"])'.
28. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
29. Diese Zeile definiert den Inhalt 'PAGE_SIZE_DEFAULT = 20'.
30. Diese Zeile definiert den Inhalt 'PAGE_SIZE_OPTIONS = (10, 20, 40, 80)'.
31. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
32. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
33. Diese Zeile definiert den Inhalt 'def parse_positive_int(value: str, field_name: str) -> int:'.
34. Diese Zeile definiert den Inhalt 'try:'.
35. Diese Zeile definiert den Inhalt 'parsed = int(value)'.
36. Diese Zeile definiert den Inhalt 'except ValueError as exc:'.
37. Diese Zeile definiert den Inhalt 'raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{field_name} must...'.
38. Diese Zeile definiert den Inhalt 'if parsed <= 0:'.
39. Diese Zeile definiert den Inhalt 'raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{field_name} must...'.
40. Diese Zeile definiert den Inhalt 'return parsed'.
41. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
42. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
43. Diese Zeile definiert den Inhalt 'def normalize_image_url(value: str) -> str | None:'.
44. Diese Zeile definiert den Inhalt 'cleaned = value.strip()'.
45. Diese Zeile definiert den Inhalt 'if not cleaned:'.
46. Diese Zeile definiert den Inhalt 'return None'.
47. Diese Zeile definiert den Inhalt 'if not (cleaned.startswith("http://") or cleaned.startswith("https://")):'.
48. Diese Zeile definiert den Inhalt 'raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="title_image_url mu...'.
49. Diese Zeile definiert den Inhalt 'return cleaned'.
50. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
51. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
52. Diese Zeile definiert den Inhalt 'def build_pagination_items(page: int, total_pages: int) -> list[int | None]:'.
53. Diese Zeile definiert den Inhalt 'if total_pages <= 7:'.
54. Diese Zeile definiert den Inhalt 'return list(range(1, total_pages + 1))'.
55. Diese Zeile definiert den Inhalt 'if page <= 4:'.
56. Diese Zeile definiert den Inhalt 'return [1, 2, 3, 4, 5, None, total_pages]'.
57. Diese Zeile definiert den Inhalt 'if page >= total_pages - 3:'.
58. Diese Zeile definiert den Inhalt 'return [1, None, total_pages - 4, total_pages - 3, total_pages - 2, total_pages - 1, to...'.
59. Diese Zeile definiert den Inhalt 'return [1, None, page - 1, page, page + 1, None, total_pages]'.
60. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
61. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
62. Diese Zeile definiert den Inhalt 'def resolve_category_value(category_select: str, category_new: str, category_legacy: st...'.
63. Diese Zeile definiert den Inhalt 'if category_select and category_select != "__new__":'.
64. Diese Zeile definiert den Inhalt 'return normalize_category(category_select)'.
65. Diese Zeile definiert den Inhalt 'if category_new.strip():'.
66. Diese Zeile definiert den Inhalt 'return normalize_category(category_new)'.
67. Diese Zeile definiert den Inhalt 'if category_legacy.strip():'.
68. Diese Zeile definiert den Inhalt 'return normalize_category(category_legacy)'.
69. Diese Zeile definiert den Inhalt 'return DEFAULT_CATEGORY'.
70. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
71. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
72. Diese Zeile definiert den Inhalt 'def fetch_recipe_or_404(db: Session, recipe_id: int) -> Recipe:'.
73. Diese Zeile definiert den Inhalt 'recipe = db.scalar('.
74. Diese Zeile definiert den Inhalt 'select(Recipe)'.
75. Diese Zeile definiert den Inhalt '.where(Recipe.id == recipe_id)'.
76. Diese Zeile definiert den Inhalt '.options('.
77. Diese Zeile definiert den Inhalt 'joinedload(Recipe.creator),'.
78. Diese Zeile definiert den Inhalt 'selectinload(Recipe.recipe_ingredients).joinedload(RecipeIngredient.ingredient),'.
79. Diese Zeile definiert den Inhalt 'selectinload(Recipe.reviews).joinedload(Review.user),'.
80. Diese Zeile definiert den Inhalt 'selectinload(Recipe.images),'.
81. Diese Zeile definiert den Inhalt ')'.
82. Diese Zeile definiert den Inhalt ')'.
83. Diese Zeile definiert den Inhalt 'if not recipe:'.
84. Diese Zeile definiert den Inhalt 'raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found.")'.
85. Diese Zeile definiert den Inhalt 'return recipe'.
86. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
87. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
88. Diese Zeile definiert den Inhalt 'def ensure_recipe_visible(recipe: Recipe, current_user: User | None) -> None:'.
89. Diese Zeile definiert den Inhalt 'if recipe.is_published:'.
90. Diese Zeile definiert den Inhalt 'return'.
91. Diese Zeile definiert den Inhalt 'if current_user and (current_user.role == "admin" or current_user.id == recipe.creator_...'.
92. Diese Zeile definiert den Inhalt 'return'.
93. Diese Zeile definiert den Inhalt 'raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found.")'.
94. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
95. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
96. Diese Zeile definiert den Inhalt 'def ensure_recipe_access(user: User, recipe: Recipe) -> None:'.
97. Diese Zeile definiert den Inhalt 'if not can_manage_recipe(user, recipe):'.
98. Diese Zeile definiert den Inhalt 'raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissio...'.
99. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
100. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
101. Diese Zeile definiert den Inhalt 'def get_primary_image(recipe: Recipe) -> RecipeImage | None:'.
102. Diese Zeile definiert den Inhalt 'for image in recipe.images:'.
103. Diese Zeile definiert den Inhalt 'if image.is_primary:'.
104. Diese Zeile definiert den Inhalt 'return image'.
105. Diese Zeile definiert den Inhalt 'return recipe.images[0] if recipe.images else None'.
106. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
107. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
108. Diese Zeile definiert den Inhalt 'def set_recipe_primary_image(db: Session, recipe: Recipe, image_id: int) -> None:'.
109. Diese Zeile definiert den Inhalt 'for image in recipe.images:'.
110. Diese Zeile definiert den Inhalt 'image.is_primary = image.id == image_id'.
111. Diese Zeile definiert den Inhalt 'db.flush()'.
112. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
113. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
114. Diese Zeile definiert den Inhalt 'def maybe_promote_primary_after_delete(db: Session, recipe: Recipe) -> None:'.
115. Diese Zeile definiert den Inhalt 'remaining = list(recipe.images)'.
116. Diese Zeile definiert den Inhalt 'if not remaining:'.
117. Diese Zeile definiert den Inhalt 'return'.
118. Diese Zeile definiert den Inhalt 'if any(image.is_primary for image in remaining):'.
119. Diese Zeile definiert den Inhalt 'return'.
120. Diese Zeile definiert den Inhalt 'remaining[0].is_primary = True'.
121. Diese Zeile definiert den Inhalt 'db.flush()'.
122. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
123. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
124. Diese Zeile definiert den Inhalt 'def render_image_section(request: Request, db: Session, recipe_id: int, current_user: U...'.
125. Diese Zeile definiert den Inhalt 'recipe = fetch_recipe_or_404(db, recipe_id)'.
126. Diese Zeile definiert den Inhalt 'primary_image = get_primary_image(recipe)'.
127. Diese Zeile definiert den Inhalt 'return templates.TemplateResponse('.
128. Diese Zeile definiert den Inhalt '"partials/recipe_images.html",'.
129. Diese Zeile definiert den Inhalt 'template_context('.
130. Diese Zeile definiert den Inhalt 'request,'.
131. Diese Zeile definiert den Inhalt 'current_user,'.
132. Diese Zeile definiert den Inhalt 'recipe=recipe,'.
133. Diese Zeile definiert den Inhalt 'primary_image=primary_image,'.
134. Diese Zeile definiert den Inhalt '),'.
135. Diese Zeile definiert den Inhalt ')'.
136. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
137. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
138. Diese Zeile definiert den Inhalt '@router.get("/")'.
139. Diese Zeile definiert den Inhalt 'def home_page('.
140. Diese Zeile definiert den Inhalt 'request: Request,'.
141. Diese Zeile definiert den Inhalt 'page: int = 1,'.
142. Diese Zeile definiert den Inhalt 'per_page: int = PAGE_SIZE_DEFAULT,'.
143. Diese Zeile definiert den Inhalt 'sort: str = "date",'.
144. Diese Zeile definiert den Inhalt 'title: str = "",'.
145. Diese Zeile definiert den Inhalt 'category: str = "",'.
146. Diese Zeile definiert den Inhalt 'difficulty: str = "",'.
147. Diese Zeile definiert den Inhalt 'ingredient: str = "",'.
148. Diese Zeile definiert den Inhalt 'db: Session = Depends(get_db),'.
149. Diese Zeile definiert den Inhalt 'current_user: User | None = Depends(get_current_user_optional),'.
150. Diese Zeile definiert den Inhalt '):'.
151. Diese Zeile definiert den Inhalt 'page = max(page, 1)'.
152. Diese Zeile definiert den Inhalt 'if per_page not in PAGE_SIZE_OPTIONS:'.
153. Diese Zeile definiert den Inhalt 'per_page = PAGE_SIZE_DEFAULT'.
154. Diese Zeile definiert den Inhalt 'category_index = build_category_index(db, only_published=True)'.
155. Diese Zeile definiert den Inhalt 'category_options = sorted(category_index.keys(), key=str.casefold)'.
156. Diese Zeile definiert den Inhalt 'selected_category = normalize_category(category, allow_empty=True)'.
157. Diese Zeile definiert den Inhalt 'if selected_category and selected_category not in category_index:'.
158. Diese Zeile definiert den Inhalt 'category_index[selected_category] = [selected_category]'.
159. Diese Zeile definiert den Inhalt 'category_options = sorted(category_index.keys(), key=str.casefold)'.
160. Diese Zeile definiert den Inhalt 'review_stats = ('.
161. Diese Zeile definiert den Inhalt 'select('.
162. Diese Zeile definiert den Inhalt 'Review.recipe_id.label("recipe_id"),'.
163. Diese Zeile definiert den Inhalt 'func.avg(Review.rating).label("avg_rating"),'.
164. Diese Zeile definiert den Inhalt 'func.count(Review.id).label("review_count"),'.
165. Diese Zeile definiert den Inhalt ')'.
166. Diese Zeile definiert den Inhalt '.group_by(Review.recipe_id)'.
167. Diese Zeile definiert den Inhalt '.subquery()'.
168. Diese Zeile definiert den Inhalt ')'.
169. Diese Zeile definiert den Inhalt 'stmt = ('.
170. Diese Zeile definiert den Inhalt 'select('.
171. Diese Zeile definiert den Inhalt 'Recipe,'.
172. Diese Zeile definiert den Inhalt 'func.coalesce(review_stats.c.avg_rating, 0).label("avg_rating"),'.
173. Diese Zeile definiert den Inhalt 'func.coalesce(review_stats.c.review_count, 0).label("review_count"),'.
174. Diese Zeile definiert den Inhalt ')'.
175. Diese Zeile definiert den Inhalt '.outerjoin(review_stats, Recipe.id == review_stats.c.recipe_id)'.
176. Diese Zeile definiert den Inhalt '.where(Recipe.is_published.is_(True))'.
177. Diese Zeile definiert den Inhalt '.options(selectinload(Recipe.images))'.
178. Diese Zeile definiert den Inhalt ')'.
179. Diese Zeile definiert den Inhalt 'if title.strip():'.
180. Diese Zeile definiert den Inhalt 'like = f"%{title.strip()}%"'.
181. Diese Zeile definiert den Inhalt 'stmt = stmt.where(Recipe.title.ilike(like))'.
182. Diese Zeile definiert den Inhalt 'if selected_category:'.
183. Diese Zeile definiert den Inhalt 'stmt = stmt.where(Recipe.category.in_(category_index.get(selected_category, [selected_c...'.
184. Diese Zeile definiert den Inhalt 'if difficulty.strip():'.
185. Diese Zeile definiert den Inhalt 'stmt = stmt.where(Recipe.difficulty == sanitize_difficulty(difficulty))'.
186. Diese Zeile definiert den Inhalt 'if ingredient.strip():'.
187. Diese Zeile definiert den Inhalt 'like = f"%{ingredient.strip().lower()}%"'.
188. Diese Zeile definiert den Inhalt 'ingredient_recipe_ids = ('.
189. Diese Zeile definiert den Inhalt 'select(RecipeIngredient.recipe_id)'.
190. Diese Zeile definiert den Inhalt '.join(Ingredient, Ingredient.id == RecipeIngredient.ingredient_id)'.
191. Diese Zeile definiert den Inhalt '.where(Ingredient.name.ilike(like))'.
192. Diese Zeile definiert den Inhalt '.subquery()'.
193. Diese Zeile definiert den Inhalt ')'.
194. Diese Zeile definiert den Inhalt 'stmt = stmt.where(Recipe.id.in_(select(ingredient_recipe_ids.c.recipe_id)))'.
195. Diese Zeile definiert den Inhalt 'if sort == "prep_time":'.
196. Diese Zeile definiert den Inhalt 'stmt = stmt.order_by(Recipe.prep_time_minutes.asc(), Recipe.created_at.desc())'.
197. Diese Zeile definiert den Inhalt 'elif sort == "avg_rating":'.
198. Diese Zeile definiert den Inhalt 'stmt = stmt.order_by(desc("avg_rating"), Recipe.created_at.desc())'.
199. Diese Zeile definiert den Inhalt 'else:'.
200. Diese Zeile definiert den Inhalt 'stmt = stmt.order_by(Recipe.created_at.desc())'.
201. Diese Zeile definiert den Inhalt 'total = db.scalar(select(func.count()).select_from(stmt.subquery()))'.
202. Diese Zeile definiert den Inhalt 'pages = max((total + per_page - 1) // per_page, 1)'.
203. Diese Zeile definiert den Inhalt 'page = min(page, pages)'.
204. Diese Zeile definiert den Inhalt 'rows = db.execute(stmt.offset((page - 1) * per_page).limit(per_page)).all()'.
205. Diese Zeile definiert den Inhalt 'recipes_data = [{"recipe": row[0], "avg_rating": float(row[1] or 0), "review_count": in...'.
206. Diese Zeile definiert den Inhalt 'start_item = ((page - 1) * per_page + 1) if total > 0 else 0'.
207. Diese Zeile definiert den Inhalt 'end_item = min(page * per_page, total)'.
208. Diese Zeile definiert den Inhalt 'pagination_items = build_pagination_items(page, pages)'.
209. Diese Zeile definiert den Inhalt 'context = template_context('.
210. Diese Zeile definiert den Inhalt 'request,'.
211. Diese Zeile definiert den Inhalt 'current_user,'.
212. Diese Zeile definiert den Inhalt 'recipes_data=recipes_data,'.
213. Diese Zeile definiert den Inhalt 'page=page,'.
214. Diese Zeile definiert den Inhalt 'pages=pages,'.
215. Diese Zeile definiert den Inhalt 'total_pages=pages,'.
216. Diese Zeile definiert den Inhalt 'per_page=per_page,'.
217. Diese Zeile definiert den Inhalt 'per_page_options=PAGE_SIZE_OPTIONS,'.
218. Diese Zeile definiert den Inhalt 'category_options=category_options,'.
219. Diese Zeile definiert den Inhalt 'total=total,'.
220. Diese Zeile definiert den Inhalt 'total_count=total,'.
221. Diese Zeile definiert den Inhalt 'start_item=start_item,'.
222. Diese Zeile definiert den Inhalt 'end_item=end_item,'.
223. Diese Zeile definiert den Inhalt 'pagination_items=pagination_items,'.
224. Diese Zeile definiert den Inhalt 'sort=sort,'.
225. Diese Zeile definiert den Inhalt 'title=title,'.
226. Diese Zeile definiert den Inhalt 'category=selected_category,'.
227. Diese Zeile definiert den Inhalt 'difficulty=difficulty,'.
228. Diese Zeile definiert den Inhalt 'ingredient=ingredient,'.
229. Diese Zeile definiert den Inhalt ')'.
230. Diese Zeile definiert den Inhalt 'if request.headers.get("HX-Request") == "true":'.
231. Diese Zeile definiert den Inhalt 'return templates.TemplateResponse("partials/recipe_list.html", context)'.
232. Diese Zeile definiert den Inhalt 'return templates.TemplateResponse("home.html", context)'.
233. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
234. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
235. Diese Zeile definiert den Inhalt '@router.get("/recipes/new")'.
236. Diese Zeile definiert den Inhalt 'def create_recipe_page('.
237. Diese Zeile definiert den Inhalt 'request: Request,'.
238. Diese Zeile definiert den Inhalt 'db: Session = Depends(get_db),'.
239. Diese Zeile definiert den Inhalt 'current_user: User = Depends(get_admin_user),'.
240. Diese Zeile definiert den Inhalt '):'.
241. Diese Zeile definiert den Inhalt 'return templates.TemplateResponse('.
242. Diese Zeile definiert den Inhalt '"recipe_form.html",'.
243. Diese Zeile definiert den Inhalt 'template_context('.
244. Diese Zeile definiert den Inhalt 'request,'.
245. Diese Zeile definiert den Inhalt 'current_user,'.
246. Diese Zeile definiert den Inhalt 'recipe=None,'.
247. Diese Zeile definiert den Inhalt 'error=None,'.
248. Diese Zeile definiert den Inhalt 'form_mode="create",'.
249. Diese Zeile definiert den Inhalt 'category_options=get_distinct_categories(db, only_published=False),'.
250. Diese Zeile definiert den Inhalt 'selected_category=DEFAULT_CATEGORY,'.
251. Diese Zeile definiert den Inhalt 'category_new_value="",'.
252. Diese Zeile definiert den Inhalt '),'.
253. Diese Zeile definiert den Inhalt ')'.
254. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
255. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
256. Diese Zeile definiert den Inhalt '@router.post("/recipes")'.
257. Diese Zeile definiert den Inhalt '@router.post("/recipes/new")'.
258. Diese Zeile definiert den Inhalt 'async def create_recipe_submit('.
259. Diese Zeile definiert den Inhalt 'request: Request,'.
260. Diese Zeile definiert den Inhalt 'title: str = Form(...),'.
261. Diese Zeile definiert den Inhalt 'description: str = Form(...),'.
262. Diese Zeile definiert den Inhalt 'instructions: str = Form(...),'.
263. Diese Zeile definiert den Inhalt 'category_select: str = Form(DEFAULT_CATEGORY),'.
264. Diese Zeile definiert den Inhalt 'category_new: str = Form(""),'.
265. Diese Zeile definiert den Inhalt 'category: str = Form(""),'.
266. Diese Zeile definiert den Inhalt 'title_image_url: str = Form(""),'.
267. Diese Zeile definiert den Inhalt 'prep_time_minutes: str = Form(...),'.
268. Diese Zeile definiert den Inhalt 'difficulty: str = Form(...),'.
269. Diese Zeile definiert den Inhalt 'ingredients_text: str = Form(""),'.
270. Diese Zeile definiert den Inhalt 'image: UploadFile | None = File(None),'.
271. Diese Zeile definiert den Inhalt 'db: Session = Depends(get_db),'.
272. Diese Zeile definiert den Inhalt 'current_user: User = Depends(get_admin_user),'.
273. Diese Zeile definiert den Inhalt '):'.
274. Diese Zeile definiert den Inhalt 'prep_time = parse_positive_int(prep_time_minutes, "prep_time_minutes")'.
275. Diese Zeile definiert den Inhalt 'normalized_difficulty = sanitize_difficulty(difficulty)'.
276. Diese Zeile definiert den Inhalt 'if not title.strip() or not instructions.strip():'.
277. Diese Zeile definiert den Inhalt 'raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Title and instruct...'.
278. Diese Zeile definiert den Inhalt 'recipe = Recipe('.
279. Diese Zeile definiert den Inhalt 'title=title.strip(),'.
280. Diese Zeile definiert den Inhalt 'title_image_url=normalize_image_url(title_image_url),'.
281. Diese Zeile definiert den Inhalt 'source="admin_manual",'.
282. Diese Zeile definiert den Inhalt 'description=description.strip(),'.
283. Diese Zeile definiert den Inhalt 'instructions=instructions.strip(),'.
284. Diese Zeile definiert den Inhalt 'category=resolve_category_value(category_select, category_new, category),'.
285. Diese Zeile definiert den Inhalt 'prep_time_minutes=prep_time,'.
286. Diese Zeile definiert den Inhalt 'difficulty=normalized_difficulty,'.
287. Diese Zeile definiert den Inhalt 'creator_id=current_user.id,'.
288. Diese Zeile definiert den Inhalt 'is_published=True,'.
289. Diese Zeile definiert den Inhalt ')'.
290. Diese Zeile definiert den Inhalt 'db.add(recipe)'.
291. Diese Zeile definiert den Inhalt 'db.flush()'.
292. Diese Zeile definiert den Inhalt 'ingredient_entries = parse_ingredient_text(ingredients_text)'.
293. Diese Zeile definiert den Inhalt 'replace_recipe_ingredients(db, recipe, ingredient_entries)'.
294. Diese Zeile definiert den Inhalt 'if image and image.filename:'.
295. Diese Zeile definiert den Inhalt 'data = await image.read()'.
296. Diese Zeile definiert den Inhalt 'try:'.
297. Diese Zeile definiert den Inhalt 'validate_image_upload((image.content_type or "").lower(), data)'.
298. Diese Zeile definiert den Inhalt 'except ImageValidationError as exc:'.
299. Diese Zeile definiert den Inhalt 'raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc'.
300. Diese Zeile definiert den Inhalt 'image_content_type = (image.content_type or "application/octet-stream").lower()'.
301. Diese Zeile definiert den Inhalt 'db.add('.
302. Diese Zeile definiert den Inhalt 'RecipeImage('.
303. Diese Zeile definiert den Inhalt 'recipe_id=recipe.id,'.
304. Diese Zeile definiert den Inhalt 'filename=safe_image_filename(image.filename or "", image_content_type),'.
305. Diese Zeile definiert den Inhalt 'content_type=image_content_type,'.
306. Diese Zeile definiert den Inhalt 'data=data,'.
307. Diese Zeile definiert den Inhalt 'is_primary=True,'.
308. Diese Zeile definiert den Inhalt ')'.
309. Diese Zeile definiert den Inhalt ')'.
310. Diese Zeile definiert den Inhalt 'db.commit()'.
311. Diese Zeile definiert den Inhalt 'return redirect(f"/recipes/{recipe.id}")'.
312. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
313. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
314. Diese Zeile definiert den Inhalt '@router.get("/recipes/{recipe_id}")'.
315. Diese Zeile definiert den Inhalt 'def recipe_detail('.
316. Diese Zeile definiert den Inhalt 'request: Request,'.
317. Diese Zeile definiert den Inhalt 'recipe_id: int,'.
318. Diese Zeile definiert den Inhalt 'db: Session = Depends(get_db),'.
319. Diese Zeile definiert den Inhalt 'current_user: User | None = Depends(get_current_user_optional),'.
320. Diese Zeile definiert den Inhalt '):'.
321. Diese Zeile definiert den Inhalt 'recipe = fetch_recipe_or_404(db, recipe_id)'.
322. Diese Zeile definiert den Inhalt 'ensure_recipe_visible(recipe, current_user)'.
323. Diese Zeile definiert den Inhalt 'avg_rating = db.scalar(select(func.coalesce(func.avg(Review.rating), 0)).where(Review.r...'.
324. Diese Zeile definiert den Inhalt 'review_count = db.scalar(select(func.count(Review.id)).where(Review.recipe_id == recipe...'.
325. Diese Zeile definiert den Inhalt 'primary_image = get_primary_image(recipe)'.
326. Diese Zeile definiert den Inhalt 'is_favorite = False'.
327. Diese Zeile definiert den Inhalt 'if current_user:'.
328. Diese Zeile definiert den Inhalt 'is_favorite = db.scalar('.
329. Diese Zeile definiert den Inhalt 'select(Favorite).where(and_(Favorite.user_id == current_user.id, Favorite.recipe_id == ...'.
330. Diese Zeile definiert den Inhalt ') is not None'.
331. Diese Zeile definiert den Inhalt 'return templates.TemplateResponse('.
332. Diese Zeile definiert den Inhalt '"recipe_detail.html",'.
333. Diese Zeile definiert den Inhalt 'template_context('.
334. Diese Zeile definiert den Inhalt 'request,'.
335. Diese Zeile definiert den Inhalt 'current_user,'.
336. Diese Zeile definiert den Inhalt 'recipe=recipe,'.
337. Diese Zeile definiert den Inhalt 'avg_rating=float(avg_rating),'.
338. Diese Zeile definiert den Inhalt 'review_count=int(review_count),'.
339. Diese Zeile definiert den Inhalt 'is_favorite=is_favorite,'.
340. Diese Zeile definiert den Inhalt 'primary_image=primary_image,'.
341. Diese Zeile definiert den Inhalt '),'.
342. Diese Zeile definiert den Inhalt ')'.
343. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
344. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
345. Diese Zeile definiert den Inhalt '@router.get("/recipes/{recipe_id}/edit")'.
346. Diese Zeile definiert den Inhalt 'def edit_recipe_page('.
347. Diese Zeile definiert den Inhalt 'request: Request,'.
348. Diese Zeile definiert den Inhalt 'recipe_id: int,'.
349. Diese Zeile definiert den Inhalt 'db: Session = Depends(get_db),'.
350. Diese Zeile definiert den Inhalt 'current_user: User = Depends(get_current_user),'.
351. Diese Zeile definiert den Inhalt '):'.
352. Diese Zeile definiert den Inhalt 'recipe = fetch_recipe_or_404(db, recipe_id)'.
353. Diese Zeile definiert den Inhalt 'ensure_recipe_access(current_user, recipe)'.
354. Diese Zeile definiert den Inhalt 'selected_category = normalize_category(recipe.category)'.
355. Diese Zeile definiert den Inhalt 'category_options = get_distinct_categories(db)'.
356. Diese Zeile definiert den Inhalt 'if selected_category not in category_options:'.
357. Diese Zeile definiert den Inhalt 'category_options = sorted([*category_options, selected_category], key=str.casefold)'.
358. Diese Zeile definiert den Inhalt 'ingredients_text = "\n".join('.
359. Diese Zeile definiert den Inhalt 'f"{link.ingredient.name}|{link.quantity_text}|{link.grams or ''}".rstrip("|")'.
360. Diese Zeile definiert den Inhalt 'for link in recipe.recipe_ingredients'.
361. Diese Zeile definiert den Inhalt ')'.
362. Diese Zeile definiert den Inhalt 'return templates.TemplateResponse('.
363. Diese Zeile definiert den Inhalt '"recipe_form.html",'.
364. Diese Zeile definiert den Inhalt 'template_context('.
365. Diese Zeile definiert den Inhalt 'request,'.
366. Diese Zeile definiert den Inhalt 'current_user,'.
367. Diese Zeile definiert den Inhalt 'recipe=recipe,'.
368. Diese Zeile definiert den Inhalt 'ingredients_text=ingredients_text,'.
369. Diese Zeile definiert den Inhalt 'error=None,'.
370. Diese Zeile definiert den Inhalt 'form_mode="edit",'.
371. Diese Zeile definiert den Inhalt 'category_options=category_options,'.
372. Diese Zeile definiert den Inhalt 'selected_category=selected_category,'.
373. Diese Zeile definiert den Inhalt 'category_new_value="",'.
374. Diese Zeile definiert den Inhalt '),'.
375. Diese Zeile definiert den Inhalt ')'.
376. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
377. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
378. Diese Zeile definiert den Inhalt '@router.post("/recipes/{recipe_id}/edit")'.
379. Diese Zeile definiert den Inhalt 'async def edit_recipe_submit('.
380. Diese Zeile definiert den Inhalt 'recipe_id: int,'.
381. Diese Zeile definiert den Inhalt 'title: str = Form(...),'.
382. Diese Zeile definiert den Inhalt 'description: str = Form(...),'.
383. Diese Zeile definiert den Inhalt 'instructions: str = Form(...),'.
384. Diese Zeile definiert den Inhalt 'category_select: str = Form(DEFAULT_CATEGORY),'.
385. Diese Zeile definiert den Inhalt 'category_new: str = Form(""),'.
386. Diese Zeile definiert den Inhalt 'category: str = Form(""),'.
387. Diese Zeile definiert den Inhalt 'title_image_url: str = Form(""),'.
388. Diese Zeile definiert den Inhalt 'prep_time_minutes: str = Form(...),'.
389. Diese Zeile definiert den Inhalt 'difficulty: str = Form(...),'.
390. Diese Zeile definiert den Inhalt 'ingredients_text: str = Form(""),'.
391. Diese Zeile definiert den Inhalt 'image: UploadFile | None = File(None),'.
392. Diese Zeile definiert den Inhalt 'db: Session = Depends(get_db),'.
393. Diese Zeile definiert den Inhalt 'current_user: User = Depends(get_current_user),'.
394. Diese Zeile definiert den Inhalt '):'.
395. Diese Zeile definiert den Inhalt 'recipe = fetch_recipe_or_404(db, recipe_id)'.
396. Diese Zeile definiert den Inhalt 'ensure_recipe_access(current_user, recipe)'.
397. Diese Zeile definiert den Inhalt 'recipe.title = title.strip()'.
398. Diese Zeile definiert den Inhalt 'recipe.title_image_url = normalize_image_url(title_image_url)'.
399. Diese Zeile definiert den Inhalt 'recipe.description = description.strip()'.
400. Diese Zeile definiert den Inhalt 'recipe.instructions = instructions.strip()'.
401. Diese Zeile definiert den Inhalt 'recipe.category = resolve_category_value(category_select, category_new, category)'.
402. Diese Zeile definiert den Inhalt 'recipe.prep_time_minutes = parse_positive_int(prep_time_minutes, "prep_time_minutes")'.
403. Diese Zeile definiert den Inhalt 'recipe.difficulty = sanitize_difficulty(difficulty)'.
404. Diese Zeile definiert den Inhalt 'replace_recipe_ingredients(db, recipe, parse_ingredient_text(ingredients_text))'.
405. Diese Zeile definiert den Inhalt 'if image and image.filename:'.
406. Diese Zeile definiert den Inhalt 'data = await image.read()'.
407. Diese Zeile definiert den Inhalt 'try:'.
408. Diese Zeile definiert den Inhalt 'validate_image_upload((image.content_type or "").lower(), data)'.
409. Diese Zeile definiert den Inhalt 'except ImageValidationError as exc:'.
410. Diese Zeile definiert den Inhalt 'raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc'.
411. Diese Zeile definiert den Inhalt 'image_content_type = (image.content_type or "application/octet-stream").lower()'.
412. Diese Zeile definiert den Inhalt 'has_images = db.scalar(select(func.count()).select_from(RecipeImage).where(RecipeImage....'.
413. Diese Zeile definiert den Inhalt 'db.add('.
414. Diese Zeile definiert den Inhalt 'RecipeImage('.
415. Diese Zeile definiert den Inhalt 'recipe_id=recipe.id,'.
416. Diese Zeile definiert den Inhalt 'filename=safe_image_filename(image.filename or "", image_content_type),'.
417. Diese Zeile definiert den Inhalt 'content_type=image_content_type,'.
418. Diese Zeile definiert den Inhalt 'data=data,'.
419. Diese Zeile definiert den Inhalt 'is_primary=has_images == 0,'.
420. Diese Zeile definiert den Inhalt ')'.
421. Diese Zeile definiert den Inhalt ')'.
422. Diese Zeile definiert den Inhalt 'db.commit()'.
423. Diese Zeile definiert den Inhalt 'return redirect(f"/recipes/{recipe.id}")'.
424. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
425. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
426. Diese Zeile definiert den Inhalt '@router.post("/recipes/{recipe_id}/delete")'.
427. Diese Zeile definiert den Inhalt 'def delete_recipe('.
428. Diese Zeile definiert den Inhalt 'recipe_id: int,'.
429. Diese Zeile definiert den Inhalt 'db: Session = Depends(get_db),'.
430. Diese Zeile definiert den Inhalt 'current_user: User = Depends(get_current_user),'.
431. Diese Zeile definiert den Inhalt '):'.
432. Diese Zeile definiert den Inhalt 'recipe = fetch_recipe_or_404(db, recipe_id)'.
433. Diese Zeile definiert den Inhalt 'ensure_recipe_access(current_user, recipe)'.
434. Diese Zeile definiert den Inhalt 'db.delete(recipe)'.
435. Diese Zeile definiert den Inhalt 'db.commit()'.
436. Diese Zeile definiert den Inhalt 'return redirect("/my-recipes")'.
437. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
438. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
439. Diese Zeile definiert den Inhalt '@router.post("/recipes/{recipe_id}/reviews")'.
440. Diese Zeile definiert den Inhalt 'def upsert_review('.
441. Diese Zeile definiert den Inhalt 'recipe_id: int,'.
442. Diese Zeile definiert den Inhalt 'rating: int = Form(...),'.
443. Diese Zeile definiert den Inhalt 'comment: str = Form(""),'.
444. Diese Zeile definiert den Inhalt 'db: Session = Depends(get_db),'.
445. Diese Zeile definiert den Inhalt 'current_user: User = Depends(get_current_user),'.
446. Diese Zeile definiert den Inhalt '):'.
447. Diese Zeile definiert den Inhalt 'recipe = db.scalar(select(Recipe).where(Recipe.id == recipe_id))'.
448. Diese Zeile definiert den Inhalt 'if not recipe:'.
449. Diese Zeile definiert den Inhalt 'raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found.")'.
450. Diese Zeile definiert den Inhalt 'if not recipe.is_published:'.
451. Diese Zeile definiert den Inhalt 'raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found.")'.
452. Diese Zeile definiert den Inhalt 'if rating < 1 or rating > 5:'.
453. Diese Zeile definiert den Inhalt 'raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Rating must be bet...'.
454. Diese Zeile definiert den Inhalt 'review = db.scalar(select(Review).where(and_(Review.recipe_id == recipe_id, Review.user...'.
455. Diese Zeile definiert den Inhalt 'if review:'.
456. Diese Zeile definiert den Inhalt 'review.rating = rating'.
457. Diese Zeile definiert den Inhalt 'review.comment = comment.strip()'.
458. Diese Zeile definiert den Inhalt 'else:'.
459. Diese Zeile definiert den Inhalt 'db.add(Review(recipe_id=recipe_id, user_id=current_user.id, rating=rating, comment=comm...'.
460. Diese Zeile definiert den Inhalt 'db.commit()'.
461. Diese Zeile definiert den Inhalt 'return redirect(f"/recipes/{recipe_id}")'.
462. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
463. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
464. Diese Zeile definiert den Inhalt '@router.post("/reviews/{review_id}/delete")'.
465. Diese Zeile definiert den Inhalt 'def delete_review('.
466. Diese Zeile definiert den Inhalt 'review_id: int,'.
467. Diese Zeile definiert den Inhalt 'db: Session = Depends(get_db),'.
468. Diese Zeile definiert den Inhalt 'current_user: User = Depends(get_current_user),'.
469. Diese Zeile definiert den Inhalt '):'.
470. Diese Zeile definiert den Inhalt 'review = db.scalar(select(Review).where(Review.id == review_id).options(joinedload(Revi...'.
471. Diese Zeile definiert den Inhalt 'if not review:'.
472. Diese Zeile definiert den Inhalt 'raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found.")'.
473. Diese Zeile definiert den Inhalt 'if current_user.role != "admin" and review.user_id != current_user.id:'.
474. Diese Zeile definiert den Inhalt 'raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissio...'.
475. Diese Zeile definiert den Inhalt 'recipe_id = review.recipe_id'.
476. Diese Zeile definiert den Inhalt 'db.delete(review)'.
477. Diese Zeile definiert den Inhalt 'db.commit()'.
478. Diese Zeile definiert den Inhalt 'return redirect(f"/recipes/{recipe_id}")'.
479. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
480. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
481. Diese Zeile definiert den Inhalt '@router.post("/recipes/{recipe_id}/favorite")'.
482. Diese Zeile definiert den Inhalt 'def toggle_favorite('.
483. Diese Zeile definiert den Inhalt 'request: Request,'.
484. Diese Zeile definiert den Inhalt 'recipe_id: int,'.
485. Diese Zeile definiert den Inhalt 'db: Session = Depends(get_db),'.
486. Diese Zeile definiert den Inhalt 'current_user: User = Depends(get_current_user),'.
487. Diese Zeile definiert den Inhalt '):'.
488. Diese Zeile definiert den Inhalt 'recipe = db.scalar(select(Recipe).where(Recipe.id == recipe_id))'.
489. Diese Zeile definiert den Inhalt 'if not recipe or not recipe.is_published:'.
490. Diese Zeile definiert den Inhalt 'raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found.")'.
491. Diese Zeile definiert den Inhalt 'favorite = db.scalar('.
492. Diese Zeile definiert den Inhalt 'select(Favorite).where(and_(Favorite.user_id == current_user.id, Favorite.recipe_id == ...'.
493. Diese Zeile definiert den Inhalt ')'.
494. Diese Zeile definiert den Inhalt 'is_favorite = True'.
495. Diese Zeile definiert den Inhalt 'if favorite:'.
496. Diese Zeile definiert den Inhalt 'db.delete(favorite)'.
497. Diese Zeile definiert den Inhalt 'is_favorite = False'.
498. Diese Zeile definiert den Inhalt 'else:'.
499. Diese Zeile definiert den Inhalt 'db.add(Favorite(user_id=current_user.id, recipe_id=recipe_id))'.
500. Diese Zeile definiert den Inhalt 'is_favorite = True'.
501. Diese Zeile definiert den Inhalt 'db.commit()'.
502. Diese Zeile definiert den Inhalt 'if request.headers.get("HX-Request") == "true":'.
503. Diese Zeile definiert den Inhalt 'return templates.TemplateResponse('.
504. Diese Zeile definiert den Inhalt '"partials/favorite_button.html",'.
505. Diese Zeile definiert den Inhalt 'template_context(request, current_user, recipe=recipe, is_favorite=is_favorite),'.
506. Diese Zeile definiert den Inhalt ')'.
507. Diese Zeile definiert den Inhalt 'return redirect(f"/recipes/{recipe_id}")'.
508. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
509. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
510. Diese Zeile definiert den Inhalt '@router.get("/favorites")'.
511. Diese Zeile definiert den Inhalt 'def favorites_page('.
512. Diese Zeile definiert den Inhalt 'request: Request,'.
513. Diese Zeile definiert den Inhalt 'db: Session = Depends(get_db),'.
514. Diese Zeile definiert den Inhalt 'current_user: User = Depends(get_current_user),'.
515. Diese Zeile definiert den Inhalt '):'.
516. Diese Zeile definiert den Inhalt 'favorite_recipes = db.scalars('.
517. Diese Zeile definiert den Inhalt 'select(Recipe)'.
518. Diese Zeile definiert den Inhalt '.join(Favorite, Favorite.recipe_id == Recipe.id)'.
519. Diese Zeile definiert den Inhalt '.where(Favorite.user_id == current_user.id, Recipe.is_published.is_(True))'.
520. Diese Zeile definiert den Inhalt '.order_by(Recipe.created_at.desc())'.
521. Diese Zeile definiert den Inhalt '.options(selectinload(Recipe.images))'.
522. Diese Zeile definiert den Inhalt ').all()'.
523. Diese Zeile definiert den Inhalt 'return templates.TemplateResponse('.
524. Diese Zeile definiert den Inhalt '"favorites.html",'.
525. Diese Zeile definiert den Inhalt 'template_context(request, current_user, favorite_recipes=favorite_recipes),'.
526. Diese Zeile definiert den Inhalt ')'.
527. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
528. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
529. Diese Zeile definiert den Inhalt '@router.get("/my-recipes")'.
530. Diese Zeile definiert den Inhalt 'def my_recipes_page('.
531. Diese Zeile definiert den Inhalt 'request: Request,'.
532. Diese Zeile definiert den Inhalt 'db: Session = Depends(get_db),'.
533. Diese Zeile definiert den Inhalt 'current_user: User = Depends(get_current_user),'.
534. Diese Zeile definiert den Inhalt '):'.
535. Diese Zeile definiert den Inhalt 'stmt = select(Recipe).order_by(Recipe.created_at.desc()).options(selectinload(Recipe.im...'.
536. Diese Zeile definiert den Inhalt 'if current_user.role != "admin":'.
537. Diese Zeile definiert den Inhalt 'stmt = stmt.where(Recipe.creator_id == current_user.id)'.
538. Diese Zeile definiert den Inhalt 'recipes = db.scalars(stmt).all()'.
539. Diese Zeile definiert den Inhalt 'return templates.TemplateResponse('.
540. Diese Zeile definiert den Inhalt '"my_recipes.html",'.
541. Diese Zeile definiert den Inhalt 'template_context(request, current_user, recipes=recipes),'.
542. Diese Zeile definiert den Inhalt ')'.
543. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
544. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
545. Diese Zeile definiert den Inhalt '@router.post("/recipes/{recipe_id}/images")'.
546. Diese Zeile definiert den Inhalt '@limiter.limit("10/minute", key_func=key_by_user_or_ip)'.
547. Diese Zeile definiert den Inhalt 'async def upload_recipe_image('.
548. Diese Zeile definiert den Inhalt 'request: Request,'.
549. Diese Zeile definiert den Inhalt 'response: Response,'.
550. Diese Zeile definiert den Inhalt 'recipe_id: int,'.
551. Diese Zeile definiert den Inhalt 'set_primary: bool = Form(False),'.
552. Diese Zeile definiert den Inhalt 'file: UploadFile = File(...),'.
553. Diese Zeile definiert den Inhalt 'db: Session = Depends(get_db),'.
554. Diese Zeile definiert den Inhalt 'current_user: User = Depends(get_current_user),'.
555. Diese Zeile definiert den Inhalt '):'.
556. Diese Zeile definiert den Inhalt '_ = response'.
557. Diese Zeile definiert den Inhalt 'recipe = fetch_recipe_or_404(db, recipe_id)'.
558. Diese Zeile definiert den Inhalt 'ensure_recipe_access(current_user, recipe)'.
559. Diese Zeile definiert den Inhalt 'data = await file.read()'.
560. Diese Zeile definiert den Inhalt 'content_type = (file.content_type or "").lower()'.
561. Diese Zeile definiert den Inhalt 'try:'.
562. Diese Zeile definiert den Inhalt 'validate_image_upload(content_type, data)'.
563. Diese Zeile definiert den Inhalt 'except ImageValidationError as exc:'.
564. Diese Zeile definiert den Inhalt 'raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc'.
565. Diese Zeile definiert den Inhalt 'has_images = db.scalar(select(func.count()).select_from(RecipeImage).where(RecipeImage....'.
566. Diese Zeile definiert den Inhalt 'query_value = request.query_params.get("set_primary")'.
567. Diese Zeile definiert den Inhalt 'if query_value is not None:'.
568. Diese Zeile definiert den Inhalt 'set_primary = query_value.strip().lower() in {"1", "true", "yes", "on"}'.
569. Diese Zeile definiert den Inhalt 'new_is_primary = set_primary or has_images == 0'.
570. Diese Zeile definiert den Inhalt 'recipe_image = RecipeImage('.
571. Diese Zeile definiert den Inhalt 'recipe_id=recipe_id,'.
572. Diese Zeile definiert den Inhalt 'filename=safe_image_filename(file.filename or "", content_type),'.
573. Diese Zeile definiert den Inhalt 'content_type=content_type,'.
574. Diese Zeile definiert den Inhalt 'data=data,'.
575. Diese Zeile definiert den Inhalt 'is_primary=new_is_primary,'.
576. Diese Zeile definiert den Inhalt ')'.
577. Diese Zeile definiert den Inhalt 'db.add(recipe_image)'.
578. Diese Zeile definiert den Inhalt 'db.flush()'.
579. Diese Zeile definiert den Inhalt 'if new_is_primary:'.
580. Diese Zeile definiert den Inhalt 'set_recipe_primary_image(db, recipe, recipe_image.id)'.
581. Diese Zeile definiert den Inhalt 'db.commit()'.
582. Diese Zeile definiert den Inhalt 'if request.headers.get("HX-Request") == "true":'.
583. Diese Zeile definiert den Inhalt 'return render_image_section(request, db, recipe_id, current_user)'.
584. Diese Zeile definiert den Inhalt 'return redirect(f"/recipes/{recipe_id}")'.
585. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
586. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
587. Diese Zeile definiert den Inhalt '@router.get("/images/{image_id}")'.
588. Diese Zeile definiert den Inhalt 'def get_image(image_id: int, db: Session = Depends(get_db)):'.
589. Diese Zeile definiert den Inhalt 'image = db.scalar(select(RecipeImage).where(RecipeImage.id == image_id))'.
590. Diese Zeile definiert den Inhalt 'if not image:'.
591. Diese Zeile definiert den Inhalt 'raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found.")'.
592. Diese Zeile definiert den Inhalt 'return Response(content=image.data, media_type=image.content_type)'.
593. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
594. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
595. Diese Zeile definiert den Inhalt '@router.get("/external-image")'.
596. Diese Zeile definiert den Inhalt 'def external_image(url: str):'.
597. Diese Zeile definiert den Inhalt 'try:'.
598. Diese Zeile definiert den Inhalt 'resolved_url = resolve_title_image_url(url)'.
599. Diese Zeile definiert den Inhalt 'except Exception as exc:'.
600. Diese Zeile definiert den Inhalt 'raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Could not resolve...'.
601. Diese Zeile definiert den Inhalt 'if not resolved_url:'.
602. Diese Zeile definiert den Inhalt 'raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No image URL availab...'.
603. Diese Zeile definiert den Inhalt 'return RedirectResponse(url=resolved_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)'.
604. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
605. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
606. Diese Zeile definiert den Inhalt '@router.delete("/images/{image_id}")'.
607. Diese Zeile definiert den Inhalt 'def delete_image_api('.
608. Diese Zeile definiert den Inhalt 'image_id: int,'.
609. Diese Zeile definiert den Inhalt 'db: Session = Depends(get_db),'.
610. Diese Zeile definiert den Inhalt 'current_user: User = Depends(get_current_user),'.
611. Diese Zeile definiert den Inhalt '):'.
612. Diese Zeile definiert den Inhalt 'image = db.scalar(select(RecipeImage).where(RecipeImage.id == image_id).options(joinedl...'.
613. Diese Zeile definiert den Inhalt 'if not image:'.
614. Diese Zeile definiert den Inhalt 'raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found.")'.
615. Diese Zeile definiert den Inhalt 'ensure_recipe_access(current_user, image.recipe)'.
616. Diese Zeile definiert den Inhalt 'recipe = image.recipe'.
617. Diese Zeile definiert den Inhalt 'db.delete(image)'.
618. Diese Zeile definiert den Inhalt 'db.flush()'.
619. Diese Zeile definiert den Inhalt 'maybe_promote_primary_after_delete(db, recipe)'.
620. Diese Zeile definiert den Inhalt 'db.commit()'.
621. Diese Zeile definiert den Inhalt 'return {"status": "deleted"}'.
622. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
623. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
624. Diese Zeile definiert den Inhalt '@router.post("/images/{image_id}/delete")'.
625. Diese Zeile definiert den Inhalt 'def delete_image_form('.
626. Diese Zeile definiert den Inhalt 'request: Request,'.
627. Diese Zeile definiert den Inhalt 'image_id: int,'.
628. Diese Zeile definiert den Inhalt 'db: Session = Depends(get_db),'.
629. Diese Zeile definiert den Inhalt 'current_user: User = Depends(get_current_user),'.
630. Diese Zeile definiert den Inhalt '):'.
631. Diese Zeile definiert den Inhalt 'image = db.scalar(select(RecipeImage).where(RecipeImage.id == image_id).options(joinedl...'.
632. Diese Zeile definiert den Inhalt 'if not image:'.
633. Diese Zeile definiert den Inhalt 'raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found.")'.
634. Diese Zeile definiert den Inhalt 'recipe = image.recipe'.
635. Diese Zeile definiert den Inhalt 'recipe_id = image.recipe_id'.
636. Diese Zeile definiert den Inhalt 'ensure_recipe_access(current_user, recipe)'.
637. Diese Zeile definiert den Inhalt 'db.delete(image)'.
638. Diese Zeile definiert den Inhalt 'db.flush()'.
639. Diese Zeile definiert den Inhalt 'maybe_promote_primary_after_delete(db, recipe)'.
640. Diese Zeile definiert den Inhalt 'db.commit()'.
641. Diese Zeile definiert den Inhalt 'if request.headers.get("HX-Request") == "true":'.
642. Diese Zeile definiert den Inhalt 'return render_image_section(request, db, recipe_id, current_user)'.
643. Diese Zeile definiert den Inhalt 'return redirect(f"/recipes/{recipe_id}")'.
644. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
645. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
646. Diese Zeile definiert den Inhalt '@router.post("/images/{image_id}/set-primary")'.
647. Diese Zeile definiert den Inhalt 'def set_primary_image('.
648. Diese Zeile definiert den Inhalt 'request: Request,'.
649. Diese Zeile definiert den Inhalt 'image_id: int,'.
650. Diese Zeile definiert den Inhalt 'db: Session = Depends(get_db),'.
651. Diese Zeile definiert den Inhalt 'current_user: User = Depends(get_current_user),'.
652. Diese Zeile definiert den Inhalt '):'.
653. Diese Zeile definiert den Inhalt 'image = db.scalar(select(RecipeImage).where(RecipeImage.id == image_id).options(joinedl...'.
654. Diese Zeile definiert den Inhalt 'if not image:'.
655. Diese Zeile definiert den Inhalt 'raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found.")'.
656. Diese Zeile definiert den Inhalt 'recipe = image.recipe'.
657. Diese Zeile definiert den Inhalt 'ensure_recipe_access(current_user, recipe)'.
658. Diese Zeile definiert den Inhalt 'set_recipe_primary_image(db, recipe, image.id)'.
659. Diese Zeile definiert den Inhalt 'db.commit()'.
660. Diese Zeile definiert den Inhalt 'if request.headers.get("HX-Request") == "true":'.
661. Diese Zeile definiert den Inhalt 'return render_image_section(request, db, recipe.id, current_user)'.
662. Diese Zeile definiert den Inhalt 'return redirect(f"/recipes/{recipe.id}")'.
663. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
664. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
665. Diese Zeile definiert den Inhalt '@router.get("/recipes/{recipe_id}/pdf")'.
666. Diese Zeile definiert den Inhalt 'def recipe_pdf('.
667. Diese Zeile definiert den Inhalt 'recipe_id: int,'.
668. Diese Zeile definiert den Inhalt 'db: Session = Depends(get_db),'.
669. Diese Zeile definiert den Inhalt 'current_user: User = Depends(get_current_user),'.
670. Diese Zeile definiert den Inhalt '):'.
671. Diese Zeile definiert den Inhalt 'recipe = fetch_recipe_or_404(db, recipe_id)'.
672. Diese Zeile definiert den Inhalt 'ensure_recipe_visible(recipe, current_user)'.
673. Diese Zeile definiert den Inhalt 'avg_rating = db.scalar(select(func.coalesce(func.avg(Review.rating), 0)).where(Review.r...'.
674. Diese Zeile definiert den Inhalt 'review_count = db.scalar(select(func.count(Review.id)).where(Review.recipe_id == recipe...'.
675. Diese Zeile definiert den Inhalt 'pdf_bytes = build_recipe_pdf(recipe, float(avg_rating), int(review_count))'.
676. Diese Zeile definiert den Inhalt 'filename = f"mealmate_recipe_{recipe_id}.pdf"'.
677. Diese Zeile definiert den Inhalt 'headers = {"Content-Disposition": f'attachment; filename="{filename}"'}'.
678. Diese Zeile definiert den Inhalt 'return StreamingResponse(BytesIO(pdf_bytes), media_type="application/pdf", headers=head...'.
679. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
680. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
681. Diese Zeile definiert den Inhalt '@router.get("/categories")'.
682. Diese Zeile definiert den Inhalt 'def categories_api(db: Session = Depends(get_db)):'.
683. Diese Zeile definiert den Inhalt 'return {"categories": get_distinct_categories(db, only_published=True)}'.

## app/templates/base.html
```jinja2
<!doctype html>
<html lang="de">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="csrf-token" content="{{ csrf_token or '' }}">
  <title>{{ title or t("app.name") }}</title>
  <link rel="stylesheet" href="/static/style.css">
  <script src="/static/htmx.min.js"></script>
  <script src="/static/security.js" defer></script>
</head>
<body>
  <header class="topbar">
    <a href="/" class="brand">{{ t("app.name") }}</a>
    <nav>
      <a href="/">{{ t("nav.discover") }}</a>
      <a href="/submit">{{ t("nav.submit_recipe") }}</a>
      {% if current_user %}
      {% if current_user.role == "admin" %}
      <a href="/recipes/new">{{ t("nav.publish_recipe") }}</a>
      {% endif %}
      <a href="/my-recipes">{{ t("nav.my_recipes") }}</a>
      <a href="/my-submissions">{{ t("nav.my_submissions") }}</a>
      <a href="/favorites">{{ t("nav.favorites") }}</a>
      <a href="/me">{{ t("nav.profile") }}</a>
      {% if current_user.role == "admin" %}
      <a href="/admin">{{ t("nav.admin") }}</a>
      <a href="/admin/submissions">{{ t("nav.admin_submissions") }}</a>
      {% endif %}
      <form method="post" action="/logout" class="inline">
        <button type="submit">{{ t("nav.logout") }}</button>
      </form>
      {% else %}
      <a href="/login">{{ t("nav.login") }}</a>
      <a href="/register">{{ t("nav.register") }}</a>
      {% endif %}
    </nav>
  </header>
  <main class="container">
    {% block content %}{% endblock %}
  </main>
</body>
</html>
```
ZEILEN-ERKL?RUNG
1. Diese Zeile definiert den Inhalt '<!doctype html>'.
2. Diese Zeile definiert den Inhalt '<html lang="de">'.
3. Diese Zeile definiert den Inhalt '<head>'.
4. Diese Zeile definiert den Inhalt '<meta charset="utf-8">'.
5. Diese Zeile definiert den Inhalt '<meta name="viewport" content="width=device-width, initial-scale=1">'.
6. Diese Zeile definiert den Inhalt '<meta name="csrf-token" content="{{ csrf_token or '' }}">'.
7. Diese Zeile definiert den Inhalt '<title>{{ title or t("app.name") }}</title>'.
8. Diese Zeile definiert den Inhalt '<link rel="stylesheet" href="/static/style.css">'.
9. Diese Zeile definiert den Inhalt '<script src="/static/htmx.min.js"></script>'.
10. Diese Zeile definiert den Inhalt '<script src="/static/security.js" defer></script>'.
11. Diese Zeile definiert den Inhalt '</head>'.
12. Diese Zeile definiert den Inhalt '<body>'.
13. Diese Zeile definiert den Inhalt '<header class="topbar">'.
14. Diese Zeile definiert den Inhalt '<a href="/" class="brand">{{ t("app.name") }}</a>'.
15. Diese Zeile definiert den Inhalt '<nav>'.
16. Diese Zeile definiert den Inhalt '<a href="/">{{ t("nav.discover") }}</a>'.
17. Diese Zeile definiert den Inhalt '<a href="/submit">{{ t("nav.submit_recipe") }}</a>'.
18. Diese Zeile definiert den Inhalt '{% if current_user %}'.
19. Diese Zeile definiert den Inhalt '{% if current_user.role == "admin" %}'.
20. Diese Zeile definiert den Inhalt '<a href="/recipes/new">{{ t("nav.publish_recipe") }}</a>'.
21. Diese Zeile definiert den Inhalt '{% endif %}'.
22. Diese Zeile definiert den Inhalt '<a href="/my-recipes">{{ t("nav.my_recipes") }}</a>'.
23. Diese Zeile definiert den Inhalt '<a href="/my-submissions">{{ t("nav.my_submissions") }}</a>'.
24. Diese Zeile definiert den Inhalt '<a href="/favorites">{{ t("nav.favorites") }}</a>'.
25. Diese Zeile definiert den Inhalt '<a href="/me">{{ t("nav.profile") }}</a>'.
26. Diese Zeile definiert den Inhalt '{% if current_user.role == "admin" %}'.
27. Diese Zeile definiert den Inhalt '<a href="/admin">{{ t("nav.admin") }}</a>'.
28. Diese Zeile definiert den Inhalt '<a href="/admin/submissions">{{ t("nav.admin_submissions") }}</a>'.
29. Diese Zeile definiert den Inhalt '{% endif %}'.
30. Diese Zeile definiert den Inhalt '<form method="post" action="/logout" class="inline">'.
31. Diese Zeile definiert den Inhalt '<button type="submit">{{ t("nav.logout") }}</button>'.
32. Diese Zeile definiert den Inhalt '</form>'.
33. Diese Zeile definiert den Inhalt '{% else %}'.
34. Diese Zeile definiert den Inhalt '<a href="/login">{{ t("nav.login") }}</a>'.
35. Diese Zeile definiert den Inhalt '<a href="/register">{{ t("nav.register") }}</a>'.
36. Diese Zeile definiert den Inhalt '{% endif %}'.
37. Diese Zeile definiert den Inhalt '</nav>'.
38. Diese Zeile definiert den Inhalt '</header>'.
39. Diese Zeile definiert den Inhalt '<main class="container">'.
40. Diese Zeile definiert den Inhalt '{% block content %}{% endblock %}'.
41. Diese Zeile definiert den Inhalt '</main>'.
42. Diese Zeile definiert den Inhalt '</body>'.
43. Diese Zeile definiert den Inhalt '</html>'.

## app/i18n/de.py
```python
DE_TEXTS: dict[str, str] = {
    "app.name": "MealMate",
    "nav.discover": "Rezepte entdecken",
    "nav.submit_recipe": "Rezept einreichen",
    "nav.create_recipe": "Rezept erstellen",
    "nav.publish_recipe": "Rezept veroeffentlichen",
    "nav.my_recipes": "Meine Rezepte",
    "nav.my_submissions": "Meine Einreichungen",
    "nav.favorites": "Favoriten",
    "nav.profile": "Mein Profil",
    "nav.admin": "Admin",
    "nav.admin_submissions": "Moderation",
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
    "recipe_form.create_title": "Rezept veroeffentlichen",
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
    "submission.submit_title": "Rezept einreichen",
    "submission.submit_hint": "Einreichungen werden vor der Veroeffentlichung durch das Admin-Team geprueft.",
    "submission.submitter_email": "Kontakt-E-Mail (optional)",
    "submission.title": "Titel",
    "submission.description": "Beschreibung",
    "submission.instructions": "Anleitung",
    "submission.category": "Kategorie",
    "submission.new_category_option": "Neue Kategorie...",
    "submission.new_category_label": "Neue Kategorie",
    "submission.difficulty": "Schwierigkeit",
    "submission.prep_time": "Zubereitungszeit (Minuten, optional)",
    "submission.servings": "Portionen (optional)",
    "submission.ingredients": "Zutaten (Format: name|menge|gramm)",
    "submission.image_optional": "Optionales Bild",
    "submission.submit_button": "Zur Pruefung einreichen",
    "submission.default_description": "Rezept-Einreichung",
    "submission.thank_you": "Vielen Dank! Dein Rezept wurde eingereicht und wird geprueft.",
    "submission.my_title": "Meine Einreichungen",
    "submission.my_submitted_message": "Deine Einreichung wurde gespeichert und wartet auf Pruefung.",
    "submission.my_empty": "Du hast noch keine Einreichungen.",
    "submission.admin_note": "Admin-Notiz",
    "submission.status_pending": "Ausstehend",
    "submission.status_approved": "Freigegeben",
    "submission.status_rejected": "Abgelehnt",
    "submission.status_all": "Alle",
    "submission.admin_queue_title": "Moderations-Warteschlange",
    "submission.status_filter": "Status",
    "submission.stats_pending": "Ausstehend",
    "submission.stats_approved": "Freigegeben",
    "submission.stats_rejected": "Abgelehnt",
    "submission.table_date": "Datum",
    "submission.table_title": "Titel",
    "submission.table_submitter": "Einreicher",
    "submission.table_status": "Status",
    "submission.table_action": "Aktion",
    "submission.open_detail": "Details",
    "submission.admin_empty": "Keine Einreichungen gefunden.",
    "submission.admin_detail_title": "Einreichung",
    "submission.back_to_queue": "Zurueck zur Warteschlange",
    "submission.preview": "Vorschau",
    "submission.edit_submission": "Einreichung bearbeiten",
    "submission.set_primary_new_image": "Neues Bild als Hauptbild setzen",
    "submission.save_changes": "Aenderungen speichern",
    "submission.moderation_actions": "Moderations-Aktionen",
    "submission.optional_admin_note": "Admin-Notiz (optional)",
    "submission.approve_button": "Freigeben",
    "submission.reject_reason": "Ablehnungsgrund",
    "submission.reject_button": "Ablehnen",
    "submission.approved": "Einreichung wurde freigegeben.",
    "submission.rejected": "Einreichung wurde abgelehnt.",
    "submission.updated": "Einreichung wurde aktualisiert.",
    "submission.image_deleted": "Bild wurde entfernt.",
    "submission.image_primary": "Hauptbild wurde gesetzt.",
    "submission.admin_queue_link": "Zur Moderations-Warteschlange",
    "submission.guest": "Gast",
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
    "admin.import_help_title": "CSV-Format Hilfe",
    "admin.import_help_intro": "Bitte nutze das kanonische Importformat, damit der Import stabil und ohne Duplikate laeuft.",
    "admin.import_required_columns": "Pflichtspalten: title, instructions",
    "admin.import_optional_columns": "Empfohlene Spalten: description, category, difficulty, prep_time_minutes, servings_text, ingredients, image_url, source_uuid",
    "admin.import_difficulty_values": "Difficulty-Werte: easy, medium, hard",
    "admin.import_ingredients_example": "Ingredients Beispiel: 2 Eier | 200g Mehl | 1 Prise Salz oder JSON-Liste",
    "admin.import_encoding_delimiter": "Encoding: utf-8-sig, Delimiter standardmaessig ';' (',' als Fallback)",
    "admin.download_template": "CSV Template herunterladen",
    "admin.download_example": "CSV Beispiel herunterladen",
    "admin.upload_label": "CSV-Upload",
    "admin.insert_only": "Nur neue hinzufuegen (UPSERT SAFE)",
    "admin.update_existing": "Existierende aktualisieren (Warnung: nur ausgewaehlte Felder!)",
    "admin.dry_run": "Nur pruefen (Dry Run)",
    "admin.force_with_warnings": "Trotz Warnungen fortsetzen",
    "admin.import_warning_text": "Standard ist Insert-Only; Update Existing nur aktivieren, wenn bewusst gewuenscht.",
    "admin.preview_button": "Vorschau erstellen",
    "admin.preview_done": "Vorschau wurde erstellt.",
    "admin.preview_title": "Import-Vorschau",
    "admin.preview_total_rows": "Gesamtzeilen",
    "admin.preview_delimiter": "Erkannter Delimiter",
    "admin.preview_fatal_rows": "Zeilen mit Fehlern",
    "admin.preview_row": "Zeile",
    "admin.preview_status": "Status",
    "admin.preview_notes": "Hinweise",
    "admin.preview_errors_title": "Fehlerliste",
    "admin.preview_warnings_title": "Warnungsliste",
    "admin.import_result_title": "Import-Ergebnis",
    "admin.import_blocked_errors": "Import blockiert: Bitte behebe zuerst die fehlerhaften Zeilen.",
    "admin.confirm_warnings_required": "Warnungen vorhanden: Setze 'Trotz Warnungen fortsetzen', um den Import zu starten.",
    "admin.dry_run_done": "Dry-Run abgeschlossen, es wurden keine Daten geschrieben.",
    "admin.start_import": "Import starten",
    "admin.report_inserted": "Neu",
    "admin.report_updated": "Aktualisiert",
    "admin.report_skipped": "Uebersprungen",
    "admin.report_errors": "Fehler",
    "admin.report_warnings": "Warnungen",
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
    "error.submission_not_found": "Einreichung nicht gefunden.",
    "error.review_not_found": "Bewertung nicht gefunden.",
    "error.image_not_found": "Bild nicht gefunden.",
    "error.recipe_permission": "Keine ausreichenden Rechte fuer dieses Rezept.",
    "error.submission_permission": "Keine ausreichenden Rechte fuer diese Einreichung.",
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
    "error.submission_already_published": "Diese Einreichung wurde bereits veroeffentlicht.",
    "error.submission_reject_reason_required": "Bitte einen Ablehnungsgrund angeben.",
    "error.csrf_failed": "CSRF-Pruefung fehlgeschlagen.",
    "error.internal": "Interner Serverfehler.",
    "error.not_found": "Ressource nicht gefunden.",
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
ZEILEN-ERKL?RUNG
1. Diese Zeile definiert den Inhalt 'DE_TEXTS: dict[str, str] = {'.
2. Diese Zeile definiert den Inhalt '"app.name": "MealMate",'.
3. Diese Zeile definiert den Inhalt '"nav.discover": "Rezepte entdecken",'.
4. Diese Zeile definiert den Inhalt '"nav.submit_recipe": "Rezept einreichen",'.
5. Diese Zeile definiert den Inhalt '"nav.create_recipe": "Rezept erstellen",'.
6. Diese Zeile definiert den Inhalt '"nav.publish_recipe": "Rezept veroeffentlichen",'.
7. Diese Zeile definiert den Inhalt '"nav.my_recipes": "Meine Rezepte",'.
8. Diese Zeile definiert den Inhalt '"nav.my_submissions": "Meine Einreichungen",'.
9. Diese Zeile definiert den Inhalt '"nav.favorites": "Favoriten",'.
10. Diese Zeile definiert den Inhalt '"nav.profile": "Mein Profil",'.
11. Diese Zeile definiert den Inhalt '"nav.admin": "Admin",'.
12. Diese Zeile definiert den Inhalt '"nav.admin_submissions": "Moderation",'.
13. Diese Zeile definiert den Inhalt '"nav.login": "Anmelden",'.
14. Diese Zeile definiert den Inhalt '"nav.register": "Registrieren",'.
15. Diese Zeile definiert den Inhalt '"nav.logout": "Abmelden",'.
16. Diese Zeile definiert den Inhalt '"home.title": "Rezepte entdecken",'.
17. Diese Zeile definiert den Inhalt '"home.title_contains": "Titel enthaelt",'.
18. Diese Zeile definiert den Inhalt '"home.category": "Kategorie",'.
19. Diese Zeile definiert den Inhalt '"home.all_categories": "Alle Kategorien",'.
20. Diese Zeile definiert den Inhalt '"home.difficulty": "Schwierigkeit",'.
21. Diese Zeile definiert den Inhalt '"home.ingredient": "Zutat",'.
22. Diese Zeile definiert den Inhalt '"home.per_page": "Pro Seite",'.
23. Diese Zeile definiert den Inhalt '"home.apply": "Anwenden",'.
24. Diese Zeile definiert den Inhalt '"sort.newest": "Neueste",'.
25. Diese Zeile definiert den Inhalt '"sort.oldest": "Aelteste",'.
26. Diese Zeile definiert den Inhalt '"sort.highest_rated": "Beste Bewertung",'.
27. Diese Zeile definiert den Inhalt '"sort.lowest_rated": "Schlechteste Bewertung",'.
28. Diese Zeile definiert den Inhalt '"sort.prep_time": "Zubereitungszeit",'.
29. Diese Zeile definiert den Inhalt '"pagination.previous": "Zurueck",'.
30. Diese Zeile definiert den Inhalt '"pagination.next": "Weiter",'.
31. Diese Zeile definiert den Inhalt '"pagination.first": "Erste",'.
32. Diese Zeile definiert den Inhalt '"pagination.last": "Letzte",'.
33. Diese Zeile definiert den Inhalt '"pagination.page": "Seite",'.
34. Diese Zeile definiert den Inhalt '"pagination.results_range": "Zeige {start}-{end} von {total} Rezepten",'.
35. Diese Zeile definiert den Inhalt '"difficulty.easy": "Einfach",'.
36. Diese Zeile definiert den Inhalt '"difficulty.medium": "Mittel",'.
37. Diese Zeile definiert den Inhalt '"difficulty.hard": "Schwer",'.
38. Diese Zeile definiert den Inhalt '"role.user": "Nutzer",'.
39. Diese Zeile definiert den Inhalt '"role.admin": "Administrator",'.
40. Diese Zeile definiert den Inhalt '"auth.login_title": "Anmelden",'.
41. Diese Zeile definiert den Inhalt '"auth.register_title": "Registrieren",'.
42. Diese Zeile definiert den Inhalt '"auth.email": "E-Mail",'.
43. Diese Zeile definiert den Inhalt '"auth.password": "Passwort",'.
44. Diese Zeile definiert den Inhalt '"auth.login_button": "Anmelden",'.
45. Diese Zeile definiert den Inhalt '"auth.register_button": "Konto erstellen",'.
46. Diese Zeile definiert den Inhalt '"profile.title": "Mein Profil",'.
47. Diese Zeile definiert den Inhalt '"profile.email": "E-Mail",'.
48. Diese Zeile definiert den Inhalt '"profile.role": "Rolle",'.
49. Diese Zeile definiert den Inhalt '"profile.joined": "Registriert am",'.
50. Diese Zeile definiert den Inhalt '"favorites.title": "Favoriten",'.
51. Diese Zeile definiert den Inhalt '"favorites.remove": "Favorit entfernen",'.
52. Diese Zeile definiert den Inhalt '"favorites.empty": "Keine Favoriten gespeichert.",'.
53. Diese Zeile definiert den Inhalt '"my_recipes.title": "Meine Rezepte",'.
54. Diese Zeile definiert den Inhalt '"my_recipes.empty": "Noch keine Rezepte vorhanden.",'.
55. Diese Zeile definiert den Inhalt '"recipe.edit": "Bearbeiten",'.
56. Diese Zeile definiert den Inhalt '"recipe.delete": "Loeschen",'.
57. Diese Zeile definiert den Inhalt '"recipe.pdf_download": "PDF herunterladen",'.
58. Diese Zeile definiert den Inhalt '"recipe.average_rating": "Durchschnittliche Bewertung",'.
59. Diese Zeile definiert den Inhalt '"recipe.review_count_label": "Bewertungen",'.
60. Diese Zeile definiert den Inhalt '"recipe.ingredients": "Zutaten",'.
61. Diese Zeile definiert den Inhalt '"recipe.instructions": "Anleitung",'.
62. Diese Zeile definiert den Inhalt '"recipe.reviews": "Bewertungen",'.
63. Diese Zeile definiert den Inhalt '"recipe.rating": "Bewertung",'.
64. Diese Zeile definiert den Inhalt '"recipe.comment": "Kommentar",'.
65. Diese Zeile definiert den Inhalt '"recipe.save_review": "Bewertung speichern",'.
66. Diese Zeile definiert den Inhalt '"recipe.no_ingredients": "Keine Zutaten gespeichert.",'.
67. Diese Zeile definiert den Inhalt '"recipe.no_reviews": "Noch keine Bewertungen vorhanden.",'.
68. Diese Zeile definiert den Inhalt '"recipe.no_results": "Keine Rezepte gefunden.",'.
69. Diese Zeile definiert den Inhalt '"recipe.rating_short": "Bewertung",'.
70. Diese Zeile definiert den Inhalt '"recipe_form.create_title": "Rezept veroeffentlichen",'.
71. Diese Zeile definiert den Inhalt '"recipe_form.edit_title": "Rezept bearbeiten",'.
72. Diese Zeile definiert den Inhalt '"recipe_form.title": "Titel",'.
73. Diese Zeile definiert den Inhalt '"recipe_form.title_image_url": "Titelbild-URL",'.
74. Diese Zeile definiert den Inhalt '"recipe_form.description": "Beschreibung",'.
75. Diese Zeile definiert den Inhalt '"recipe_form.instructions": "Anleitung",'.
76. Diese Zeile definiert den Inhalt '"recipe_form.category": "Kategorie",'.
77. Diese Zeile definiert den Inhalt '"recipe_form.new_category_option": "Neue Kategorie...",'.
78. Diese Zeile definiert den Inhalt '"recipe_form.new_category_label": "Neue Kategorie",'.
79. Diese Zeile definiert den Inhalt '"recipe_form.prep_time": "Zubereitungszeit (Minuten)",'.
80. Diese Zeile definiert den Inhalt '"recipe_form.difficulty": "Schwierigkeit",'.
81. Diese Zeile definiert den Inhalt '"recipe_form.ingredients": "Zutaten (Format: name|menge|gramm)",'.
82. Diese Zeile definiert den Inhalt '"recipe_form.optional_image": "Optionales Bild",'.
83. Diese Zeile definiert den Inhalt '"recipe_form.save": "Speichern",'.
84. Diese Zeile definiert den Inhalt '"recipe_form.create": "Erstellen",'.
85. Diese Zeile definiert den Inhalt '"submission.submit_title": "Rezept einreichen",'.
86. Diese Zeile definiert den Inhalt '"submission.submit_hint": "Einreichungen werden vor der Veroeffentlichung durch das Adm...'.
87. Diese Zeile definiert den Inhalt '"submission.submitter_email": "Kontakt-E-Mail (optional)",'.
88. Diese Zeile definiert den Inhalt '"submission.title": "Titel",'.
89. Diese Zeile definiert den Inhalt '"submission.description": "Beschreibung",'.
90. Diese Zeile definiert den Inhalt '"submission.instructions": "Anleitung",'.
91. Diese Zeile definiert den Inhalt '"submission.category": "Kategorie",'.
92. Diese Zeile definiert den Inhalt '"submission.new_category_option": "Neue Kategorie...",'.
93. Diese Zeile definiert den Inhalt '"submission.new_category_label": "Neue Kategorie",'.
94. Diese Zeile definiert den Inhalt '"submission.difficulty": "Schwierigkeit",'.
95. Diese Zeile definiert den Inhalt '"submission.prep_time": "Zubereitungszeit (Minuten, optional)",'.
96. Diese Zeile definiert den Inhalt '"submission.servings": "Portionen (optional)",'.
97. Diese Zeile definiert den Inhalt '"submission.ingredients": "Zutaten (Format: name|menge|gramm)",'.
98. Diese Zeile definiert den Inhalt '"submission.image_optional": "Optionales Bild",'.
99. Diese Zeile definiert den Inhalt '"submission.submit_button": "Zur Pruefung einreichen",'.
100. Diese Zeile definiert den Inhalt '"submission.default_description": "Rezept-Einreichung",'.
101. Diese Zeile definiert den Inhalt '"submission.thank_you": "Vielen Dank! Dein Rezept wurde eingereicht und wird geprueft.",'.
102. Diese Zeile definiert den Inhalt '"submission.my_title": "Meine Einreichungen",'.
103. Diese Zeile definiert den Inhalt '"submission.my_submitted_message": "Deine Einreichung wurde gespeichert und wartet auf ...'.
104. Diese Zeile definiert den Inhalt '"submission.my_empty": "Du hast noch keine Einreichungen.",'.
105. Diese Zeile definiert den Inhalt '"submission.admin_note": "Admin-Notiz",'.
106. Diese Zeile definiert den Inhalt '"submission.status_pending": "Ausstehend",'.
107. Diese Zeile definiert den Inhalt '"submission.status_approved": "Freigegeben",'.
108. Diese Zeile definiert den Inhalt '"submission.status_rejected": "Abgelehnt",'.
109. Diese Zeile definiert den Inhalt '"submission.status_all": "Alle",'.
110. Diese Zeile definiert den Inhalt '"submission.admin_queue_title": "Moderations-Warteschlange",'.
111. Diese Zeile definiert den Inhalt '"submission.status_filter": "Status",'.
112. Diese Zeile definiert den Inhalt '"submission.stats_pending": "Ausstehend",'.
113. Diese Zeile definiert den Inhalt '"submission.stats_approved": "Freigegeben",'.
114. Diese Zeile definiert den Inhalt '"submission.stats_rejected": "Abgelehnt",'.
115. Diese Zeile definiert den Inhalt '"submission.table_date": "Datum",'.
116. Diese Zeile definiert den Inhalt '"submission.table_title": "Titel",'.
117. Diese Zeile definiert den Inhalt '"submission.table_submitter": "Einreicher",'.
118. Diese Zeile definiert den Inhalt '"submission.table_status": "Status",'.
119. Diese Zeile definiert den Inhalt '"submission.table_action": "Aktion",'.
120. Diese Zeile definiert den Inhalt '"submission.open_detail": "Details",'.
121. Diese Zeile definiert den Inhalt '"submission.admin_empty": "Keine Einreichungen gefunden.",'.
122. Diese Zeile definiert den Inhalt '"submission.admin_detail_title": "Einreichung",'.
123. Diese Zeile definiert den Inhalt '"submission.back_to_queue": "Zurueck zur Warteschlange",'.
124. Diese Zeile definiert den Inhalt '"submission.preview": "Vorschau",'.
125. Diese Zeile definiert den Inhalt '"submission.edit_submission": "Einreichung bearbeiten",'.
126. Diese Zeile definiert den Inhalt '"submission.set_primary_new_image": "Neues Bild als Hauptbild setzen",'.
127. Diese Zeile definiert den Inhalt '"submission.save_changes": "Aenderungen speichern",'.
128. Diese Zeile definiert den Inhalt '"submission.moderation_actions": "Moderations-Aktionen",'.
129. Diese Zeile definiert den Inhalt '"submission.optional_admin_note": "Admin-Notiz (optional)",'.
130. Diese Zeile definiert den Inhalt '"submission.approve_button": "Freigeben",'.
131. Diese Zeile definiert den Inhalt '"submission.reject_reason": "Ablehnungsgrund",'.
132. Diese Zeile definiert den Inhalt '"submission.reject_button": "Ablehnen",'.
133. Diese Zeile definiert den Inhalt '"submission.approved": "Einreichung wurde freigegeben.",'.
134. Diese Zeile definiert den Inhalt '"submission.rejected": "Einreichung wurde abgelehnt.",'.
135. Diese Zeile definiert den Inhalt '"submission.updated": "Einreichung wurde aktualisiert.",'.
136. Diese Zeile definiert den Inhalt '"submission.image_deleted": "Bild wurde entfernt.",'.
137. Diese Zeile definiert den Inhalt '"submission.image_primary": "Hauptbild wurde gesetzt.",'.
138. Diese Zeile definiert den Inhalt '"submission.admin_queue_link": "Zur Moderations-Warteschlange",'.
139. Diese Zeile definiert den Inhalt '"submission.guest": "Gast",'.
140. Diese Zeile definiert den Inhalt '"images.title": "Bilder",'.
141. Diese Zeile definiert den Inhalt '"images.new_file": "Neue Bilddatei",'.
142. Diese Zeile definiert den Inhalt '"images.set_primary": "Als Hauptbild setzen",'.
143. Diese Zeile definiert den Inhalt '"images.upload": "Bild hochladen",'.
144. Diese Zeile definiert den Inhalt '"images.primary": "Hauptbild",'.
145. Diese Zeile definiert den Inhalt '"images.delete": "Loeschen",'.
146. Diese Zeile definiert den Inhalt '"images.empty": "Noch keine Bilder vorhanden.",'.
147. Diese Zeile definiert den Inhalt '"favorite.add": "Zu Favoriten",'.
148. Diese Zeile definiert den Inhalt '"favorite.remove": "Aus Favoriten entfernen",'.
149. Diese Zeile definiert den Inhalt '"admin.title": "Admin-Bereich",'.
150. Diese Zeile definiert den Inhalt '"admin.seed_title": "KochWiki-Seed (einmalig)",'.
151. Diese Zeile definiert den Inhalt '"admin.csv_path": "CSV-Pfad",'.
152. Diese Zeile definiert den Inhalt '"admin.seed_done": "Seed-Status: bereits ausgefuehrt.",'.
153. Diese Zeile definiert den Inhalt '"admin.seed_run": "Einmaligen KochWiki-Seed ausfuehren",'.
154. Diese Zeile definiert den Inhalt '"admin.import_title": "CSV manuell importieren",'.
155. Diese Zeile definiert den Inhalt '"admin.import_help_title": "CSV-Format Hilfe",'.
156. Diese Zeile definiert den Inhalt '"admin.import_help_intro": "Bitte nutze das kanonische Importformat, damit der Import s...'.
157. Diese Zeile definiert den Inhalt '"admin.import_required_columns": "Pflichtspalten: title, instructions",'.
158. Diese Zeile definiert den Inhalt '"admin.import_optional_columns": "Empfohlene Spalten: description, category, difficulty...'.
159. Diese Zeile definiert den Inhalt '"admin.import_difficulty_values": "Difficulty-Werte: easy, medium, hard",'.
160. Diese Zeile definiert den Inhalt '"admin.import_ingredients_example": "Ingredients Beispiel: 2 Eier | 200g Mehl | 1 Prise...'.
161. Diese Zeile definiert den Inhalt '"admin.import_encoding_delimiter": "Encoding: utf-8-sig, Delimiter standardmaessig ';' ...'.
162. Diese Zeile definiert den Inhalt '"admin.download_template": "CSV Template herunterladen",'.
163. Diese Zeile definiert den Inhalt '"admin.download_example": "CSV Beispiel herunterladen",'.
164. Diese Zeile definiert den Inhalt '"admin.upload_label": "CSV-Upload",'.
165. Diese Zeile definiert den Inhalt '"admin.insert_only": "Nur neue hinzufuegen (UPSERT SAFE)",'.
166. Diese Zeile definiert den Inhalt '"admin.update_existing": "Existierende aktualisieren (Warnung: nur ausgewaehlte Felder!)",'.
167. Diese Zeile definiert den Inhalt '"admin.dry_run": "Nur pruefen (Dry Run)",'.
168. Diese Zeile definiert den Inhalt '"admin.force_with_warnings": "Trotz Warnungen fortsetzen",'.
169. Diese Zeile definiert den Inhalt '"admin.import_warning_text": "Standard ist Insert-Only; Update Existing nur aktivieren,...'.
170. Diese Zeile definiert den Inhalt '"admin.preview_button": "Vorschau erstellen",'.
171. Diese Zeile definiert den Inhalt '"admin.preview_done": "Vorschau wurde erstellt.",'.
172. Diese Zeile definiert den Inhalt '"admin.preview_title": "Import-Vorschau",'.
173. Diese Zeile definiert den Inhalt '"admin.preview_total_rows": "Gesamtzeilen",'.
174. Diese Zeile definiert den Inhalt '"admin.preview_delimiter": "Erkannter Delimiter",'.
175. Diese Zeile definiert den Inhalt '"admin.preview_fatal_rows": "Zeilen mit Fehlern",'.
176. Diese Zeile definiert den Inhalt '"admin.preview_row": "Zeile",'.
177. Diese Zeile definiert den Inhalt '"admin.preview_status": "Status",'.
178. Diese Zeile definiert den Inhalt '"admin.preview_notes": "Hinweise",'.
179. Diese Zeile definiert den Inhalt '"admin.preview_errors_title": "Fehlerliste",'.
180. Diese Zeile definiert den Inhalt '"admin.preview_warnings_title": "Warnungsliste",'.
181. Diese Zeile definiert den Inhalt '"admin.import_result_title": "Import-Ergebnis",'.
182. Diese Zeile definiert den Inhalt '"admin.import_blocked_errors": "Import blockiert: Bitte behebe zuerst die fehlerhaften ...'.
183. Diese Zeile definiert den Inhalt '"admin.confirm_warnings_required": "Warnungen vorhanden: Setze 'Trotz Warnungen fortset...'.
184. Diese Zeile definiert den Inhalt '"admin.dry_run_done": "Dry-Run abgeschlossen, es wurden keine Daten geschrieben.",'.
185. Diese Zeile definiert den Inhalt '"admin.start_import": "Import starten",'.
186. Diese Zeile definiert den Inhalt '"admin.report_inserted": "Neu",'.
187. Diese Zeile definiert den Inhalt '"admin.report_updated": "Aktualisiert",'.
188. Diese Zeile definiert den Inhalt '"admin.report_skipped": "Uebersprungen",'.
189. Diese Zeile definiert den Inhalt '"admin.report_errors": "Fehler",'.
190. Diese Zeile definiert den Inhalt '"admin.report_warnings": "Warnungen",'.
191. Diese Zeile definiert den Inhalt '"admin.users": "Nutzer",'.
192. Diese Zeile definiert den Inhalt '"admin.recipes": "Rezepte",'.
193. Diese Zeile definiert den Inhalt '"admin.category_stats_title": "Kategorien-Status",'.
194. Diese Zeile definiert den Inhalt '"admin.category_distinct_count": "Anzahl eindeutiger Kategorien",'.
195. Diese Zeile definiert den Inhalt '"admin.category_top": "Top 10 Kategorien",'.
196. Diese Zeile definiert den Inhalt '"admin.id": "ID",'.
197. Diese Zeile definiert den Inhalt '"admin.email": "E-Mail",'.
198. Diese Zeile definiert den Inhalt '"admin.role": "Rolle",'.
199. Diese Zeile definiert den Inhalt '"admin.action": "Aktion",'.
200. Diese Zeile definiert den Inhalt '"admin.save": "Speichern",'.
201. Diese Zeile definiert den Inhalt '"admin.title_column": "Titel",'.
202. Diese Zeile definiert den Inhalt '"admin.creator": "Ersteller",'.
203. Diese Zeile definiert den Inhalt '"admin.source": "Quelle",'.
204. Diese Zeile definiert den Inhalt '"error.404_title": "404 - Seite nicht gefunden",'.
205. Diese Zeile definiert den Inhalt '"error.404_text": "Die angeforderte Seite existiert nicht oder wurde verschoben.",'.
206. Diese Zeile definiert den Inhalt '"error.500_title": "500 - Interner Fehler",'.
207. Diese Zeile definiert den Inhalt '"error.500_text": "Beim Verarbeiten der Anfrage ist ein unerwarteter Fehler aufgetreten.",'.
208. Diese Zeile definiert den Inhalt '"error.home_link": "Zur Startseite",'.
209. Diese Zeile definiert den Inhalt '"error.trace": "Stacktrace (nur Dev)",'.
210. Diese Zeile definiert den Inhalt '"error.auth_required": "Anmeldung erforderlich.",'.
211. Diese Zeile definiert den Inhalt '"error.admin_required": "Administratorrechte erforderlich.",'.
212. Diese Zeile definiert den Inhalt '"error.invalid_credentials": "Ungueltige Zugangsdaten.",'.
213. Diese Zeile definiert den Inhalt '"error.email_registered": "Diese E-Mail ist bereits registriert.",'.
214. Diese Zeile definiert den Inhalt '"error.password_min_length": "Das Passwort muss mindestens 10 Zeichen enthalten.",'.
215. Diese Zeile definiert den Inhalt '"error.password_upper": "Das Passwort muss mindestens einen Grossbuchstaben enthalten.",'.
216. Diese Zeile definiert den Inhalt '"error.password_number": "Das Passwort muss mindestens eine Zahl enthalten.",'.
217. Diese Zeile definiert den Inhalt '"error.password_special": "Das Passwort muss mindestens ein Sonderzeichen enthalten.",'.
218. Diese Zeile definiert den Inhalt '"error.role_invalid": "Die Rolle muss 'user' oder 'admin' sein.",'.
219. Diese Zeile definiert den Inhalt '"error.user_not_found": "Nutzer nicht gefunden.",'.
220. Diese Zeile definiert den Inhalt '"error.recipe_not_found": "Rezept nicht gefunden.",'.
221. Diese Zeile definiert den Inhalt '"error.submission_not_found": "Einreichung nicht gefunden.",'.
222. Diese Zeile definiert den Inhalt '"error.review_not_found": "Bewertung nicht gefunden.",'.
223. Diese Zeile definiert den Inhalt '"error.image_not_found": "Bild nicht gefunden.",'.
224. Diese Zeile definiert den Inhalt '"error.recipe_permission": "Keine ausreichenden Rechte fuer dieses Rezept.",'.
225. Diese Zeile definiert den Inhalt '"error.submission_permission": "Keine ausreichenden Rechte fuer diese Einreichung.",'.
226. Diese Zeile definiert den Inhalt '"error.review_permission": "Keine ausreichenden Rechte fuer diese Bewertung.",'.
227. Diese Zeile definiert den Inhalt '"error.rating_range": "Die Bewertung muss zwischen 1 und 5 liegen.",'.
228. Diese Zeile definiert den Inhalt '"error.title_instructions_required": "Titel und Anleitung sind erforderlich.",'.
229. Diese Zeile definiert den Inhalt '"error.image_url_scheme": "Die title_image_url muss mit http:// oder https:// beginnen.",'.
230. Diese Zeile definiert den Inhalt '"error.no_image_url": "Keine Bild-URL verfuegbar.",'.
231. Diese Zeile definiert den Inhalt '"error.image_resolve_prefix": "Die Bild-URL konnte nicht aufgeloest werden",'.
232. Diese Zeile definiert den Inhalt '"error.seed_already_done": "Der KochWiki-Seed ist bereits als abgeschlossen markiert.",'.
233. Diese Zeile definiert den Inhalt '"error.seed_not_empty": "Der Seed darf nur bei leerer Rezepttabelle laufen.",'.
234. Diese Zeile definiert den Inhalt '"error.seed_finished_errors": "Der Seed wurde mit Fehlern beendet; Marker wurde nicht g...'.
235. Diese Zeile definiert den Inhalt '"error.seed_success": "Der KochWiki-Seed wurde erfolgreich abgeschlossen und markiert.",'.
236. Diese Zeile definiert den Inhalt '"error.csv_upload_required": "Bitte eine CSV-Datei hochladen.",'.
237. Diese Zeile definiert den Inhalt '"error.csv_only": "Es sind nur CSV-Uploads erlaubt.",'.
238. Diese Zeile definiert den Inhalt '"error.csv_too_large": "CSV-Upload ist zu gross.",'.
239. Diese Zeile definiert den Inhalt '"error.csv_empty": "Die hochgeladene CSV-Datei ist leer.",'.
240. Diese Zeile definiert den Inhalt '"error.csv_not_found_prefix": "CSV-Datei nicht gefunden",'.
241. Diese Zeile definiert den Inhalt '"error.import_finished_insert": "Import im Modus 'nur neu' abgeschlossen.",'.
242. Diese Zeile definiert den Inhalt '"error.import_finished_update": "Import im Modus 'bestehende aktualisieren' abgeschloss...'.
243. Diese Zeile definiert den Inhalt '"error.submission_already_published": "Diese Einreichung wurde bereits veroeffentlicht.",'.
244. Diese Zeile definiert den Inhalt '"error.submission_reject_reason_required": "Bitte einen Ablehnungsgrund angeben.",'.
245. Diese Zeile definiert den Inhalt '"error.csrf_failed": "CSRF-Pruefung fehlgeschlagen.",'.
246. Diese Zeile definiert den Inhalt '"error.internal": "Interner Serverfehler.",'.
247. Diese Zeile definiert den Inhalt '"error.not_found": "Ressource nicht gefunden.",'.
248. Diese Zeile definiert den Inhalt '"error.field_int": "{field} muss eine ganze Zahl sein.",'.
249. Diese Zeile definiert den Inhalt '"error.field_positive": "{field} muss groesser als null sein.",'.
250. Diese Zeile definiert den Inhalt '"error.mime_unsupported": "Nicht unterstuetzter MIME-Typ '{content_type}'.",'.
251. Diese Zeile definiert den Inhalt '"error.magic_mismatch": "Dateisignatur passt nicht zum Content-Type.",'.
252. Diese Zeile definiert den Inhalt '"error.webp_signature": "Ungueltige WEBP-Dateisignatur.",'.
253. Diese Zeile definiert den Inhalt '"error.image_too_large": "Bild ist zu gross. Maximal {max_mb} MB.",'.
254. Diese Zeile definiert den Inhalt '"error.image_too_small": "Die hochgeladene Datei ist zu klein fuer ein gueltiges Bild.",'.
255. Diese Zeile definiert den Inhalt '"error.image_invalid": "Die hochgeladene Datei ist kein gueltiges Bild.",'.
256. Diese Zeile definiert den Inhalt '"error.image_format_mismatch": "Das Bildformat passt nicht zum Content-Type.",'.
257. Diese Zeile definiert den Inhalt '}'.

## app/moderation_repair.py
```python
from dataclasses import dataclass, field

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models import Recipe, RecipeIngredient, RecipeSubmission, SubmissionImage, User
from app.services import DEFAULT_CATEGORY, normalize_category, replace_submission_ingredients, sanitize_difficulty


@dataclass
class ModerationRepairReport:
    dry_run: bool
    scanned_count: int = 0
    affected_count: int = 0
    moved_to_pending_count: int = 0
    skipped_count: int = 0
    details: list[str] = field(default_factory=list)


def _suspicious_recipes_query():
    return (
        select(Recipe)
        .join(User, User.id == Recipe.creator_id)
        .where(
            Recipe.is_published.is_(True),
            User.role != "admin",
            Recipe.source != "kochwiki",
        )
        .options(
            joinedload(Recipe.creator),
            selectinload(Recipe.recipe_ingredients).joinedload(RecipeIngredient.ingredient),
            selectinload(Recipe.images),
        )
        .order_by(Recipe.id.asc())
    )


def _copy_recipe_to_pending_submission(db: Session, recipe: Recipe) -> RecipeSubmission:
    submission = RecipeSubmission(
        submitter_user_id=recipe.creator_id,
        submitter_email=None,
        title=recipe.title.strip()[:255],
        description=recipe.description.strip() or "Aus veroeffentlichtem Rezept zur Moderation uebernommen.",
        category=normalize_category(recipe.category or DEFAULT_CATEGORY),
        difficulty=sanitize_difficulty(recipe.difficulty or "medium"),
        prep_time_minutes=recipe.prep_time_minutes,
        servings_text=(recipe.servings_text or "").strip()[:120] or None,
        instructions=recipe.instructions.strip(),
        status="pending",
        admin_note=f"Auto-Reparatur: Rezept {recipe.id} wurde zur Moderation verschoben.",
    )
    db.add(submission)
    db.flush()

    ingredient_entries: list[dict[str, object]] = []
    for link in recipe.recipe_ingredients:
        ingredient_entries.append(
            {
                "name": link.ingredient.name if link.ingredient else "",
                "quantity_text": link.quantity_text,
                "grams": link.grams,
            }
        )
    replace_submission_ingredients(db, submission, ingredient_entries)

    any_primary = False
    first_copy: SubmissionImage | None = None
    for image in recipe.images:
        copied = SubmissionImage(
            submission_id=submission.id,
            filename=image.filename,
            content_type=image.content_type,
            data=image.data,
            is_primary=image.is_primary,
        )
        db.add(copied)
        if first_copy is None:
            first_copy = copied
        any_primary = any_primary or image.is_primary
    if first_copy and not any_primary:
        first_copy.is_primary = True

    return submission


def run_moderation_repair(db: Session, dry_run: bool = True) -> ModerationRepairReport:
    report = ModerationRepairReport(dry_run=dry_run)
    recipes = db.scalars(_suspicious_recipes_query()).all()
    report.scanned_count = len(recipes)
    for recipe in recipes:
        report.affected_count += 1
        report.details.append(
            f"recipe_id={recipe.id} title={recipe.title!r} creator={recipe.creator.email if recipe.creator else recipe.creator_id}"
        )
        if dry_run:
            continue
        _copy_recipe_to_pending_submission(db, recipe)
        recipe.is_published = False
        db.add(recipe)
        report.moved_to_pending_count += 1
    report.skipped_count = report.scanned_count - report.affected_count
    return report
```
ZEILEN-ERKL?RUNG
1. Diese Zeile definiert den Inhalt 'from dataclasses import dataclass, field'.
2. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
3. Diese Zeile definiert den Inhalt 'from sqlalchemy import select'.
4. Diese Zeile definiert den Inhalt 'from sqlalchemy.orm import Session, joinedload, selectinload'.
5. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
6. Diese Zeile definiert den Inhalt 'from app.models import Recipe, RecipeIngredient, RecipeSubmission, SubmissionImage, User'.
7. Diese Zeile definiert den Inhalt 'from app.services import DEFAULT_CATEGORY, normalize_category, replace_submission_ingre...'.
8. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
9. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
10. Diese Zeile definiert den Inhalt '@dataclass'.
11. Diese Zeile definiert den Inhalt 'class ModerationRepairReport:'.
12. Diese Zeile definiert den Inhalt 'dry_run: bool'.
13. Diese Zeile definiert den Inhalt 'scanned_count: int = 0'.
14. Diese Zeile definiert den Inhalt 'affected_count: int = 0'.
15. Diese Zeile definiert den Inhalt 'moved_to_pending_count: int = 0'.
16. Diese Zeile definiert den Inhalt 'skipped_count: int = 0'.
17. Diese Zeile definiert den Inhalt 'details: list[str] = field(default_factory=list)'.
18. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
19. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
20. Diese Zeile definiert den Inhalt 'def _suspicious_recipes_query():'.
21. Diese Zeile definiert den Inhalt 'return ('.
22. Diese Zeile definiert den Inhalt 'select(Recipe)'.
23. Diese Zeile definiert den Inhalt '.join(User, User.id == Recipe.creator_id)'.
24. Diese Zeile definiert den Inhalt '.where('.
25. Diese Zeile definiert den Inhalt 'Recipe.is_published.is_(True),'.
26. Diese Zeile definiert den Inhalt 'User.role != "admin",'.
27. Diese Zeile definiert den Inhalt 'Recipe.source != "kochwiki",'.
28. Diese Zeile definiert den Inhalt ')'.
29. Diese Zeile definiert den Inhalt '.options('.
30. Diese Zeile definiert den Inhalt 'joinedload(Recipe.creator),'.
31. Diese Zeile definiert den Inhalt 'selectinload(Recipe.recipe_ingredients).joinedload(RecipeIngredient.ingredient),'.
32. Diese Zeile definiert den Inhalt 'selectinload(Recipe.images),'.
33. Diese Zeile definiert den Inhalt ')'.
34. Diese Zeile definiert den Inhalt '.order_by(Recipe.id.asc())'.
35. Diese Zeile definiert den Inhalt ')'.
36. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
37. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
38. Diese Zeile definiert den Inhalt 'def _copy_recipe_to_pending_submission(db: Session, recipe: Recipe) -> RecipeSubmission:'.
39. Diese Zeile definiert den Inhalt 'submission = RecipeSubmission('.
40. Diese Zeile definiert den Inhalt 'submitter_user_id=recipe.creator_id,'.
41. Diese Zeile definiert den Inhalt 'submitter_email=None,'.
42. Diese Zeile definiert den Inhalt 'title=recipe.title.strip()[:255],'.
43. Diese Zeile definiert den Inhalt 'description=recipe.description.strip() or "Aus veroeffentlichtem Rezept zur Moderation ...'.
44. Diese Zeile definiert den Inhalt 'category=normalize_category(recipe.category or DEFAULT_CATEGORY),'.
45. Diese Zeile definiert den Inhalt 'difficulty=sanitize_difficulty(recipe.difficulty or "medium"),'.
46. Diese Zeile definiert den Inhalt 'prep_time_minutes=recipe.prep_time_minutes,'.
47. Diese Zeile definiert den Inhalt 'servings_text=(recipe.servings_text or "").strip()[:120] or None,'.
48. Diese Zeile definiert den Inhalt 'instructions=recipe.instructions.strip(),'.
49. Diese Zeile definiert den Inhalt 'status="pending",'.
50. Diese Zeile definiert den Inhalt 'admin_note=f"Auto-Reparatur: Rezept {recipe.id} wurde zur Moderation verschoben.",'.
51. Diese Zeile definiert den Inhalt ')'.
52. Diese Zeile definiert den Inhalt 'db.add(submission)'.
53. Diese Zeile definiert den Inhalt 'db.flush()'.
54. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
55. Diese Zeile definiert den Inhalt 'ingredient_entries: list[dict[str, object]] = []'.
56. Diese Zeile definiert den Inhalt 'for link in recipe.recipe_ingredients:'.
57. Diese Zeile definiert den Inhalt 'ingredient_entries.append('.
58. Diese Zeile definiert den Inhalt '{'.
59. Diese Zeile definiert den Inhalt '"name": link.ingredient.name if link.ingredient else "",'.
60. Diese Zeile definiert den Inhalt '"quantity_text": link.quantity_text,'.
61. Diese Zeile definiert den Inhalt '"grams": link.grams,'.
62. Diese Zeile definiert den Inhalt '}'.
63. Diese Zeile definiert den Inhalt ')'.
64. Diese Zeile definiert den Inhalt 'replace_submission_ingredients(db, submission, ingredient_entries)'.
65. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
66. Diese Zeile definiert den Inhalt 'any_primary = False'.
67. Diese Zeile definiert den Inhalt 'first_copy: SubmissionImage | None = None'.
68. Diese Zeile definiert den Inhalt 'for image in recipe.images:'.
69. Diese Zeile definiert den Inhalt 'copied = SubmissionImage('.
70. Diese Zeile definiert den Inhalt 'submission_id=submission.id,'.
71. Diese Zeile definiert den Inhalt 'filename=image.filename,'.
72. Diese Zeile definiert den Inhalt 'content_type=image.content_type,'.
73. Diese Zeile definiert den Inhalt 'data=image.data,'.
74. Diese Zeile definiert den Inhalt 'is_primary=image.is_primary,'.
75. Diese Zeile definiert den Inhalt ')'.
76. Diese Zeile definiert den Inhalt 'db.add(copied)'.
77. Diese Zeile definiert den Inhalt 'if first_copy is None:'.
78. Diese Zeile definiert den Inhalt 'first_copy = copied'.
79. Diese Zeile definiert den Inhalt 'any_primary = any_primary or image.is_primary'.
80. Diese Zeile definiert den Inhalt 'if first_copy and not any_primary:'.
81. Diese Zeile definiert den Inhalt 'first_copy.is_primary = True'.
82. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
83. Diese Zeile definiert den Inhalt 'return submission'.
84. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
85. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
86. Diese Zeile definiert den Inhalt 'def run_moderation_repair(db: Session, dry_run: bool = True) -> ModerationRepairReport:'.
87. Diese Zeile definiert den Inhalt 'report = ModerationRepairReport(dry_run=dry_run)'.
88. Diese Zeile definiert den Inhalt 'recipes = db.scalars(_suspicious_recipes_query()).all()'.
89. Diese Zeile definiert den Inhalt 'report.scanned_count = len(recipes)'.
90. Diese Zeile definiert den Inhalt 'for recipe in recipes:'.
91. Diese Zeile definiert den Inhalt 'report.affected_count += 1'.
92. Diese Zeile definiert den Inhalt 'report.details.append('.
93. Diese Zeile definiert den Inhalt 'f"recipe_id={recipe.id} title={recipe.title!r} creator={recipe.creator.email if recipe....'.
94. Diese Zeile definiert den Inhalt ')'.
95. Diese Zeile definiert den Inhalt 'if dry_run:'.
96. Diese Zeile definiert den Inhalt 'continue'.
97. Diese Zeile definiert den Inhalt '_copy_recipe_to_pending_submission(db, recipe)'.
98. Diese Zeile definiert den Inhalt 'recipe.is_published = False'.
99. Diese Zeile definiert den Inhalt 'db.add(recipe)'.
100. Diese Zeile definiert den Inhalt 'report.moved_to_pending_count += 1'.
101. Diese Zeile definiert den Inhalt 'report.skipped_count = report.scanned_count - report.affected_count'.
102. Diese Zeile definiert den Inhalt 'return report'.

## scripts/moderation_repair.py
```python
import argparse
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.database import SessionLocal
from app.moderation_repair import run_moderation_repair


def main() -> None:
    parser = argparse.ArgumentParser(description="Repair moderation visibility by moving non-admin published recipes to pending submissions.")
    parser.add_argument("--apply", action="store_true", help="Apply changes. Without this flag, only dry-run is executed.")
    parser.add_argument("--verbose", action="store_true", help="Print per-recipe detail lines.")
    args = parser.parse_args()

    db = SessionLocal()
    try:
        report = run_moderation_repair(db, dry_run=not args.apply)
        if args.apply:
            db.commit()
        else:
            db.rollback()
        print("Moderation repair finished.")
        print(f"dry_run={report.dry_run}")
        print(f"scanned_count={report.scanned_count}")
        print(f"affected_count={report.affected_count}")
        print(f"moved_to_pending_count={report.moved_to_pending_count}")
        print(f"skipped_count={report.skipped_count}")
        if args.verbose:
            for detail in report.details:
                print(f"- {detail}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
```
ZEILEN-ERKL?RUNG
1. Diese Zeile definiert den Inhalt 'import argparse'.
2. Diese Zeile definiert den Inhalt 'import sys'.
3. Diese Zeile definiert den Inhalt 'from pathlib import Path'.
4. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
5. Diese Zeile definiert den Inhalt 'sys.path.append(str(Path(__file__).resolve().parents[1]))'.
6. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
7. Diese Zeile definiert den Inhalt 'from app.database import SessionLocal'.
8. Diese Zeile definiert den Inhalt 'from app.moderation_repair import run_moderation_repair'.
9. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
10. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
11. Diese Zeile definiert den Inhalt 'def main() -> None:'.
12. Diese Zeile definiert den Inhalt 'parser = argparse.ArgumentParser(description="Repair moderation visibility by moving no...'.
13. Diese Zeile definiert den Inhalt 'parser.add_argument("--apply", action="store_true", help="Apply changes. Without this f...'.
14. Diese Zeile definiert den Inhalt 'parser.add_argument("--verbose", action="store_true", help="Print per-recipe detail lin...'.
15. Diese Zeile definiert den Inhalt 'args = parser.parse_args()'.
16. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
17. Diese Zeile definiert den Inhalt 'db = SessionLocal()'.
18. Diese Zeile definiert den Inhalt 'try:'.
19. Diese Zeile definiert den Inhalt 'report = run_moderation_repair(db, dry_run=not args.apply)'.
20. Diese Zeile definiert den Inhalt 'if args.apply:'.
21. Diese Zeile definiert den Inhalt 'db.commit()'.
22. Diese Zeile definiert den Inhalt 'else:'.
23. Diese Zeile definiert den Inhalt 'db.rollback()'.
24. Diese Zeile definiert den Inhalt 'print("Moderation repair finished.")'.
25. Diese Zeile definiert den Inhalt 'print(f"dry_run={report.dry_run}")'.
26. Diese Zeile definiert den Inhalt 'print(f"scanned_count={report.scanned_count}")'.
27. Diese Zeile definiert den Inhalt 'print(f"affected_count={report.affected_count}")'.
28. Diese Zeile definiert den Inhalt 'print(f"moved_to_pending_count={report.moved_to_pending_count}")'.
29. Diese Zeile definiert den Inhalt 'print(f"skipped_count={report.skipped_count}")'.
30. Diese Zeile definiert den Inhalt 'if args.verbose:'.
31. Diese Zeile definiert den Inhalt 'for detail in report.details:'.
32. Diese Zeile definiert den Inhalt 'print(f"- {detail}")'.
33. Diese Zeile definiert den Inhalt 'finally:'.
34. Diese Zeile definiert den Inhalt 'db.close()'.
35. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
36. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
37. Diese Zeile definiert den Inhalt 'if __name__ == "__main__":'.
38. Diese Zeile definiert den Inhalt 'main()'.

## scripts/seed_test_accounts_and_recipes.py
```python
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import select

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.config import get_settings
from app.database import SessionLocal
from app.models import Recipe, RecipeSubmission, User
from app.security import hash_password
from app.services import normalize_category, publish_submission_as_recipe, sanitize_difficulty

TEST_PASSWORD = "TestPass123!"
USER_COUNT = 15
ADMIN_COUNT = 3
RECIPES_PER_ADMIN = 3

CATEGORIES = [
    "Pasta",
    "Salat",
    "Suppe",
    "Dessert",
    "Fruehstueck",
    "Vegetarisch",
]
DIFFICULTIES = ["easy", "medium", "hard"]


def allow_moderation_fixtures() -> bool:
    settings = get_settings()
    return settings.app_env == "dev" or os.getenv("TESTING") == "1"


def ensure_user(db, email: str, role: str) -> tuple[User, str]:
    existing = db.scalar(select(User).where(User.email == email))
    if existing:
        changed = False
        if existing.role != role:
            existing.role = role
            changed = True
        if not existing.hashed_password:
            existing.hashed_password = hash_password(TEST_PASSWORD)
            changed = True
        return existing, "updated" if changed else "unchanged"
    user = User(email=email, hashed_password=hash_password(TEST_PASSWORD), role=role)
    db.add(user)
    db.flush()
    return user, "created"


def ensure_admin_recipe(db, owner: User, owner_index: int, recipe_index: int) -> bool:
    source_uuid = f"test-seed:admin:{owner_index:02d}:recipe:{recipe_index}"
    existing = db.scalar(select(Recipe).where(Recipe.source_uuid == source_uuid))
    if existing:
        return False
    category = normalize_category(CATEGORIES[(owner_index + recipe_index) % len(CATEGORIES)])
    difficulty = sanitize_difficulty(DIFFICULTIES[(owner_index + recipe_index - 1) % len(DIFFICULTIES)])
    db.add(
        Recipe(
            title=f"Testrezept ADMIN {owner_index:02d}-{recipe_index}",
            title_image_url=f"https://picsum.photos/seed/admin{owner_index:02d}{recipe_index}/640/360",
            description="Automatisch erzeugtes Admin-Testrezept fuer UI- und Workflow-Tests.",
            instructions=(
                "1. Zutaten vorbereiten.\n"
                "2. Alles nach Rezeptschritten kombinieren.\n"
                "3. Abschmecken und servieren."
            ),
            category=category,
            prep_time_minutes=15 + recipe_index * 10,
            difficulty=difficulty,
            creator_id=owner.id,
            source="test_seed",
            source_uuid=source_uuid,
            is_published=True,
        )
    )
    return True


def ensure_submission_fixture(
    db,
    *,
    title: str,
    submitter: User,
    admin: User,
    status: str,
    admin_note: str | None = None,
) -> tuple[RecipeSubmission, bool]:
    submission = db.scalar(select(RecipeSubmission).where(RecipeSubmission.title == title))
    created = False
    if not submission:
        submission = RecipeSubmission(
            submitter_user_id=submitter.id,
            submitter_email=None,
            title=title,
            description="Gezielte Moderations-Testeinreichung.",
            category=normalize_category("Test Kategorie"),
            difficulty="medium",
            prep_time_minutes=25,
            servings_text="2 Portionen",
            instructions="1. Testeinreichung vorbereiten.\n2. Speichern und Moderation pruefen.",
            status="pending",
        )
        db.add(submission)
        db.flush()
        created = True

    if status == "pending":
        if submission.status != "pending":
            submission.status = "pending"
            submission.admin_note = None
            submission.reviewed_by_admin_id = None
            submission.reviewed_at = None
        return submission, created

    if status == "rejected":
        submission.status = "rejected"
        submission.admin_note = admin_note or "Nicht ausreichend beschrieben."
        submission.reviewed_by_admin_id = admin.id
        submission.reviewed_at = datetime.now(timezone.utc)
        return submission, created

    if status == "approved":
        recipe = db.scalar(select(Recipe).where(Recipe.source_uuid == f"submission:{submission.id}"))
        if recipe is None:
            publish_submission_as_recipe(db, submission, admin.id)
        submission.status = "approved"
        submission.admin_note = admin_note or "Freigegeben fuer Discover."
        submission.reviewed_by_admin_id = admin.id
        submission.reviewed_at = datetime.now(timezone.utc)
        return submission, created

    raise ValueError(f"Unknown status: {status}")


def seed_test_data() -> None:
    db = SessionLocal()
    try:
        users_created = 0
        users_updated = 0
        admin_recipes_created = 0
        moderation_fixtures_created = 0

        test_users: list[User] = []
        test_admins: list[User] = []

        for index in range(1, USER_COUNT + 1):
            email = f"test.user{index:02d}@mealmate.local"
            user, state = ensure_user(db, email, "user")
            test_users.append(user)
            if state == "created":
                users_created += 1
            elif state == "updated":
                users_updated += 1

        for index in range(1, ADMIN_COUNT + 1):
            email = f"test.admin{index:02d}@mealmate.local"
            admin, state = ensure_user(db, email, "admin")
            test_admins.append(admin)
            if state == "created":
                users_created += 1
            elif state == "updated":
                users_updated += 1
            for recipe_index in range(1, RECIPES_PER_ADMIN + 1):
                if ensure_admin_recipe(db, admin, index, recipe_index):
                    admin_recipes_created += 1

        if allow_moderation_fixtures() and test_users and test_admins:
            submitter = test_users[0]
            reviewer = test_admins[0]
            for idx in range(1, 4):
                _, created = ensure_submission_fixture(
                    db,
                    title=f"Moderation Pending {idx}",
                    submitter=submitter,
                    admin=reviewer,
                    status="pending",
                )
                if created:
                    moderation_fixtures_created += 1
            _, created_rejected = ensure_submission_fixture(
                db,
                title="Moderation Rejected 1",
                submitter=submitter,
                admin=reviewer,
                status="rejected",
                admin_note="Ablehnung: Zutatenliste unvollstaendig.",
            )
            if created_rejected:
                moderation_fixtures_created += 1
            _, created_approved = ensure_submission_fixture(
                db,
                title="Moderation Approved 1",
                submitter=submitter,
                admin=reviewer,
                status="approved",
                admin_note="Freigabe: Inhalt geprueft.",
            )
            if created_approved:
                moderation_fixtures_created += 1

        db.commit()
        print("Seed abgeschlossen.")
        print(f"Passwort fuer alle neuen Test-Accounts: {TEST_PASSWORD}")
        print(f"Neue Benutzer/Admins: {users_created}")
        print(f"Aktualisierte Benutzer/Admins: {users_updated}")
        print(f"Neue Admin-Rezepte (published): {admin_recipes_created}")
        print(f"Neue Moderations-Fixtures: {moderation_fixtures_created}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_test_data()
```
ZEILEN-ERKL?RUNG
1. Diese Zeile definiert den Inhalt 'import os'.
2. Diese Zeile definiert den Inhalt 'import sys'.
3. Diese Zeile definiert den Inhalt 'from datetime import datetime, timezone'.
4. Diese Zeile definiert den Inhalt 'from pathlib import Path'.
5. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
6. Diese Zeile definiert den Inhalt 'from sqlalchemy import select'.
7. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
8. Diese Zeile definiert den Inhalt 'sys.path.append(str(Path(__file__).resolve().parents[1]))'.
9. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
10. Diese Zeile definiert den Inhalt 'from app.config import get_settings'.
11. Diese Zeile definiert den Inhalt 'from app.database import SessionLocal'.
12. Diese Zeile definiert den Inhalt 'from app.models import Recipe, RecipeSubmission, User'.
13. Diese Zeile definiert den Inhalt 'from app.security import hash_password'.
14. Diese Zeile definiert den Inhalt 'from app.services import normalize_category, publish_submission_as_recipe, sanitize_dif...'.
15. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
16. Diese Zeile definiert den Inhalt 'TEST_PASSWORD = "TestPass123!"'.
17. Diese Zeile definiert den Inhalt 'USER_COUNT = 15'.
18. Diese Zeile definiert den Inhalt 'ADMIN_COUNT = 3'.
19. Diese Zeile definiert den Inhalt 'RECIPES_PER_ADMIN = 3'.
20. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
21. Diese Zeile definiert den Inhalt 'CATEGORIES = ['.
22. Diese Zeile definiert den Inhalt '"Pasta",'.
23. Diese Zeile definiert den Inhalt '"Salat",'.
24. Diese Zeile definiert den Inhalt '"Suppe",'.
25. Diese Zeile definiert den Inhalt '"Dessert",'.
26. Diese Zeile definiert den Inhalt '"Fruehstueck",'.
27. Diese Zeile definiert den Inhalt '"Vegetarisch",'.
28. Diese Zeile definiert den Inhalt ']'.
29. Diese Zeile definiert den Inhalt 'DIFFICULTIES = ["easy", "medium", "hard"]'.
30. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
31. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
32. Diese Zeile definiert den Inhalt 'def allow_moderation_fixtures() -> bool:'.
33. Diese Zeile definiert den Inhalt 'settings = get_settings()'.
34. Diese Zeile definiert den Inhalt 'return settings.app_env == "dev" or os.getenv("TESTING") == "1"'.
35. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
36. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
37. Diese Zeile definiert den Inhalt 'def ensure_user(db, email: str, role: str) -> tuple[User, str]:'.
38. Diese Zeile definiert den Inhalt 'existing = db.scalar(select(User).where(User.email == email))'.
39. Diese Zeile definiert den Inhalt 'if existing:'.
40. Diese Zeile definiert den Inhalt 'changed = False'.
41. Diese Zeile definiert den Inhalt 'if existing.role != role:'.
42. Diese Zeile definiert den Inhalt 'existing.role = role'.
43. Diese Zeile definiert den Inhalt 'changed = True'.
44. Diese Zeile definiert den Inhalt 'if not existing.hashed_password:'.
45. Diese Zeile definiert den Inhalt 'existing.hashed_password = hash_password(TEST_PASSWORD)'.
46. Diese Zeile definiert den Inhalt 'changed = True'.
47. Diese Zeile definiert den Inhalt 'return existing, "updated" if changed else "unchanged"'.
48. Diese Zeile definiert den Inhalt 'user = User(email=email, hashed_password=hash_password(TEST_PASSWORD), role=role)'.
49. Diese Zeile definiert den Inhalt 'db.add(user)'.
50. Diese Zeile definiert den Inhalt 'db.flush()'.
51. Diese Zeile definiert den Inhalt 'return user, "created"'.
52. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
53. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
54. Diese Zeile definiert den Inhalt 'def ensure_admin_recipe(db, owner: User, owner_index: int, recipe_index: int) -> bool:'.
55. Diese Zeile definiert den Inhalt 'source_uuid = f"test-seed:admin:{owner_index:02d}:recipe:{recipe_index}"'.
56. Diese Zeile definiert den Inhalt 'existing = db.scalar(select(Recipe).where(Recipe.source_uuid == source_uuid))'.
57. Diese Zeile definiert den Inhalt 'if existing:'.
58. Diese Zeile definiert den Inhalt 'return False'.
59. Diese Zeile definiert den Inhalt 'category = normalize_category(CATEGORIES[(owner_index + recipe_index) % len(CATEGORIES)])'.
60. Diese Zeile definiert den Inhalt 'difficulty = sanitize_difficulty(DIFFICULTIES[(owner_index + recipe_index - 1) % len(DI...'.
61. Diese Zeile definiert den Inhalt 'db.add('.
62. Diese Zeile definiert den Inhalt 'Recipe('.
63. Diese Zeile definiert den Inhalt 'title=f"Testrezept ADMIN {owner_index:02d}-{recipe_index}",'.
64. Diese Zeile definiert den Inhalt 'title_image_url=f"https://picsum.photos/seed/admin{owner_index:02d}{recipe_index}/640/3...'.
65. Diese Zeile definiert den Inhalt 'description="Automatisch erzeugtes Admin-Testrezept fuer UI- und Workflow-Tests.",'.
66. Diese Zeile definiert den Inhalt 'instructions=('.
67. Diese Zeile definiert den Inhalt '"1. Zutaten vorbereiten.\n"'.
68. Diese Zeile definiert den Inhalt '"2. Alles nach Rezeptschritten kombinieren.\n"'.
69. Diese Zeile definiert den Inhalt '"3. Abschmecken und servieren."'.
70. Diese Zeile definiert den Inhalt '),'.
71. Diese Zeile definiert den Inhalt 'category=category,'.
72. Diese Zeile definiert den Inhalt 'prep_time_minutes=15 + recipe_index * 10,'.
73. Diese Zeile definiert den Inhalt 'difficulty=difficulty,'.
74. Diese Zeile definiert den Inhalt 'creator_id=owner.id,'.
75. Diese Zeile definiert den Inhalt 'source="test_seed",'.
76. Diese Zeile definiert den Inhalt 'source_uuid=source_uuid,'.
77. Diese Zeile definiert den Inhalt 'is_published=True,'.
78. Diese Zeile definiert den Inhalt ')'.
79. Diese Zeile definiert den Inhalt ')'.
80. Diese Zeile definiert den Inhalt 'return True'.
81. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
82. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
83. Diese Zeile definiert den Inhalt 'def ensure_submission_fixture('.
84. Diese Zeile definiert den Inhalt 'db,'.
85. Diese Zeile definiert den Inhalt '*,'.
86. Diese Zeile definiert den Inhalt 'title: str,'.
87. Diese Zeile definiert den Inhalt 'submitter: User,'.
88. Diese Zeile definiert den Inhalt 'admin: User,'.
89. Diese Zeile definiert den Inhalt 'status: str,'.
90. Diese Zeile definiert den Inhalt 'admin_note: str | None = None,'.
91. Diese Zeile definiert den Inhalt ') -> tuple[RecipeSubmission, bool]:'.
92. Diese Zeile definiert den Inhalt 'submission = db.scalar(select(RecipeSubmission).where(RecipeSubmission.title == title))'.
93. Diese Zeile definiert den Inhalt 'created = False'.
94. Diese Zeile definiert den Inhalt 'if not submission:'.
95. Diese Zeile definiert den Inhalt 'submission = RecipeSubmission('.
96. Diese Zeile definiert den Inhalt 'submitter_user_id=submitter.id,'.
97. Diese Zeile definiert den Inhalt 'submitter_email=None,'.
98. Diese Zeile definiert den Inhalt 'title=title,'.
99. Diese Zeile definiert den Inhalt 'description="Gezielte Moderations-Testeinreichung.",'.
100. Diese Zeile definiert den Inhalt 'category=normalize_category("Test Kategorie"),'.
101. Diese Zeile definiert den Inhalt 'difficulty="medium",'.
102. Diese Zeile definiert den Inhalt 'prep_time_minutes=25,'.
103. Diese Zeile definiert den Inhalt 'servings_text="2 Portionen",'.
104. Diese Zeile definiert den Inhalt 'instructions="1. Testeinreichung vorbereiten.\n2. Speichern und Moderation pruefen.",'.
105. Diese Zeile definiert den Inhalt 'status="pending",'.
106. Diese Zeile definiert den Inhalt ')'.
107. Diese Zeile definiert den Inhalt 'db.add(submission)'.
108. Diese Zeile definiert den Inhalt 'db.flush()'.
109. Diese Zeile definiert den Inhalt 'created = True'.
110. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
111. Diese Zeile definiert den Inhalt 'if status == "pending":'.
112. Diese Zeile definiert den Inhalt 'if submission.status != "pending":'.
113. Diese Zeile definiert den Inhalt 'submission.status = "pending"'.
114. Diese Zeile definiert den Inhalt 'submission.admin_note = None'.
115. Diese Zeile definiert den Inhalt 'submission.reviewed_by_admin_id = None'.
116. Diese Zeile definiert den Inhalt 'submission.reviewed_at = None'.
117. Diese Zeile definiert den Inhalt 'return submission, created'.
118. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
119. Diese Zeile definiert den Inhalt 'if status == "rejected":'.
120. Diese Zeile definiert den Inhalt 'submission.status = "rejected"'.
121. Diese Zeile definiert den Inhalt 'submission.admin_note = admin_note or "Nicht ausreichend beschrieben."'.
122. Diese Zeile definiert den Inhalt 'submission.reviewed_by_admin_id = admin.id'.
123. Diese Zeile definiert den Inhalt 'submission.reviewed_at = datetime.now(timezone.utc)'.
124. Diese Zeile definiert den Inhalt 'return submission, created'.
125. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
126. Diese Zeile definiert den Inhalt 'if status == "approved":'.
127. Diese Zeile definiert den Inhalt 'recipe = db.scalar(select(Recipe).where(Recipe.source_uuid == f"submission:{submission....'.
128. Diese Zeile definiert den Inhalt 'if recipe is None:'.
129. Diese Zeile definiert den Inhalt 'publish_submission_as_recipe(db, submission, admin.id)'.
130. Diese Zeile definiert den Inhalt 'submission.status = "approved"'.
131. Diese Zeile definiert den Inhalt 'submission.admin_note = admin_note or "Freigegeben fuer Discover."'.
132. Diese Zeile definiert den Inhalt 'submission.reviewed_by_admin_id = admin.id'.
133. Diese Zeile definiert den Inhalt 'submission.reviewed_at = datetime.now(timezone.utc)'.
134. Diese Zeile definiert den Inhalt 'return submission, created'.
135. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
136. Diese Zeile definiert den Inhalt 'raise ValueError(f"Unknown status: {status}")'.
137. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
138. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
139. Diese Zeile definiert den Inhalt 'def seed_test_data() -> None:'.
140. Diese Zeile definiert den Inhalt 'db = SessionLocal()'.
141. Diese Zeile definiert den Inhalt 'try:'.
142. Diese Zeile definiert den Inhalt 'users_created = 0'.
143. Diese Zeile definiert den Inhalt 'users_updated = 0'.
144. Diese Zeile definiert den Inhalt 'admin_recipes_created = 0'.
145. Diese Zeile definiert den Inhalt 'moderation_fixtures_created = 0'.
146. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
147. Diese Zeile definiert den Inhalt 'test_users: list[User] = []'.
148. Diese Zeile definiert den Inhalt 'test_admins: list[User] = []'.
149. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
150. Diese Zeile definiert den Inhalt 'for index in range(1, USER_COUNT + 1):'.
151. Diese Zeile definiert den Inhalt 'email = f"test.user{index:02d}@mealmate.local"'.
152. Diese Zeile definiert den Inhalt 'user, state = ensure_user(db, email, "user")'.
153. Diese Zeile definiert den Inhalt 'test_users.append(user)'.
154. Diese Zeile definiert den Inhalt 'if state == "created":'.
155. Diese Zeile definiert den Inhalt 'users_created += 1'.
156. Diese Zeile definiert den Inhalt 'elif state == "updated":'.
157. Diese Zeile definiert den Inhalt 'users_updated += 1'.
158. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
159. Diese Zeile definiert den Inhalt 'for index in range(1, ADMIN_COUNT + 1):'.
160. Diese Zeile definiert den Inhalt 'email = f"test.admin{index:02d}@mealmate.local"'.
161. Diese Zeile definiert den Inhalt 'admin, state = ensure_user(db, email, "admin")'.
162. Diese Zeile definiert den Inhalt 'test_admins.append(admin)'.
163. Diese Zeile definiert den Inhalt 'if state == "created":'.
164. Diese Zeile definiert den Inhalt 'users_created += 1'.
165. Diese Zeile definiert den Inhalt 'elif state == "updated":'.
166. Diese Zeile definiert den Inhalt 'users_updated += 1'.
167. Diese Zeile definiert den Inhalt 'for recipe_index in range(1, RECIPES_PER_ADMIN + 1):'.
168. Diese Zeile definiert den Inhalt 'if ensure_admin_recipe(db, admin, index, recipe_index):'.
169. Diese Zeile definiert den Inhalt 'admin_recipes_created += 1'.
170. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
171. Diese Zeile definiert den Inhalt 'if allow_moderation_fixtures() and test_users and test_admins:'.
172. Diese Zeile definiert den Inhalt 'submitter = test_users[0]'.
173. Diese Zeile definiert den Inhalt 'reviewer = test_admins[0]'.
174. Diese Zeile definiert den Inhalt 'for idx in range(1, 4):'.
175. Diese Zeile definiert den Inhalt '_, created = ensure_submission_fixture('.
176. Diese Zeile definiert den Inhalt 'db,'.
177. Diese Zeile definiert den Inhalt 'title=f"Moderation Pending {idx}",'.
178. Diese Zeile definiert den Inhalt 'submitter=submitter,'.
179. Diese Zeile definiert den Inhalt 'admin=reviewer,'.
180. Diese Zeile definiert den Inhalt 'status="pending",'.
181. Diese Zeile definiert den Inhalt ')'.
182. Diese Zeile definiert den Inhalt 'if created:'.
183. Diese Zeile definiert den Inhalt 'moderation_fixtures_created += 1'.
184. Diese Zeile definiert den Inhalt '_, created_rejected = ensure_submission_fixture('.
185. Diese Zeile definiert den Inhalt 'db,'.
186. Diese Zeile definiert den Inhalt 'title="Moderation Rejected 1",'.
187. Diese Zeile definiert den Inhalt 'submitter=submitter,'.
188. Diese Zeile definiert den Inhalt 'admin=reviewer,'.
189. Diese Zeile definiert den Inhalt 'status="rejected",'.
190. Diese Zeile definiert den Inhalt 'admin_note="Ablehnung: Zutatenliste unvollstaendig.",'.
191. Diese Zeile definiert den Inhalt ')'.
192. Diese Zeile definiert den Inhalt 'if created_rejected:'.
193. Diese Zeile definiert den Inhalt 'moderation_fixtures_created += 1'.
194. Diese Zeile definiert den Inhalt '_, created_approved = ensure_submission_fixture('.
195. Diese Zeile definiert den Inhalt 'db,'.
196. Diese Zeile definiert den Inhalt 'title="Moderation Approved 1",'.
197. Diese Zeile definiert den Inhalt 'submitter=submitter,'.
198. Diese Zeile definiert den Inhalt 'admin=reviewer,'.
199. Diese Zeile definiert den Inhalt 'status="approved",'.
200. Diese Zeile definiert den Inhalt 'admin_note="Freigabe: Inhalt geprueft.",'.
201. Diese Zeile definiert den Inhalt ')'.
202. Diese Zeile definiert den Inhalt 'if created_approved:'.
203. Diese Zeile definiert den Inhalt 'moderation_fixtures_created += 1'.
204. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
205. Diese Zeile definiert den Inhalt 'db.commit()'.
206. Diese Zeile definiert den Inhalt 'print("Seed abgeschlossen.")'.
207. Diese Zeile definiert den Inhalt 'print(f"Passwort fuer alle neuen Test-Accounts: {TEST_PASSWORD}")'.
208. Diese Zeile definiert den Inhalt 'print(f"Neue Benutzer/Admins: {users_created}")'.
209. Diese Zeile definiert den Inhalt 'print(f"Aktualisierte Benutzer/Admins: {users_updated}")'.
210. Diese Zeile definiert den Inhalt 'print(f"Neue Admin-Rezepte (published): {admin_recipes_created}")'.
211. Diese Zeile definiert den Inhalt 'print(f"Neue Moderations-Fixtures: {moderation_fixtures_created}")'.
212. Diese Zeile definiert den Inhalt 'finally:'.
213. Diese Zeile definiert den Inhalt 'db.close()'.
214. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
215. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
216. Diese Zeile definiert den Inhalt 'if __name__ == "__main__":'.
217. Diese Zeile definiert den Inhalt 'seed_test_data()'.

## requirements.txt
```text
fastapi==0.116.1
uvicorn[standard]==0.35.0
gunicorn==23.0.0
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
slowapi==0.1.9
httpx==0.28.1
pytest==8.4.2
```
ZEILEN-ERKL?RUNG
1. Diese Zeile definiert den Inhalt 'fastapi==0.116.1'.
2. Diese Zeile definiert den Inhalt 'uvicorn[standard]==0.35.0'.
3. Diese Zeile definiert den Inhalt 'gunicorn==23.0.0'.
4. Diese Zeile definiert den Inhalt 'jinja2==3.1.6'.
5. Diese Zeile definiert den Inhalt 'sqlalchemy==2.0.43'.
6. Diese Zeile definiert den Inhalt 'alembic==1.16.5'.
7. Diese Zeile definiert den Inhalt 'python-jose[cryptography]==3.5.0'.
8. Diese Zeile definiert den Inhalt 'pwdlib==0.2.1'.
9. Diese Zeile definiert den Inhalt 'argon2-cffi==25.1.0'.
10. Diese Zeile definiert den Inhalt 'python-multipart==0.0.20'.
11. Diese Zeile definiert den Inhalt 'pydantic-settings==2.10.1'.
12. Diese Zeile definiert den Inhalt 'reportlab==4.4.4'.
13. Diese Zeile definiert den Inhalt 'pillow==11.3.0'.
14. Diese Zeile definiert den Inhalt 'psycopg[binary]==3.2.13'.
15. Diese Zeile definiert den Inhalt 'slowapi==0.1.9'.
16. Diese Zeile definiert den Inhalt 'httpx==0.28.1'.
17. Diese Zeile definiert den Inhalt 'pytest==8.4.2'.

## tests/conftest.py
```python
from pathlib import Path
import sys

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from app import models  # noqa: F401
from app.database import Base, get_db
from app.main import app


@pytest.fixture()
def db_session_factory(tmp_path):
    database_path = tmp_path / "test_mealmate.db"
    engine = create_engine(
        f"sqlite:///{database_path}",
        connect_args={"check_same_thread": False},
    )
    TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    Base.metadata.create_all(bind=engine)
    try:
        yield TestingSessionLocal
    finally:
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture()
def client(db_session_factory):
    def override_get_db():
        db = db_session_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
```
ZEILEN-ERKL?RUNG
1. Diese Zeile definiert den Inhalt 'from pathlib import Path'.
2. Diese Zeile definiert den Inhalt 'import sys'.
3. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
4. Diese Zeile definiert den Inhalt 'import pytest'.
5. Diese Zeile definiert den Inhalt 'from fastapi.testclient import TestClient'.
6. Diese Zeile definiert den Inhalt 'from sqlalchemy import create_engine'.
7. Diese Zeile definiert den Inhalt 'from sqlalchemy.orm import sessionmaker'.
8. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
9. Diese Zeile definiert den Inhalt 'PROJECT_ROOT = Path(__file__).resolve().parents[1]'.
10. Diese Zeile definiert den Inhalt 'if str(PROJECT_ROOT) not in sys.path:'.
11. Diese Zeile definiert den Inhalt 'sys.path.append(str(PROJECT_ROOT))'.
12. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
13. Diese Zeile definiert den Inhalt 'from app import models  # noqa: F401'.
14. Diese Zeile definiert den Inhalt 'from app.database import Base, get_db'.
15. Diese Zeile definiert den Inhalt 'from app.main import app'.
16. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
17. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
18. Diese Zeile definiert den Inhalt '@pytest.fixture()'.
19. Diese Zeile definiert den Inhalt 'def db_session_factory(tmp_path):'.
20. Diese Zeile definiert den Inhalt 'database_path = tmp_path / "test_mealmate.db"'.
21. Diese Zeile definiert den Inhalt 'engine = create_engine('.
22. Diese Zeile definiert den Inhalt 'f"sqlite:///{database_path}",'.
23. Diese Zeile definiert den Inhalt 'connect_args={"check_same_thread": False},'.
24. Diese Zeile definiert den Inhalt ')'.
25. Diese Zeile definiert den Inhalt 'TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)'.
26. Diese Zeile definiert den Inhalt 'Base.metadata.create_all(bind=engine)'.
27. Diese Zeile definiert den Inhalt 'try:'.
28. Diese Zeile definiert den Inhalt 'yield TestingSessionLocal'.
29. Diese Zeile definiert den Inhalt 'finally:'.
30. Diese Zeile definiert den Inhalt 'Base.metadata.drop_all(bind=engine)'.
31. Diese Zeile definiert den Inhalt 'engine.dispose()'.
32. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
33. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
34. Diese Zeile definiert den Inhalt '@pytest.fixture()'.
35. Diese Zeile definiert den Inhalt 'def client(db_session_factory):'.
36. Diese Zeile definiert den Inhalt 'def override_get_db():'.
37. Diese Zeile definiert den Inhalt 'db = db_session_factory()'.
38. Diese Zeile definiert den Inhalt 'try:'.
39. Diese Zeile definiert den Inhalt 'yield db'.
40. Diese Zeile definiert den Inhalt 'finally:'.
41. Diese Zeile definiert den Inhalt 'db.close()'.
42. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
43. Diese Zeile definiert den Inhalt 'app.dependency_overrides[get_db] = override_get_db'.
44. Diese Zeile definiert den Inhalt 'with TestClient(app) as test_client:'.
45. Diese Zeile definiert den Inhalt 'yield test_client'.
46. Diese Zeile definiert den Inhalt 'app.dependency_overrides.clear()'.

## tests/test_moderation_workflow.py
```python
from datetime import datetime, timezone

from sqlalchemy import select

from app.moderation_repair import run_moderation_repair
from app.models import Recipe, RecipeSubmission, User
from app.security import create_access_token, hash_password


def create_user(db, email: str, role: str) -> tuple[int, str, str]:
    user = User(email=email, hashed_password=hash_password("StrongTestPass123!"), role=role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user.id, user.email, user.role


def auth_client(client, email: str, role: str) -> str:
    token = create_access_token(email, role)
    csrf_token = "test-csrf-token"
    client.cookies.set("access_token", f"Bearer {token}")
    client.cookies.set("csrf_token", csrf_token)
    return csrf_token


def test_user_submit_goes_to_pending_not_discover(client, db_session_factory):
    with db_session_factory() as db:
        _, user_email, user_role = create_user(db, "submitter@example.local", "user")
    csrf = auth_client(client, user_email, user_role)

    response = client.post(
        "/submit",
        data={
            "title": "Pending Rezept Alpha",
            "description": "Nur zur Moderation.",
            "instructions": "Testschritt 1\nTestschritt 2",
            "difficulty": "medium",
            "category_select": "Unkategorisiert",
        },
        headers={"X-CSRF-Token": csrf},
        follow_redirects=False,
    )
    assert response.status_code == 303

    with db_session_factory() as db:
        submission = db.scalar(select(RecipeSubmission).where(RecipeSubmission.title == "Pending Rezept Alpha"))
        assert submission is not None
        assert submission.status == "pending"
        recipe = db.scalar(select(Recipe).where(Recipe.title == "Pending Rezept Alpha"))
        assert recipe is None

    discover = client.get("/")
    assert discover.status_code == 200
    assert "Pending Rezept Alpha" not in discover.text


def test_user_cannot_publish_recipe_directly(client, db_session_factory):
    with db_session_factory() as db:
        _, user_email, user_role = create_user(db, "publisher-denied@example.local", "user")
    csrf = auth_client(client, user_email, user_role)

    response = client.post(
        "/recipes",
        data={
            "title": "Direkt Publizieren Verboten",
            "description": "Darf nicht live gehen.",
            "instructions": "Keine direkte Freigabe.",
            "category_select": "Unkategorisiert",
            "category_new": "",
            "category": "",
            "title_image_url": "",
            "prep_time_minutes": "20",
            "difficulty": "easy",
            "ingredients_text": "",
        },
        headers={"X-CSRF-Token": csrf},
        follow_redirects=False,
    )
    assert response.status_code == 403


def test_admin_can_approve_submission_and_then_it_appears(client, db_session_factory):
    with db_session_factory() as db:
        _, admin_email, admin_role = create_user(db, "moderator@example.local", "admin")
        _, user_email, user_role = create_user(db, "user-for-approval@example.local", "user")
    user_csrf = auth_client(client, user_email, user_role)

    submit_response = client.post(
        "/submit",
        data={
            "title": "Freigabe Kandidat",
            "description": "Wird nach Freigabe sichtbar.",
            "instructions": "Schritt A\nSchritt B",
            "difficulty": "easy",
            "category_select": "Unkategorisiert",
        },
        headers={"X-CSRF-Token": user_csrf},
        follow_redirects=False,
    )
    assert submit_response.status_code == 303

    with db_session_factory() as db:
        submission = db.scalar(select(RecipeSubmission).where(RecipeSubmission.title == "Freigabe Kandidat"))
        assert submission is not None
        submission_id = submission.id
        assert submission.status == "pending"

    admin_csrf = auth_client(client, admin_email, admin_role)
    approve_response = client.post(
        f"/admin/submissions/{submission_id}/approve",
        data={"admin_note": "Freigegeben im Test."},
        headers={"X-CSRF-Token": admin_csrf},
        follow_redirects=False,
    )
    assert approve_response.status_code == 303

    with db_session_factory() as db:
        approved_submission = db.scalar(select(RecipeSubmission).where(RecipeSubmission.id == submission_id))
        assert approved_submission is not None
        assert approved_submission.status == "approved"
        recipe = db.scalar(select(Recipe).where(Recipe.source_uuid == f"submission:{submission_id}"))
        assert recipe is not None
        assert recipe.is_published is True

    discover = client.get("/")
    assert discover.status_code == 200
    assert "Freigabe Kandidat" in discover.text


def test_repair_script_marks_non_admin_recipes_unpublished(db_session_factory):
    with db_session_factory() as db:
        user_id, _, _ = create_user(db, "legacy-user@example.local", "user")
        _ = create_user(db, "legacy-admin@example.local", "admin")
        legacy_recipe = Recipe(
            title="Legacy Direkt Veroeffentlicht",
            description="War faelschlich live.",
            instructions="Legacy Schritte",
            category="Legacy",
            prep_time_minutes=30,
            difficulty="medium",
            creator_id=user_id,
            source="user",
            source_uuid="legacy-direct-001",
            is_published=True,
        )
        db.add(legacy_recipe)
        db.commit()
        db.refresh(legacy_recipe)
        legacy_recipe_id = legacy_recipe.id

        dry_report = run_moderation_repair(db, dry_run=True)
        assert dry_report.affected_count == 1
        assert dry_report.moved_to_pending_count == 0
        db.rollback()

        apply_report = run_moderation_repair(db, dry_run=False)
        assert apply_report.affected_count == 1
        assert apply_report.moved_to_pending_count == 1
        db.commit()

    with db_session_factory() as db:
        repaired_recipe = db.scalar(select(Recipe).where(Recipe.id == legacy_recipe_id))
        assert repaired_recipe is not None
        assert repaired_recipe.is_published is False
        pending_submission = db.scalar(
            select(RecipeSubmission).where(
                RecipeSubmission.title == "Legacy Direkt Veroeffentlicht",
                RecipeSubmission.status == "pending",
            )
        )
        assert pending_submission is not None
        assert pending_submission.submitter_user_id is not None
```
ZEILEN-ERKL?RUNG
1. Diese Zeile definiert den Inhalt 'from datetime import datetime, timezone'.
2. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
3. Diese Zeile definiert den Inhalt 'from sqlalchemy import select'.
4. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
5. Diese Zeile definiert den Inhalt 'from app.moderation_repair import run_moderation_repair'.
6. Diese Zeile definiert den Inhalt 'from app.models import Recipe, RecipeSubmission, User'.
7. Diese Zeile definiert den Inhalt 'from app.security import create_access_token, hash_password'.
8. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
9. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
10. Diese Zeile definiert den Inhalt 'def create_user(db, email: str, role: str) -> tuple[int, str, str]:'.
11. Diese Zeile definiert den Inhalt 'user = User(email=email, hashed_password=hash_password("StrongTestPass123!"), role=role)'.
12. Diese Zeile definiert den Inhalt 'db.add(user)'.
13. Diese Zeile definiert den Inhalt 'db.commit()'.
14. Diese Zeile definiert den Inhalt 'db.refresh(user)'.
15. Diese Zeile definiert den Inhalt 'return user.id, user.email, user.role'.
16. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
17. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
18. Diese Zeile definiert den Inhalt 'def auth_client(client, email: str, role: str) -> str:'.
19. Diese Zeile definiert den Inhalt 'token = create_access_token(email, role)'.
20. Diese Zeile definiert den Inhalt 'csrf_token = "test-csrf-token"'.
21. Diese Zeile definiert den Inhalt 'client.cookies.set("access_token", f"Bearer {token}")'.
22. Diese Zeile definiert den Inhalt 'client.cookies.set("csrf_token", csrf_token)'.
23. Diese Zeile definiert den Inhalt 'return csrf_token'.
24. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
25. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
26. Diese Zeile definiert den Inhalt 'def test_user_submit_goes_to_pending_not_discover(client, db_session_factory):'.
27. Diese Zeile definiert den Inhalt 'with db_session_factory() as db:'.
28. Diese Zeile definiert den Inhalt '_, user_email, user_role = create_user(db, "submitter@example.local", "user")'.
29. Diese Zeile definiert den Inhalt 'csrf = auth_client(client, user_email, user_role)'.
30. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
31. Diese Zeile definiert den Inhalt 'response = client.post('.
32. Diese Zeile definiert den Inhalt '"/submit",'.
33. Diese Zeile definiert den Inhalt 'data={'.
34. Diese Zeile definiert den Inhalt '"title": "Pending Rezept Alpha",'.
35. Diese Zeile definiert den Inhalt '"description": "Nur zur Moderation.",'.
36. Diese Zeile definiert den Inhalt '"instructions": "Testschritt 1\nTestschritt 2",'.
37. Diese Zeile definiert den Inhalt '"difficulty": "medium",'.
38. Diese Zeile definiert den Inhalt '"category_select": "Unkategorisiert",'.
39. Diese Zeile definiert den Inhalt '},'.
40. Diese Zeile definiert den Inhalt 'headers={"X-CSRF-Token": csrf},'.
41. Diese Zeile definiert den Inhalt 'follow_redirects=False,'.
42. Diese Zeile definiert den Inhalt ')'.
43. Diese Zeile definiert den Inhalt 'assert response.status_code == 303'.
44. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
45. Diese Zeile definiert den Inhalt 'with db_session_factory() as db:'.
46. Diese Zeile definiert den Inhalt 'submission = db.scalar(select(RecipeSubmission).where(RecipeSubmission.title == "Pendin...'.
47. Diese Zeile definiert den Inhalt 'assert submission is not None'.
48. Diese Zeile definiert den Inhalt 'assert submission.status == "pending"'.
49. Diese Zeile definiert den Inhalt 'recipe = db.scalar(select(Recipe).where(Recipe.title == "Pending Rezept Alpha"))'.
50. Diese Zeile definiert den Inhalt 'assert recipe is None'.
51. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
52. Diese Zeile definiert den Inhalt 'discover = client.get("/")'.
53. Diese Zeile definiert den Inhalt 'assert discover.status_code == 200'.
54. Diese Zeile definiert den Inhalt 'assert "Pending Rezept Alpha" not in discover.text'.
55. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
56. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
57. Diese Zeile definiert den Inhalt 'def test_user_cannot_publish_recipe_directly(client, db_session_factory):'.
58. Diese Zeile definiert den Inhalt 'with db_session_factory() as db:'.
59. Diese Zeile definiert den Inhalt '_, user_email, user_role = create_user(db, "publisher-denied@example.local", "user")'.
60. Diese Zeile definiert den Inhalt 'csrf = auth_client(client, user_email, user_role)'.
61. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
62. Diese Zeile definiert den Inhalt 'response = client.post('.
63. Diese Zeile definiert den Inhalt '"/recipes",'.
64. Diese Zeile definiert den Inhalt 'data={'.
65. Diese Zeile definiert den Inhalt '"title": "Direkt Publizieren Verboten",'.
66. Diese Zeile definiert den Inhalt '"description": "Darf nicht live gehen.",'.
67. Diese Zeile definiert den Inhalt '"instructions": "Keine direkte Freigabe.",'.
68. Diese Zeile definiert den Inhalt '"category_select": "Unkategorisiert",'.
69. Diese Zeile definiert den Inhalt '"category_new": "",'.
70. Diese Zeile definiert den Inhalt '"category": "",'.
71. Diese Zeile definiert den Inhalt '"title_image_url": "",'.
72. Diese Zeile definiert den Inhalt '"prep_time_minutes": "20",'.
73. Diese Zeile definiert den Inhalt '"difficulty": "easy",'.
74. Diese Zeile definiert den Inhalt '"ingredients_text": "",'.
75. Diese Zeile definiert den Inhalt '},'.
76. Diese Zeile definiert den Inhalt 'headers={"X-CSRF-Token": csrf},'.
77. Diese Zeile definiert den Inhalt 'follow_redirects=False,'.
78. Diese Zeile definiert den Inhalt ')'.
79. Diese Zeile definiert den Inhalt 'assert response.status_code == 403'.
80. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
81. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
82. Diese Zeile definiert den Inhalt 'def test_admin_can_approve_submission_and_then_it_appears(client, db_session_factory):'.
83. Diese Zeile definiert den Inhalt 'with db_session_factory() as db:'.
84. Diese Zeile definiert den Inhalt '_, admin_email, admin_role = create_user(db, "moderator@example.local", "admin")'.
85. Diese Zeile definiert den Inhalt '_, user_email, user_role = create_user(db, "user-for-approval@example.local", "user")'.
86. Diese Zeile definiert den Inhalt 'user_csrf = auth_client(client, user_email, user_role)'.
87. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
88. Diese Zeile definiert den Inhalt 'submit_response = client.post('.
89. Diese Zeile definiert den Inhalt '"/submit",'.
90. Diese Zeile definiert den Inhalt 'data={'.
91. Diese Zeile definiert den Inhalt '"title": "Freigabe Kandidat",'.
92. Diese Zeile definiert den Inhalt '"description": "Wird nach Freigabe sichtbar.",'.
93. Diese Zeile definiert den Inhalt '"instructions": "Schritt A\nSchritt B",'.
94. Diese Zeile definiert den Inhalt '"difficulty": "easy",'.
95. Diese Zeile definiert den Inhalt '"category_select": "Unkategorisiert",'.
96. Diese Zeile definiert den Inhalt '},'.
97. Diese Zeile definiert den Inhalt 'headers={"X-CSRF-Token": user_csrf},'.
98. Diese Zeile definiert den Inhalt 'follow_redirects=False,'.
99. Diese Zeile definiert den Inhalt ')'.
100. Diese Zeile definiert den Inhalt 'assert submit_response.status_code == 303'.
101. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
102. Diese Zeile definiert den Inhalt 'with db_session_factory() as db:'.
103. Diese Zeile definiert den Inhalt 'submission = db.scalar(select(RecipeSubmission).where(RecipeSubmission.title == "Freiga...'.
104. Diese Zeile definiert den Inhalt 'assert submission is not None'.
105. Diese Zeile definiert den Inhalt 'submission_id = submission.id'.
106. Diese Zeile definiert den Inhalt 'assert submission.status == "pending"'.
107. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
108. Diese Zeile definiert den Inhalt 'admin_csrf = auth_client(client, admin_email, admin_role)'.
109. Diese Zeile definiert den Inhalt 'approve_response = client.post('.
110. Diese Zeile definiert den Inhalt 'f"/admin/submissions/{submission_id}/approve",'.
111. Diese Zeile definiert den Inhalt 'data={"admin_note": "Freigegeben im Test."},'.
112. Diese Zeile definiert den Inhalt 'headers={"X-CSRF-Token": admin_csrf},'.
113. Diese Zeile definiert den Inhalt 'follow_redirects=False,'.
114. Diese Zeile definiert den Inhalt ')'.
115. Diese Zeile definiert den Inhalt 'assert approve_response.status_code == 303'.
116. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
117. Diese Zeile definiert den Inhalt 'with db_session_factory() as db:'.
118. Diese Zeile definiert den Inhalt 'approved_submission = db.scalar(select(RecipeSubmission).where(RecipeSubmission.id == s...'.
119. Diese Zeile definiert den Inhalt 'assert approved_submission is not None'.
120. Diese Zeile definiert den Inhalt 'assert approved_submission.status == "approved"'.
121. Diese Zeile definiert den Inhalt 'recipe = db.scalar(select(Recipe).where(Recipe.source_uuid == f"submission:{submission_...'.
122. Diese Zeile definiert den Inhalt 'assert recipe is not None'.
123. Diese Zeile definiert den Inhalt 'assert recipe.is_published is True'.
124. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
125. Diese Zeile definiert den Inhalt 'discover = client.get("/")'.
126. Diese Zeile definiert den Inhalt 'assert discover.status_code == 200'.
127. Diese Zeile definiert den Inhalt 'assert "Freigabe Kandidat" in discover.text'.
128. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
129. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
130. Diese Zeile definiert den Inhalt 'def test_repair_script_marks_non_admin_recipes_unpublished(db_session_factory):'.
131. Diese Zeile definiert den Inhalt 'with db_session_factory() as db:'.
132. Diese Zeile definiert den Inhalt 'user_id, _, _ = create_user(db, "legacy-user@example.local", "user")'.
133. Diese Zeile definiert den Inhalt '_ = create_user(db, "legacy-admin@example.local", "admin")'.
134. Diese Zeile definiert den Inhalt 'legacy_recipe = Recipe('.
135. Diese Zeile definiert den Inhalt 'title="Legacy Direkt Veroeffentlicht",'.
136. Diese Zeile definiert den Inhalt 'description="War faelschlich live.",'.
137. Diese Zeile definiert den Inhalt 'instructions="Legacy Schritte",'.
138. Diese Zeile definiert den Inhalt 'category="Legacy",'.
139. Diese Zeile definiert den Inhalt 'prep_time_minutes=30,'.
140. Diese Zeile definiert den Inhalt 'difficulty="medium",'.
141. Diese Zeile definiert den Inhalt 'creator_id=user_id,'.
142. Diese Zeile definiert den Inhalt 'source="user",'.
143. Diese Zeile definiert den Inhalt 'source_uuid="legacy-direct-001",'.
144. Diese Zeile definiert den Inhalt 'is_published=True,'.
145. Diese Zeile definiert den Inhalt ')'.
146. Diese Zeile definiert den Inhalt 'db.add(legacy_recipe)'.
147. Diese Zeile definiert den Inhalt 'db.commit()'.
148. Diese Zeile definiert den Inhalt 'db.refresh(legacy_recipe)'.
149. Diese Zeile definiert den Inhalt 'legacy_recipe_id = legacy_recipe.id'.
150. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
151. Diese Zeile definiert den Inhalt 'dry_report = run_moderation_repair(db, dry_run=True)'.
152. Diese Zeile definiert den Inhalt 'assert dry_report.affected_count == 1'.
153. Diese Zeile definiert den Inhalt 'assert dry_report.moved_to_pending_count == 0'.
154. Diese Zeile definiert den Inhalt 'db.rollback()'.
155. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
156. Diese Zeile definiert den Inhalt 'apply_report = run_moderation_repair(db, dry_run=False)'.
157. Diese Zeile definiert den Inhalt 'assert apply_report.affected_count == 1'.
158. Diese Zeile definiert den Inhalt 'assert apply_report.moved_to_pending_count == 1'.
159. Diese Zeile definiert den Inhalt 'db.commit()'.
160. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
161. Diese Zeile definiert den Inhalt 'with db_session_factory() as db:'.
162. Diese Zeile definiert den Inhalt 'repaired_recipe = db.scalar(select(Recipe).where(Recipe.id == legacy_recipe_id))'.
163. Diese Zeile definiert den Inhalt 'assert repaired_recipe is not None'.
164. Diese Zeile definiert den Inhalt 'assert repaired_recipe.is_published is False'.
165. Diese Zeile definiert den Inhalt 'pending_submission = db.scalar('.
166. Diese Zeile definiert den Inhalt 'select(RecipeSubmission).where('.
167. Diese Zeile definiert den Inhalt 'RecipeSubmission.title == "Legacy Direkt Veroeffentlicht",'.
168. Diese Zeile definiert den Inhalt 'RecipeSubmission.status == "pending",'.
169. Diese Zeile definiert den Inhalt ')'.
170. Diese Zeile definiert den Inhalt ')'.
171. Diese Zeile definiert den Inhalt 'assert pending_submission is not None'.
172. Diese Zeile definiert den Inhalt 'assert pending_submission.submitter_user_id is not None'.

## README_MODERATION.md
```markdown
# MealMate Moderations-Workflow

## Ziel

Rezepte werden nur durch Admins veroeffentlicht.
Normale User und Gaeste duerfen Rezepte nur einreichen.

## Kernregeln

- `recipes` ist die veroeffentlichte Sammlung.
- Sichtbarkeit in Discover:
  - nur `recipes.is_published = true`.
- Direktes Veroeffentlichen:
  - nur Admin ueber `/recipes/new` oder `POST /recipes`.
- Einreichung:
  - User/Gast ueber `GET/POST /submit`.
  - neue Einreichung landet immer als `recipe_submissions.status = pending`.

## Admin Moderation

- Queue: `GET /admin/submissions?status=pending|approved|rejected|all`
- Detail: `GET /admin/submissions/{id}`
- Bearbeiten: `POST /admin/submissions/{id}/edit`
- Freigeben: `POST /admin/submissions/{id}/approve`
  - erstellt ein neues veroeffentlichtes Rezept (`is_published=true`)
  - setzt Submission auf `approved`
- Ablehnen: `POST /admin/submissions/{id}/reject`
  - erfordert `admin_note`
  - setzt Submission auf `rejected`

## User-Ansicht

- Eigene Einreichungen: `GET /my-submissions`
- Zeigt Status (`pending`, `approved`, `rejected`) und `admin_note`.

## Moderation Repair (Bestandsdaten)

Falls frueher User-Rezepte versehentlich direkt live gegangen sind:

- Dry-Run:
  - `py scripts/moderation_repair.py`
- Anwenden:
  - `py scripts/moderation_repair.py --apply`

Was passiert beim Apply:

- findet veroeffentlichte Rezepte von Nicht-Admins (ausser `source=kochwiki`)
- erstellt eine `pending` Submission-Kopie
- setzt das Rezept auf `is_published=false`

So gehen keine Daten verloren und Discover zeigt nur sauber freigegebene Inhalte.
```
ZEILEN-ERKL?RUNG
1. Diese Zeile definiert den Inhalt '# MealMate Moderations-Workflow'.
2. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
3. Diese Zeile definiert den Inhalt '## Ziel'.
4. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
5. Diese Zeile definiert den Inhalt 'Rezepte werden nur durch Admins veroeffentlicht.'.
6. Diese Zeile definiert den Inhalt 'Normale User und Gaeste duerfen Rezepte nur einreichen.'.
7. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
8. Diese Zeile definiert den Inhalt '## Kernregeln'.
9. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
10. Diese Zeile definiert den Inhalt '- 'recipes' ist die veroeffentlichte Sammlung.'.
11. Diese Zeile definiert den Inhalt '- Sichtbarkeit in Discover:'.
12. Diese Zeile definiert den Inhalt '- nur 'recipes.is_published = true'.'.
13. Diese Zeile definiert den Inhalt '- Direktes Veroeffentlichen:'.
14. Diese Zeile definiert den Inhalt '- nur Admin ueber '/recipes/new' oder 'POST /recipes'.'.
15. Diese Zeile definiert den Inhalt '- Einreichung:'.
16. Diese Zeile definiert den Inhalt '- User/Gast ueber 'GET/POST /submit'.'.
17. Diese Zeile definiert den Inhalt '- neue Einreichung landet immer als 'recipe_submissions.status = pending'.'.
18. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
19. Diese Zeile definiert den Inhalt '## Admin Moderation'.
20. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
21. Diese Zeile definiert den Inhalt '- Queue: 'GET /admin/submissions?status=pending|approved|rejected|all''.
22. Diese Zeile definiert den Inhalt '- Detail: 'GET /admin/submissions/{id}''.
23. Diese Zeile definiert den Inhalt '- Bearbeiten: 'POST /admin/submissions/{id}/edit''.
24. Diese Zeile definiert den Inhalt '- Freigeben: 'POST /admin/submissions/{id}/approve''.
25. Diese Zeile definiert den Inhalt '- erstellt ein neues veroeffentlichtes Rezept ('is_published=true')'.
26. Diese Zeile definiert den Inhalt '- setzt Submission auf 'approved''.
27. Diese Zeile definiert den Inhalt '- Ablehnen: 'POST /admin/submissions/{id}/reject''.
28. Diese Zeile definiert den Inhalt '- erfordert 'admin_note''.
29. Diese Zeile definiert den Inhalt '- setzt Submission auf 'rejected''.
30. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
31. Diese Zeile definiert den Inhalt '## User-Ansicht'.
32. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
33. Diese Zeile definiert den Inhalt '- Eigene Einreichungen: 'GET /my-submissions''.
34. Diese Zeile definiert den Inhalt '- Zeigt Status ('pending', 'approved', 'rejected') und 'admin_note'.'.
35. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
36. Diese Zeile definiert den Inhalt '## Moderation Repair (Bestandsdaten)'.
37. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
38. Diese Zeile definiert den Inhalt 'Falls frueher User-Rezepte versehentlich direkt live gegangen sind:'.
39. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
40. Diese Zeile definiert den Inhalt '- Dry-Run:'.
41. Diese Zeile definiert den Inhalt '- 'py scripts/moderation_repair.py''.
42. Diese Zeile definiert den Inhalt '- Anwenden:'.
43. Diese Zeile definiert den Inhalt '- 'py scripts/moderation_repair.py --apply''.
44. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
45. Diese Zeile definiert den Inhalt 'Was passiert beim Apply:'.
46. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
47. Diese Zeile definiert den Inhalt '- findet veroeffentlichte Rezepte von Nicht-Admins (ausser 'source=kochwiki')'.
48. Diese Zeile definiert den Inhalt '- erstellt eine 'pending' Submission-Kopie'.
49. Diese Zeile definiert den Inhalt '- setzt das Rezept auf 'is_published=false''.
50. Diese Zeile ist leer und dient der Strukturierung des Dokuments.
51. Diese Zeile definiert den Inhalt 'So gehen keine Daten verloren und Discover zeigt nur sauber freigegebene Inhalte.'.
