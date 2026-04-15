# Moderations-Workflow Deliverable

## Betroffene Dateien
- `app/models.py`
- `alembic/versions/20260303_0005_recipe_submissions.py`
- `app/services.py`
- `app/i18n/__init__.py`
- `app/i18n/de.py`
- `app/views.py`
- `app/routers/submissions.py`
- `app/routers/__init__.py`
- `app/main.py`
- `app/templates/base.html`
- `app/templates/admin.html`
- `app/templates/submit_recipe.html`
- `app/templates/my_submissions.html`
- `app/templates/admin_submissions.html`
- `app/templates/admin_submission_detail.html`
- `app/static/style.css`

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
ZEILEN-ERKLAERUNG
1. Diese Zeile importiert gezielte Elemente aus einem anderen Modul.
2. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
3. Diese Zeile importiert gezielte Elemente aus einem anderen Modul.
4. Diese Zeile importiert gezielte Elemente aus einem anderen Modul.
5. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
6. Diese Zeile importiert gezielte Elemente aus einem anderen Modul.
7. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
8. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
9. Diese Zeile startet die Definition einer Funktion.
10. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
11. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
12. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
13. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
14. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
15. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
16. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
17. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
18. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
19. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
20. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
21. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
22. Diese Zeile startet die Definition einer Klasse.
23. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
24. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
25. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
26. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
27. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
28. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
29. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
30. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
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
43. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
44. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
45. Diese Zeile startet die Definition einer Klasse.
46. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
47. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
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
64. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
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
77. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
78. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
79. Diese Zeile startet die Definition einer Klasse.
80. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
81. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
82. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
83. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
84. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
85. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
86. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
87. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
88. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
89. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
90. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
91. Diese Zeile startet die Definition einer Klasse.
92. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
93. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
94. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
95. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
96. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
97. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
98. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
99. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
100. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
101. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
102. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
103. Diese Zeile startet die Definition einer Klasse.
104. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
105. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
106. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
107. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
108. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
109. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
110. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
111. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
112. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
113. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
114. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
115. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
116. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
117. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
118. Diese Zeile startet die Definition einer Klasse.
119. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
120. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
121. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
122. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
123. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
124. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
125. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
126. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
127. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
128. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
129. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
130. Diese Zeile startet die Definition einer Klasse.
131. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
132. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
133. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
134. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
135. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
136. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
137. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
138. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
139. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
140. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
141. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
142. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
143. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
144. Diese Zeile startet die Definition einer Klasse.
145. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
146. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
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
162. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
163. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
164. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
165. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
166. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
167. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
168. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
169. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
170. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
171. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
172. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
173. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
174. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
175. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
176. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
177. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
178. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
179. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
180. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
181. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
182. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
183. Diese Zeile startet die Definition einer Klasse.
184. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
185. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
186. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
187. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
188. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
189. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
190. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
191. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
192. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
193. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
194. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
195. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
196. Diese Zeile startet die Definition einer Klasse.
197. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
198. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
199. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
200. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
201. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
202. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
203. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
204. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
205. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
206. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
207. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
208. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
209. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
210. Diese Zeile startet die Definition einer Klasse.
211. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
212. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
213. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
214. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.

## alembic/versions/20260303_0005_recipe_submissions.py
```python
"""add recipe submissions moderation workflow tables

Revision ID: 20260303_0005
Revises: 20260303_0004
Create Date: 2026-03-03 18:30:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20260303_0005"
down_revision: Union[str, None] = "20260303_0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

submission_status_enum = sa.Enum(
    "pending",
    "approved",
    "rejected",
    name="submission_status",
    native_enum=False,
)


def upgrade() -> None:
    op.create_table(
        "recipe_submissions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("submitter_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("submitter_email", sa.String(length=255), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("category", sa.String(length=120), nullable=True),
        sa.Column("difficulty", sa.String(length=30), nullable=False, server_default="medium"),
        sa.Column("prep_time_minutes", sa.Integer(), nullable=True),
        sa.Column("servings_text", sa.String(length=120), nullable=True),
        sa.Column("instructions", sa.Text(), nullable=False),
        sa.Column("status", submission_status_enum, nullable=False, server_default="pending"),
        sa.Column("admin_note", sa.Text(), nullable=True),
        sa.Column("reviewed_by_admin_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_recipe_submissions_title", "recipe_submissions", ["title"], unique=False)
    op.create_index("ix_recipe_submissions_status", "recipe_submissions", ["status"], unique=False)
    op.create_index("ix_recipe_submissions_category", "recipe_submissions", ["category"], unique=False)
    op.create_index("ix_recipe_submissions_difficulty", "recipe_submissions", ["difficulty"], unique=False)
    op.create_index("ix_recipe_submissions_created_at", "recipe_submissions", ["created_at"], unique=False)
    op.create_index("ix_recipe_submissions_submitter_user_id", "recipe_submissions", ["submitter_user_id"], unique=False)
    op.create_index("ix_recipe_submissions_reviewed_by_admin_id", "recipe_submissions", ["reviewed_by_admin_id"], unique=False)

    op.create_table(
        "submission_ingredients",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "submission_id",
            sa.Integer(),
            sa.ForeignKey("recipe_submissions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("ingredient_name", sa.String(length=200), nullable=False),
        sa.Column("quantity_text", sa.String(length=120), nullable=False, server_default=""),
        sa.Column("grams", sa.Integer(), nullable=True),
        sa.Column("ingredient_name_normalized", sa.String(length=200), nullable=True),
    )
    op.create_index("ix_submission_ingredients_submission_id", "submission_ingredients", ["submission_id"], unique=False)
    op.create_index(
        "ix_submission_ingredients_ingredient_name_normalized",
        "submission_ingredients",
        ["ingredient_name_normalized"],
        unique=False,
    )

    op.create_table(
        "submission_images",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "submission_id",
            sa.Integer(),
            sa.ForeignKey("recipe_submissions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("content_type", sa.String(length=50), nullable=False),
        sa.Column("data", sa.LargeBinary(), nullable=False),
        sa.Column("is_primary", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_submission_images_submission_id", "submission_images", ["submission_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_submission_images_submission_id", table_name="submission_images")
    op.drop_table("submission_images")

    op.drop_index("ix_submission_ingredients_ingredient_name_normalized", table_name="submission_ingredients")
    op.drop_index("ix_submission_ingredients_submission_id", table_name="submission_ingredients")
    op.drop_table("submission_ingredients")

    op.drop_index("ix_recipe_submissions_reviewed_by_admin_id", table_name="recipe_submissions")
    op.drop_index("ix_recipe_submissions_submitter_user_id", table_name="recipe_submissions")
    op.drop_index("ix_recipe_submissions_created_at", table_name="recipe_submissions")
    op.drop_index("ix_recipe_submissions_difficulty", table_name="recipe_submissions")
    op.drop_index("ix_recipe_submissions_category", table_name="recipe_submissions")
    op.drop_index("ix_recipe_submissions_status", table_name="recipe_submissions")
    op.drop_index("ix_recipe_submissions_title", table_name="recipe_submissions")
    op.drop_table("recipe_submissions")

```
ZEILEN-ERKLAERUNG
1. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
2. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
3. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
4. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
5. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
6. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
7. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
8. Diese Zeile importiert gezielte Elemente aus einem anderen Modul.
9. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
10. Diese Zeile importiert gezielte Elemente aus einem anderen Modul.
11. Diese Zeile importiert benoetigte Module fuer die folgenden Funktionen.
12. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
13. Diese Zeile enthaelt einen Kommentar zur Orientierung im Code.
14. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
15. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
16. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
17. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
18. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
19. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
20. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
21. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
22. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
23. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
24. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
25. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
26. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
27. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
28. Diese Zeile startet die Definition einer Funktion.
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
54. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
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
76. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
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
93. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
94. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
95. Diese Zeile startet die Definition einer Funktion.
96. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
97. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
98. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
99. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
100. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
101. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
102. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
103. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
104. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
105. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
106. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
107. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
108. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
109. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
110. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.

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
6. Diese Zeile importiert gezielte Elemente aus einem anderen Modul.
7. Diese Zeile importiert gezielte Elemente aus einem anderen Modul.
8. Diese Zeile importiert gezielte Elemente aus einem anderen Modul.
9. Diese Zeile importiert gezielte Elemente aus einem anderen Modul.
10. Diese Zeile importiert gezielte Elemente aus einem anderen Modul.
11. Diese Zeile importiert gezielte Elemente aus einem anderen Modul.
12. Diese Zeile importiert gezielte Elemente aus einem anderen Modul.
13. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
14. Diese Zeile importiert gezielte Elemente aus einem anderen Modul.
15. Diese Zeile importiert gezielte Elemente aus einem anderen Modul.
16. Diese Zeile importiert gezielte Elemente aus einem anderen Modul.
17. Diese Zeile importiert gezielte Elemente aus einem anderen Modul.
18. Diese Zeile importiert gezielte Elemente aus einem anderen Modul.
19. Diese Zeile importiert gezielte Elemente aus einem anderen Modul.
20. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
21. Diese Zeile importiert gezielte Elemente aus einem anderen Modul.
22. Diese Zeile importiert gezielte Elemente aus einem anderen Modul.
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
33. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
34. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
35. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
36. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
37. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
38. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
39. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
40. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
41. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
42. Diese Zeile definiert einen Decorator fuer die nachfolgende Funktion.
43. Diese Zeile startet die Definition einer Klasse.
44. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
45. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
46. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
47. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
48. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
49. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
50. Diese Zeile startet die Definition einer Funktion.
51. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
52. Diese Zeile startet eine Schleife ueber mehrere Elemente.
53. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
54. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
55. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
56. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
57. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
58. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
59. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
60. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
61. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
62. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
63. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
64. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
65. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
66. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
67. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
68. Diese Zeile startet die Definition einer Funktion.
69. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
70. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
71. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
72. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
73. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
74. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
75. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
76. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
77. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
78. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
79. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
80. Diese Zeile startet die Definition einer Funktion.
81. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
82. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
83. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
84. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
85. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
86. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
87. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
88. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
89. Diese Zeile startet die Definition einer Funktion.
90. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
91. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
92. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
93. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
94. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
95. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
96. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
97. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
98. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
99. Diese Zeile startet die Definition einer Funktion.
100. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
101. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
102. Diese Zeile startet eine Schleife ueber mehrere Elemente.
103. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
104. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
105. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
106. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
107. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
108. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
109. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
110. Diese Zeile startet die Definition einer Funktion.
111. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
112. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
113. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
114. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
115. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
116. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
117. Diese Zeile startet die Definition einer Funktion.
118. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
119. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
120. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
121. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
122. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
123. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
124. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
125. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
126. Diese Zeile startet die Definition einer Funktion.
127. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
128. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
129. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
130. Diese Zeile startet die Definition einer Funktion.
131. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
132. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
133. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
134. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
135. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
136. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
137. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
138. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
139. Diese Zeile startet einen Block fuer Fehlerbehandlung.
140. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
141. Diese Zeile faengt einen moeglichen Fehler aus dem Try-Block ab.
142. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
143. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
144. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
145. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
146. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
147. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
148. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
149. Diese Zeile startet die Definition einer Funktion.
150. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
151. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
152. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
153. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
154. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
155. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
156. Diese Zeile startet die Definition einer Funktion.
157. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
158. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
159. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
160. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
161. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
162. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
163. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
164. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
165. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
166. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
167. Diese Zeile startet die Definition einer Funktion.
168. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
169. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
170. Diese Zeile startet eine Schleife ueber mehrere Elemente.
171. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
172. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
173. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
174. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
175. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
176. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
177. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
178. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
179. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
180. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
181. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
182. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
183. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
184. Diese Zeile definiert den Alternativzweig der Bedingung.
185. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
186. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
187. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
188. Diese Zeile startet eine Schleife ueber mehrere Elemente.
189. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
190. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
191. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
192. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
193. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
194. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
195. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
196. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
197. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
198. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
199. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
200. Diese Zeile startet die Definition einer Funktion.
201. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
202. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
203. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
204. Diese Zeile oeffnet einen neuen eingerueckten Logikblock.
205. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
206. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
207. Diese Zeile startet eine Schleife ueber mehrere Elemente.
208. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
209. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
210. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
211. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
212. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
213. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
214. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
215. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
216. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
217. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
218. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
219. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
220. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
221. Diese Zeile definiert den Alternativzweig der Bedingung.
222. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
223. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
224. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
225. Diese Zeile startet eine Schleife ueber mehrere Elemente.
226. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
227. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
228. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
229. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
230. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
231. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
232. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
233. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
234. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
235. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
236. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
237. Diese Zeile startet die Definition einer Funktion.
238. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
239. Diese Zeile startet eine Schleife ueber mehrere Elemente.
240. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
241. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
242. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
243. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
244. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
245. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
246. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
247. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
248. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
249. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
250. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
251. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
252. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
253. Diese Zeile startet die Definition einer Funktion.
254. Diese Zeile startet eine Schleife ueber mehrere Elemente.
255. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
256. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
257. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
258. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
259. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
260. Diese Zeile startet die Definition einer Funktion.
261. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
262. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
263. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
264. Diese Zeile loest eine Exception mit einer klaren Fehlersituation aus.
265. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
266. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
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
282. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
283. Diese Zeile startet eine Schleife ueber mehrere Elemente.
284. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
285. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
286. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
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
297. Diese Zeile startet eine Schleife ueber mehrere Elemente.
298. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
299. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
300. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
301. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
302. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
303. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
304. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
305. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
306. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
307. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
308. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
309. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
310. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
311. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
312. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
313. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
314. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
315. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
316. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
317. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
318. Diese Zeile startet die Definition einer Funktion.
319. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
320. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
321. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
322. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
323. Diese Zeile startet eine Schleife ueber mehrere Elemente.
324. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
325. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
326. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
327. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
328. Diese Zeile startet die Definition einer Funktion.
329. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
330. Diese Zeile loest eine Exception mit einer klaren Fehlersituation aus.
331. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
332. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
333. Diese Zeile loest eine Exception mit einer klaren Fehlersituation aus.
334. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
335. Diese Zeile startet einen Block fuer Fehlerbehandlung.
336. Diese Zeile oeffnet einen Kontextmanager fuer sichere Ressourcenverwaltung.
337. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
338. Diese Zeile faengt einen moeglichen Fehler aus dem Try-Block ab.
339. Diese Zeile loest eine Exception mit einer klaren Fehlersituation aus.
340. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
341. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
342. Diese Zeile definiert einen Decorator fuer die nachfolgende Funktion.
343. Diese Zeile startet die Definition einer Funktion.
344. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
345. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
346. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
347. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
348. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
349. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
350. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
351. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
352. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
353. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
354. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
355. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
356. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
357. Diese Zeile oeffnet einen Kontextmanager fuer sichere Ressourcenverwaltung.
358. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
359. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
360. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
361. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
362. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
363. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
364. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
365. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
366. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
367. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
368. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
369. Diese Zeile startet die Definition einer Funktion.
370. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
371. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
372. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
373. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
374. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
375. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
376. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
377. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
378. Diese Zeile startet die Definition einer Funktion.
379. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
380. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
381. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
382. Diese Zeile startet die Definition einer Funktion.
383. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
384. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
385. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
386. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
387. Diese Zeile startet die Definition einer Funktion.
388. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
389. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
390. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
391. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
392. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
393. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
394. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
395. Diese Zeile startet die Definition einer Funktion.
396. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
397. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
398. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
399. Diese Zeile startet die Definition einer Funktion.
400. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
401. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
402. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
403. Diese Zeile startet die Definition einer Funktion.
404. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
405. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
406. Diese Zeile loest eine Exception mit einer klaren Fehlersituation aus.
407. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
408. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
409. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
410. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
411. Diese Zeile startet die Definition einer Funktion.
412. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
413. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
414. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
415. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
416. Diese Zeile startet die Definition einer Funktion.
417. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
418. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
419. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
420. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
421. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
422. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
423. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
424. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
425. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
426. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
427. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
428. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
429. Diese Zeile startet die Definition einer Funktion.
430. Diese Zeile startet eine Schleife ueber mehrere Elemente.
431. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
432. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
433. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
434. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
435. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
436. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
437. Diese Zeile startet die Definition einer Funktion.
438. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
439. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
440. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
441. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
442. Diese Zeile startet die Definition einer Funktion.
443. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
444. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
445. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
446. Diese Zeile startet die Definition einer Funktion.
447. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
448. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
449. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
450. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
451. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
452. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
453. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
454. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
455. Diese Zeile startet die Definition einer Funktion.
456. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
457. Diese Zeile startet eine Schleife ueber mehrere Elemente.
458. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
459. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
460. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
461. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
462. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
463. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
464. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
465. Diese Zeile definiert den Alternativzweig der Bedingung.
466. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
467. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
468. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
469. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
470. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
471. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
472. Diese Zeile startet die Definition einer Funktion.
473. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
474. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
475. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
476. Diese Zeile startet eine Schleife ueber mehrere Elemente.
477. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
478. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
479. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
480. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
481. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
482. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
483. Diese Zeile startet die Definition einer Funktion.
484. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
485. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
486. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
487. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
488. Diese Zeile startet die Definition einer Funktion.
489. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
490. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
491. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
492. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
493. Diese Zeile startet die Definition einer Funktion.
494. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
495. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
496. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
497. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
498. Diese Zeile oeffnet einen neuen eingerueckten Logikblock.
499. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
500. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
501. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
502. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
503. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
504. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
505. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
506. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
507. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
508. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
509. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
510. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
511. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
512. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
513. Diese Zeile startet die Definition einer Funktion.
514. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
515. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
516. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
517. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
518. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
519. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
520. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
521. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
522. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
523. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
524. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
525. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
526. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
527. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
528. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
529. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
530. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
531. Diese Zeile startet die Definition einer Funktion.
532. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
533. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
534. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
535. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
536. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
537. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
538. Diese Zeile oeffnet einen Kontextmanager fuer sichere Ressourcenverwaltung.
539. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
540. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
541. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
542. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
543. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
544. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
545. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
546. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
547. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
548. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
549. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
550. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
551. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
552. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
553. Diese Zeile startet die Definition einer Funktion.
554. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
555. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
556. Diese Zeile loest eine Exception mit einer klaren Fehlersituation aus.
557. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
558. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
559. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
560. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
561. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
562. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
563. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
564. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
565. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
566. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
567. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
568. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
569. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
570. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
571. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
572. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
573. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
574. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
575. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
576. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
577. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
578. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
579. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
580. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
581. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
582. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
583. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
584. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
585. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
586. Diese Zeile startet die Definition einer Funktion.
587. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
588. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
589. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
590. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
591. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
592. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
593. Diese Zeile oeffnet einen neuen eingerueckten Logikblock.
594. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
595. Diese Zeile loest eine Exception mit einer klaren Fehlersituation aus.
596. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
597. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
598. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
599. Diese Zeile startet eine Schleife ueber mehrere Elemente.
600. Diese Zeile startet einen Block fuer Fehlerbehandlung.
601. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
602. Diese Zeile oeffnet einen Kontextmanager fuer sichere Ressourcenverwaltung.
603. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
604. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
605. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
606. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
607. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
608. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
609. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
610. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
611. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
612. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
613. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
614. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
615. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
616. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
617. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
618. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
619. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
620. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
621. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
622. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
623. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
624. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
625. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
626. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
627. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
628. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
629. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
630. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
631. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
632. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
633. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
634. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
635. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
636. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
637. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
638. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
639. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
640. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
641. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
642. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
643. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
644. Diese Zeile definiert den Alternativzweig der Bedingung.
645. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
646. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
647. Diese Zeile faengt einen moeglichen Fehler aus dem Try-Block ab.
648. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
649. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
650. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
651. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
652. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
653. Diese Zeile definiert den Alternativzweig der Bedingung.
654. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
655. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
656. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
657. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
658. Diese Zeile startet die Definition einer Funktion.
659. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
660. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
661. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
662. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
663. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
664. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
665. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
666. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
667. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
668. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
669. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
670. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
671. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
672. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
673. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
674. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
675. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
676. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
677. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
678. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
679. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
680. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
681. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
682. Diese Zeile startet eine Schleife ueber mehrere Elemente.
683. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
684. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
685. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
686. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
687. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
688. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
689. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
690. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
691. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
692. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
693. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
694. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
695. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
696. Diese Zeile startet eine Schleife ueber mehrere Elemente.
697. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
698. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
699. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
700. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
701. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
702. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
703. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
704. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
705. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
706. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
707. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
708. Diese Zeile startet die Definition einer Funktion.
709. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
710. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
711. Diese Zeile startet eine Schleife ueber mehrere Elemente.
712. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
713. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
714. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
715. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
716. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
717. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
718. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
719. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
720. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
721. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
722. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
723. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
724. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
725. Diese Zeile startet die Definition einer Funktion.
726. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.

## app/i18n/__init__.py
```python
import re
from datetime import datetime
from typing import Any

from app.i18n.de import DE_TEXTS

DIFFICULTY_MAP = {
    "easy": "difficulty.easy",
    "medium": "difficulty.medium",
    "hard": "difficulty.hard",
}

ROLE_MAP = {
    "user": "role.user",
    "admin": "role.admin",
}

SUBMISSION_STATUS_MAP = {
    "pending": "submission.status_pending",
    "approved": "submission.status_approved",
    "rejected": "submission.status_rejected",
}

ERROR_MAP = {
    "Authentication required.": "error.auth_required",
    "Admin role required.": "error.admin_required",
    "Invalid credentials.": "error.invalid_credentials",
    "Email already registered.": "error.email_registered",
    "Role must be user or admin.": "error.role_invalid",
    "User not found.": "error.user_not_found",
    "Recipe not found.": "error.recipe_not_found",
    "Review not found.": "error.review_not_found",
    "Image not found.": "error.image_not_found",
    "Not enough permissions for this recipe.": "error.recipe_permission",
    "Not enough permissions for this review.": "error.review_permission",
    "Rating must be between 1 and 5.": "error.rating_range",
    "Title and instructions are required.": "error.title_instructions_required",
    "title_image_url must start with http:// or https://": "error.image_url_scheme",
    "No image URL available.": "error.no_image_url",
    "KochWiki seed is already marked as done.": "error.seed_already_done",
    "Seed can only run on an empty recipes table.": "error.seed_not_empty",
    "Seed finished with errors, marker was not set.": "error.seed_finished_errors",
    "KochWiki seed finished successfully and was marked as done.": "error.seed_success",
    "Please upload a CSV file.": "error.csv_upload_required",
    "Only CSV uploads are allowed.": "error.csv_only",
    "CSV upload too large.": "error.csv_too_large",
    "Uploaded CSV file is empty.": "error.csv_empty",
    "Submission has already been published.": "error.submission_already_published",
    "Import finished in insert-only mode.": "error.import_finished_insert",
    "Import finished in update-existing mode.": "error.import_finished_update",
    "CSRF validation failed.": "error.csrf_failed",
    "Internal server error.": "error.internal",
}


def t(key: str, **kwargs: Any) -> str:
    template = DE_TEXTS.get(key, key)
    try:
        return template.format(**kwargs)
    except Exception:
        return template


def difficulty_label(value: str | None) -> str:
    if not value:
        return "-"
    mapped = DIFFICULTY_MAP.get(value.strip().lower())
    return t(mapped) if mapped else value


def role_label(value: str | None) -> str:
    if not value:
        return "-"
    mapped = ROLE_MAP.get(value.strip().lower())
    return t(mapped) if mapped else value


def submission_status_label(value: str | None) -> str:
    if not value:
        return "-"
    mapped = SUBMISSION_STATUS_MAP.get(value.strip().lower())
    return t(mapped) if mapped else value


def datetime_de(value: datetime | None) -> str:
    if value is None:
        return "-"
    return value.strftime("%d.%m.%Y %H:%M")


def translate_error_message(message: Any) -> Any:
    if not isinstance(message, str):
        return message
    if message in ERROR_MAP:
        return t(ERROR_MAP[message])
    int_match = re.match(r"^(.+?) must be an integer\.$", message)
    if int_match:
        return t("error.field_int", field=int_match.group(1))
    positive_match = re.match(r"^(.+?) must be greater than zero\.$", message)
    if positive_match:
        return t("error.field_positive", field=positive_match.group(1))
    csv_missing_match = re.match(r"^CSV file not found:\s*(.+)$", message)
    if csv_missing_match:
        return f"{t('error.csv_not_found_prefix')}: {csv_missing_match.group(1)}"
    image_resolve_match = re.match(r"^Could not resolve image URL:\s*(.+)$", message)
    if image_resolve_match:
        return f"{t('error.image_resolve_prefix')}: {image_resolve_match.group(1)}"
    return message

```
ZEILEN-ERKLAERUNG
1. Diese Zeile importiert benoetigte Module fuer die folgenden Funktionen.
2. Diese Zeile importiert gezielte Elemente aus einem anderen Modul.
3. Diese Zeile importiert gezielte Elemente aus einem anderen Modul.
4. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
5. Diese Zeile importiert gezielte Elemente aus einem anderen Modul.
6. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
7. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
8. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
9. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
10. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
11. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
12. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
13. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
14. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
15. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
16. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
17. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
18. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
19. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
20. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
21. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
22. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
23. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
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
54. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
55. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
56. Diese Zeile startet die Definition einer Funktion.
57. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
58. Diese Zeile startet einen Block fuer Fehlerbehandlung.
59. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
60. Diese Zeile faengt einen moeglichen Fehler aus dem Try-Block ab.
61. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
62. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
63. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
64. Diese Zeile startet die Definition einer Funktion.
65. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
66. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
67. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
68. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
69. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
70. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
71. Diese Zeile startet die Definition einer Funktion.
72. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
73. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
74. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
75. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
76. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
77. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
78. Diese Zeile startet die Definition einer Funktion.
79. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
80. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
81. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
82. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
83. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
84. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
85. Diese Zeile startet die Definition einer Funktion.
86. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
87. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
88. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
89. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
90. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
91. Diese Zeile startet die Definition einer Funktion.
92. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
93. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
94. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
95. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
96. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
97. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
98. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
99. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
100. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
101. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
102. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
103. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
104. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
105. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
106. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
107. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
108. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.

## app/i18n/de.py
```python
DE_TEXTS: dict[str, str] = {
    "app.name": "MealMate",
    "nav.discover": "Rezepte entdecken",
    "nav.submit_recipe": "Rezept einreichen",
    "nav.create_recipe": "Rezept erstellen",
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
166. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
167. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
168. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
169. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
170. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
171. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
172. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
173. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
174. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
175. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
176. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
177. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
178. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
179. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
180. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
181. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
182. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
183. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
184. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
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
221. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
222. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
223. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
224. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
225. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
226. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
227. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.

## app/views.py
```python
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from app.i18n import datetime_de, difficulty_label, role_label, submission_status_label, t

templates = Jinja2Templates(directory="app/templates")
templates.env.globals["t"] = t
templates.env.globals["difficulty_label"] = difficulty_label
templates.env.globals["role_label"] = role_label
templates.env.globals["submission_status_label"] = submission_status_label
templates.env.filters["datetime_de"] = datetime_de


def redirect(url: str, status_code: int = 303) -> RedirectResponse:
    return RedirectResponse(url=url, status_code=status_code)

```
ZEILEN-ERKLAERUNG
1. Diese Zeile importiert gezielte Elemente aus einem anderen Modul.
2. Diese Zeile importiert gezielte Elemente aus einem anderen Modul.
3. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
4. Diese Zeile importiert gezielte Elemente aus einem anderen Modul.
5. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
6. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
7. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
8. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
9. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
10. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
11. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
12. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
13. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
14. Diese Zeile startet die Definition einer Funktion.
15. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.

## app/routers/submissions.py
```python
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

```
ZEILEN-ERKLAERUNG
1. Diese Zeile importiert gezielte Elemente aus einem anderen Modul.
2. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
3. Diese Zeile importiert gezielte Elemente aus einem anderen Modul.
4. Diese Zeile importiert gezielte Elemente aus einem anderen Modul.
5. Diese Zeile importiert gezielte Elemente aus einem anderen Modul.
6. Diese Zeile importiert gezielte Elemente aus einem anderen Modul.
7. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
8. Diese Zeile importiert gezielte Elemente aus einem anderen Modul.
9. Diese Zeile importiert gezielte Elemente aus einem anderen Modul.
10. Diese Zeile importiert gezielte Elemente aus einem anderen Modul.
11. Diese Zeile importiert gezielte Elemente aus einem anderen Modul.
12. Diese Zeile importiert gezielte Elemente aus einem anderen Modul.
13. Diese Zeile importiert gezielte Elemente aus einem anderen Modul.
14. Diese Zeile importiert gezielte Elemente aus einem anderen Modul.
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
25. Diese Zeile importiert gezielte Elemente aus einem anderen Modul.
26. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
27. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
28. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
29. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
30. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
31. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
32. Diese Zeile startet die Definition einer Funktion.
33. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
34. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
35. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
36. Diese Zeile startet einen Block fuer Fehlerbehandlung.
37. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
38. Diese Zeile faengt einen moeglichen Fehler aus dem Try-Block ab.
39. Diese Zeile loest eine Exception mit einer klaren Fehlersituation aus.
40. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
41. Diese Zeile loest eine Exception mit einer klaren Fehlersituation aus.
42. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
43. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
44. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
45. Diese Zeile startet die Definition einer Funktion.
46. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
47. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
48. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
49. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
50. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
51. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
52. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
53. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
54. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
55. Diese Zeile startet die Definition einer Funktion.
56. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
57. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
58. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
59. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
60. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
61. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
62. Diese Zeile startet die Definition einer Funktion.
63. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
64. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
65. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
66. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
67. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
68. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
69. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
70. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
71. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
72. Diese Zeile startet die Definition einer Funktion.
73. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
74. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
75. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
76. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
77. Diese Zeile oeffnet einen neuen eingerueckten Logikblock.
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
95. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
96. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
97. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
98. Diese Zeile startet die Definition einer Funktion.
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
109. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
110. Diese Zeile loest eine Exception mit einer klaren Fehlersituation aus.
111. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
112. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
113. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
114. Diese Zeile startet die Definition einer Funktion.
115. Diese Zeile startet eine Schleife ueber mehrere Elemente.
116. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
117. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
118. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
119. Diese Zeile startet die Definition einer Funktion.
120. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
121. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
122. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
123. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
124. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
125. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
126. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
127. Diese Zeile definiert einen Decorator fuer die nachfolgende Funktion.
128. Diese Zeile startet die Definition einer Funktion.
129. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
130. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
131. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
132. Diese Zeile oeffnet einen neuen eingerueckten Logikblock.
133. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
134. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
135. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
136. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
137. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
138. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
139. Diese Zeile definiert einen Decorator fuer die nachfolgende Funktion.
140. Diese Zeile definiert einen Decorator fuer die nachfolgende Funktion.
141. Diese Zeile startet die Definition einer asynchronen Funktion.
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
158. Diese Zeile oeffnet einen neuen eingerueckten Logikblock.
159. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
160. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
161. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
162. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
163. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
164. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
165. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
166. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
167. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
168. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
169. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
170. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
171. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
172. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
173. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
174. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
175. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
176. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
177. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
178. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
179. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
180. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
181. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
182. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
183. Diese Zeile startet einen Block fuer Fehlerbehandlung.
184. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
185. Diese Zeile faengt einen moeglichen Fehler aus dem Try-Block ab.
186. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
187. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
188. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
189. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
190. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
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
221. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
222. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
223. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
224. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
225. Diese Zeile startet einen Block fuer Fehlerbehandlung.
226. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
227. Diese Zeile faengt einen moeglichen Fehler aus dem Try-Block ab.
228. Diese Zeile loest eine Exception mit einer klaren Fehlersituation aus.
229. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
230. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
231. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
232. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
233. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
234. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
235. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
236. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
237. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
238. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
239. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
240. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
241. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
242. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
243. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
244. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
245. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
246. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
247. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
248. Diese Zeile definiert einen Decorator fuer die nachfolgende Funktion.
249. Diese Zeile startet die Definition einer Funktion.
250. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
251. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
252. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
253. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
254. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
255. Diese Zeile oeffnet einen neuen eingerueckten Logikblock.
256. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
257. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
258. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
259. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
260. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
261. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
262. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
263. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
264. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
265. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
266. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
267. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
268. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
269. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
270. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
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
282. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
283. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
284. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
285. Diese Zeile definiert einen Decorator fuer die nachfolgende Funktion.
286. Diese Zeile startet die Definition einer Funktion.
287. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
288. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
289. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
290. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
291. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
292. Diese Zeile oeffnet einen neuen eingerueckten Logikblock.
293. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
294. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
295. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
296. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
297. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
298. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
299. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
300. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
301. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
302. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
303. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
304. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
305. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
306. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
307. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
308. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
309. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
310. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
311. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
312. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
313. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
314. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
315. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
316. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
317. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
318. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
319. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
320. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
321. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
322. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
323. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
324. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
325. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
326. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
327. Diese Zeile definiert einen Decorator fuer die nachfolgende Funktion.
328. Diese Zeile startet die Definition einer Funktion.
329. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
330. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
331. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
332. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
333. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
334. Diese Zeile oeffnet einen neuen eingerueckten Logikblock.
335. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
336. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
337. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
338. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
339. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
340. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
341. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
342. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
343. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
344. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
345. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
346. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
347. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
348. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
349. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
350. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
351. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
352. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
353. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
354. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
355. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
356. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
357. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
358. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
359. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
360. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
361. Diese Zeile definiert einen Decorator fuer die nachfolgende Funktion.
362. Diese Zeile definiert einen Decorator fuer die nachfolgende Funktion.
363. Diese Zeile startet die Definition einer asynchronen Funktion.
364. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
365. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
366. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
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
380. Diese Zeile oeffnet einen neuen eingerueckten Logikblock.
381. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
382. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
383. Diese Zeile loest eine Exception mit einer klaren Fehlersituation aus.
384. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
385. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
386. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
387. Diese Zeile loest eine Exception mit einer klaren Fehlersituation aus.
388. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
389. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
390. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
391. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
392. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
393. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
394. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
395. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
396. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
397. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
398. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
399. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
400. Diese Zeile startet einen Block fuer Fehlerbehandlung.
401. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
402. Diese Zeile faengt einen moeglichen Fehler aus dem Try-Block ab.
403. Diese Zeile loest eine Exception mit einer klaren Fehlersituation aus.
404. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
405. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
406. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
407. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
408. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
409. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
410. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
411. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
412. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
413. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
414. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
415. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
416. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
417. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
418. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
419. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
420. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
421. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
422. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
423. Diese Zeile definiert einen Decorator fuer die nachfolgende Funktion.
424. Diese Zeile definiert einen Decorator fuer die nachfolgende Funktion.
425. Diese Zeile startet die Definition einer Funktion.
426. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
427. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
428. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
429. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
430. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
431. Diese Zeile oeffnet einen neuen eingerueckten Logikblock.
432. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
433. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
434. Diese Zeile loest eine Exception mit einer klaren Fehlersituation aus.
435. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
436. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
437. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
438. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
439. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
440. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
441. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
442. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
443. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
444. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
445. Diese Zeile definiert einen Decorator fuer die nachfolgende Funktion.
446. Diese Zeile definiert einen Decorator fuer die nachfolgende Funktion.
447. Diese Zeile startet die Definition einer Funktion.
448. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
449. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
450. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
451. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
452. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
453. Diese Zeile oeffnet einen neuen eingerueckten Logikblock.
454. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
455. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
456. Diese Zeile loest eine Exception mit einer klaren Fehlersituation aus.
457. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
458. Diese Zeile loest eine Exception mit einer klaren Fehlersituation aus.
459. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
460. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
461. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
462. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
463. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
464. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
465. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
466. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
467. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
468. Diese Zeile definiert einen Decorator fuer die nachfolgende Funktion.
469. Diese Zeile definiert einen Decorator fuer die nachfolgende Funktion.
470. Diese Zeile startet die Definition einer Funktion.
471. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
472. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
473. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
474. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
475. Diese Zeile oeffnet einen neuen eingerueckten Logikblock.
476. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
477. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
478. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
479. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
480. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
481. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
482. Diese Zeile loest eine Exception mit einer klaren Fehlersituation aus.
483. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
484. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
485. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
486. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
487. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
488. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
489. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
490. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
491. Diese Zeile definiert einen Decorator fuer die nachfolgende Funktion.
492. Diese Zeile definiert einen Decorator fuer die nachfolgende Funktion.
493. Diese Zeile startet die Definition einer Funktion.
494. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
495. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
496. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
497. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
498. Diese Zeile oeffnet einen neuen eingerueckten Logikblock.
499. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
500. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
501. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
502. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
503. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
504. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
505. Diese Zeile loest eine Exception mit einer klaren Fehlersituation aus.
506. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
507. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
508. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
509. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
510. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
511. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
512. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
513. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
514. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
515. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
516. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
517. Diese Zeile definiert einen Decorator fuer die nachfolgende Funktion.
518. Diese Zeile startet die Definition einer Funktion.
519. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
520. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
521. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
522. Diese Zeile oeffnet einen neuen eingerueckten Logikblock.
523. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
524. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
525. Diese Zeile loest eine Exception mit einer klaren Fehlersituation aus.
526. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
527. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
528. Diese Zeile loest eine Exception mit einer klaren Fehlersituation aus.
529. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
530. Diese Zeile loest eine Exception mit einer klaren Fehlersituation aus.
531. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.

## app/routers/__init__.py
```python
from app.routers import admin, auth, recipes, submissions

__all__ = ["admin", "auth", "recipes", "submissions"]

```
ZEILEN-ERKLAERUNG
1. Diese Zeile importiert gezielte Elemente aus einem anderen Modul.
2. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
3. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.

## app/main.py
```python
import logging
import traceback
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from sqlalchemy import func, select
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.trustedhost import TrustedHostMiddleware
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

from app.config import get_settings
from app.database import SessionLocal
from app.dependencies import template_context
from app.i18n import t, translate_error_message
from app.logging_config import configure_logging
from app.middleware import CSRFMiddleware, HTTPSRedirectMiddleware, RequestContextMiddleware, SecurityHeadersMiddleware
from app.models import Recipe, User
from app.rate_limit import limiter
from app.routers import admin, auth, recipes, submissions
from app.security import hash_password
from app.services import import_kochwiki_csv, is_meta_true, set_meta_value
from app.views import templates

settings = get_settings()
configure_logging()
logger = logging.getLogger("mealmate.app")

app = FastAPI(title=settings.app_name, version="1.0.0", debug=not settings.prod_mode)


class CacheControlStaticFiles(StaticFiles):
    def __init__(self, *args, cache_control: str | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.cache_control = cache_control

    async def get_response(self, path: str, scope):
        response = await super().get_response(path, scope)
        if self.cache_control and response.status_code == 200:
            response.headers.setdefault("Cache-Control", self.cache_control)
        return response


app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")
if settings.allowed_hosts != ["*"]:
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.allowed_hosts)
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(CSRFMiddleware)
app.add_middleware(HTTPSRedirectMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestContextMiddleware)

static_dir = Path("app/static")
static_dir.mkdir(parents=True, exist_ok=True)
static_cache = "public, max-age=3600" if settings.prod_mode else None
app.mount("/static", CacheControlStaticFiles(directory=str(static_dir), cache_control=static_cache), name="static")

app.include_router(auth.router)
app.include_router(recipes.router)
app.include_router(submissions.router)
app.include_router(admin.router)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    accept = request.headers.get("accept", "")
    if exc.status_code == 404 and "text/html" in accept:
        return templates.TemplateResponse(
            "error_404.html",
            template_context(request, None, title=t("error.404_title")),
            status_code=404,
        )
    detail = translate_error_message(exc.detail)
    return JSONResponse({"detail": detail}, status_code=exc.status_code)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    request_id = getattr(request.state, "request_id", "-")
    logger.exception("unhandled_exception request_id=%s path=%s", request_id, request.url.path)
    accept = request.headers.get("accept", "")
    if settings.prod_mode:
        if "text/html" in accept:
            return templates.TemplateResponse(
                "error_500.html",
                template_context(request, None, title=t("error.500_title"), show_trace=False, error_trace=None),
                status_code=500,
            )
        return JSONResponse({"detail": t("error.internal")}, status_code=500)
    trace = traceback.format_exc()
    if "text/html" in accept:
        return templates.TemplateResponse(
            "error_500.html",
            template_context(request, None, title=t("error.500_title"), show_trace=True, error_trace=trace),
            status_code=500,
        )
    return JSONResponse({"detail": t("error.internal"), "trace": trace}, status_code=500)


def _ensure_seed_admin(db) -> User:
    admin = db.scalar(select(User).where(User.role == "admin").order_by(User.id))
    if admin:
        return admin
    fallback_email = settings.seed_admin_email.strip().lower()
    admin = db.scalar(select(User).where(User.email == fallback_email))
    if admin:
        admin.role = "admin"
        db.commit()
        db.refresh(admin)
        return admin
    admin = User(
        email=fallback_email,
        hashed_password=hash_password(settings.seed_admin_password),
        role="admin",
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin


def run_auto_seed_if_enabled() -> None:
    if not settings.auto_seed_kochwiki:
        return
    db = SessionLocal()
    try:
        if is_meta_true(db, "kochwiki_seed_done"):
            return
        recipes_count = db.scalar(select(func.count()).select_from(Recipe)) or 0
        if recipes_count > 0:
            return
        csv_path = Path(settings.kochwiki_csv_path)
        if not csv_path.exists():
            return
        admin_user = _ensure_seed_admin(db)
        report = import_kochwiki_csv(db, csv_path, admin_user.id, mode="insert_only")
        if report.errors:
            logger.warning("auto_seed_finished_with_errors errors=%s", len(report.errors))
            return
        set_meta_value(db, "kochwiki_seed_done", "1")
        db.commit()
        logger.info(
            "auto_seed_done inserted=%s updated=%s skipped=%s",
            report.inserted,
            report.updated,
            report.skipped,
        )
    finally:
        db.close()


@app.on_event("startup")
def startup_event() -> None:
    run_auto_seed_if_enabled()


@app.get("/health")
@app.get("/healthz")
def healthcheck():
    return {"status": "ok"}

```
ZEILEN-ERKLAERUNG
1. Diese Zeile importiert benoetigte Module fuer die folgenden Funktionen.
2. Diese Zeile importiert benoetigte Module fuer die folgenden Funktionen.
3. Diese Zeile importiert gezielte Elemente aus einem anderen Modul.
4. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
5. Diese Zeile importiert gezielte Elemente aus einem anderen Modul.
6. Diese Zeile importiert gezielte Elemente aus einem anderen Modul.
7. Diese Zeile importiert gezielte Elemente aus einem anderen Modul.
8. Diese Zeile importiert gezielte Elemente aus einem anderen Modul.
9. Diese Zeile importiert gezielte Elemente aus einem anderen Modul.
10. Diese Zeile importiert gezielte Elemente aus einem anderen Modul.
11. Diese Zeile importiert gezielte Elemente aus einem anderen Modul.
12. Diese Zeile importiert gezielte Elemente aus einem anderen Modul.
13. Diese Zeile importiert gezielte Elemente aus einem anderen Modul.
14. Diese Zeile importiert gezielte Elemente aus einem anderen Modul.
15. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
16. Diese Zeile importiert gezielte Elemente aus einem anderen Modul.
17. Diese Zeile importiert gezielte Elemente aus einem anderen Modul.
18. Diese Zeile importiert gezielte Elemente aus einem anderen Modul.
19. Diese Zeile importiert gezielte Elemente aus einem anderen Modul.
20. Diese Zeile importiert gezielte Elemente aus einem anderen Modul.
21. Diese Zeile importiert gezielte Elemente aus einem anderen Modul.
22. Diese Zeile importiert gezielte Elemente aus einem anderen Modul.
23. Diese Zeile importiert gezielte Elemente aus einem anderen Modul.
24. Diese Zeile importiert gezielte Elemente aus einem anderen Modul.
25. Diese Zeile importiert gezielte Elemente aus einem anderen Modul.
26. Diese Zeile importiert gezielte Elemente aus einem anderen Modul.
27. Diese Zeile importiert gezielte Elemente aus einem anderen Modul.
28. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
29. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
30. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
31. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
32. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
33. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
34. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
35. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
36. Diese Zeile startet die Definition einer Klasse.
37. Diese Zeile startet die Definition einer Funktion.
38. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
39. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
40. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
41. Diese Zeile startet die Definition einer asynchronen Funktion.
42. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
43. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
44. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
45. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
46. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
47. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
48. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
49. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
50. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
51. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
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
68. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
69. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
70. Diese Zeile definiert einen Decorator fuer die nachfolgende Funktion.
71. Diese Zeile startet die Definition einer asynchronen Funktion.
72. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
73. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
74. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
75. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
76. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
77. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
78. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
79. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
80. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
81. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
82. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
83. Diese Zeile definiert einen Decorator fuer die nachfolgende Funktion.
84. Diese Zeile startet die Definition einer asynchronen Funktion.
85. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
86. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
87. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
88. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
89. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
90. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
91. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
92. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
93. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
94. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
95. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
96. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
97. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
98. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
99. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
100. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
101. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
102. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
103. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
104. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
105. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
106. Diese Zeile startet die Definition einer Funktion.
107. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
108. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
109. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
110. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
111. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
112. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
113. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
114. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
115. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
116. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
117. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
118. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
119. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
120. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
121. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
122. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
123. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
124. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
125. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.
126. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
127. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
128. Diese Zeile startet die Definition einer Funktion.
129. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
130. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
131. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
132. Diese Zeile startet einen Block fuer Fehlerbehandlung.
133. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
134. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
135. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
136. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
137. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
138. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
139. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
140. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
141. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
142. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
143. Diese Zeile prueft eine Bedingung fuer den weiteren Ablauf.
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
154. Diese Zeile definiert den Abschlussblock der Fehlerbehandlung.
155. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
156. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
157. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
158. Diese Zeile definiert einen Decorator fuer die nachfolgende Funktion.
159. Diese Zeile startet die Definition einer Funktion.
160. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
161. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
162. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
163. Diese Zeile definiert einen Decorator fuer die nachfolgende Funktion.
164. Diese Zeile definiert einen Decorator fuer die nachfolgende Funktion.
165. Diese Zeile startet die Definition einer Funktion.
166. Diese Zeile gibt einen Rueckgabewert aus der Funktion zurueck.

## app/templates/base.html
```html
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
      <a href="/recipes/new">{{ t("nav.create_recipe") }}</a>
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
ZEILEN-ERKLAERUNG
1. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
2. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
3. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
4. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
5. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
6. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
7. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
8. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
9. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
10. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
11. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
12. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
13. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
14. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
15. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
16. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
17. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
18. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
19. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
20. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
21. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
22. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
23. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
24. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
25. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
26. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
27. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
28. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
29. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
30. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
31. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
32. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
33. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
34. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
35. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
36. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
37. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
38. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
39. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
40. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
41. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.

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
  <p><a href="/admin/submissions">{{ t("submission.admin_queue_link") }}</a></p>
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
3. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
4. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
5. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
6. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
7. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
8. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
9. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
10. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
11. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
12. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
13. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
14. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
15. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
16. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
17. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
18. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
19. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
20. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
21. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
22. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
23. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
24. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
25. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
26. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
27. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
28. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
29. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
30. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
31. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
32. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
33. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
34. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
35. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
36. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
37. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
38. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
39. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
40. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
41. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
42. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
43. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
44. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
45. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
46. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
47. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
48. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
49. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
50. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
51. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
52. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
53. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
54. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
55. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
56. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
57. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
58. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
59. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
60. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
61. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
62. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
63. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
64. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
65. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
66. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
67. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
68. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
69. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
70. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
71. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
72. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
73. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
74. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
75. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
76. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
77. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
78. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
79. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
80. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
81. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
82. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
83. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
84. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
85. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
86. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
87. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
88. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
89. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
90. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
91. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
92. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
93. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
94. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
95. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
96. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
97. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
98. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
99. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
100. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
101. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
102. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
103. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
104. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
105. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
106. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
107. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
108. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
109. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
110. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
111. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
112. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
113. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
114. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
115. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.

## app/templates/submit_recipe.html
```html
{% extends "base.html" %}
{% block content %}
<section class="panel">
  <h1>{{ t("submission.submit_title") }}</h1>
  <p class="meta">{{ t("submission.submit_hint") }}</p>
  {% if message %}
  <p class="meta">{{ message }}</p>
  {% endif %}
  {% if error %}
  <p class="error">{{ error }}</p>
  {% endif %}
  <form method="post" action="/submit" enctype="multipart/form-data" class="stack">
    {% if not current_user %}
    <label>{{ t("submission.submitter_email") }} <input type="email" name="submitter_email" value="{{ submitter_email_value }}" placeholder="name@example.com"></label>
    {% endif %}
    <label>{{ t("submission.title") }} <input type="text" name="title" value="{{ title_value }}" required></label>
    <label>{{ t("submission.description") }} <textarea name="description" rows="3">{{ description_value }}</textarea></label>
    <label>{{ t("submission.instructions") }} <textarea name="instructions" rows="8" required>{{ instructions_value }}</textarea></label>
    <label>{{ t("submission.category") }}
      <select name="category_select" id="category_select">
        {% for option in category_options %}
        <option value="{{ option }}" {% if selected_category == option %}selected{% endif %}>{{ option }}</option>
        {% endfor %}
        <option value="__new__">{{ t("submission.new_category_option") }}</option>
      </select>
    </label>
    <div id="new-category-wrapper" class="stack hidden">
      <label>{{ t("submission.new_category_label") }} <input type="text" id="category_new" name="category_new" value="{{ category_new_value }}"></label>
    </div>
    <label>{{ t("submission.difficulty") }}
      <select name="difficulty">
        <option value="easy" {% if difficulty_value == "easy" %}selected{% endif %}>{{ t("difficulty.easy") }}</option>
        <option value="medium" {% if difficulty_value == "medium" %}selected{% endif %}>{{ t("difficulty.medium") }}</option>
        <option value="hard" {% if difficulty_value == "hard" %}selected{% endif %}>{{ t("difficulty.hard") }}</option>
      </select>
    </label>
    <label>{{ t("submission.prep_time") }} <input type="number" min="1" name="prep_time_minutes" value="{{ prep_time_value }}"></label>
    <label>{{ t("submission.servings") }} <input type="text" name="servings_text" value="{{ servings_value }}"></label>
    <label>{{ t("submission.ingredients") }}
      <textarea name="ingredients_text" rows="6" placeholder="Tomate|2 Stueck&#10;Olivenoel|1 EL">{{ ingredients_text }}</textarea>
    </label>
    <label>{{ t("submission.image_optional") }} <input type="file" name="image" accept="image/png,image/jpeg,image/webp"></label>
    <button type="submit">{{ t("submission.submit_button") }}</button>
  </form>
</section>
{% endblock %}

```
ZEILEN-ERKLAERUNG
1. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
2. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
3. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
4. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
5. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
6. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
7. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
8. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
9. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
10. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
11. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
12. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
13. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
14. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
15. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
16. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
17. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
18. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
19. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
20. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
21. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
22. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
23. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
24. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
25. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
26. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
27. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
28. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
29. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
30. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
31. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
32. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
33. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
34. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
35. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
36. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
37. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
38. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
39. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
40. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
41. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
42. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
43. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
44. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
45. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
46. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.

## app/templates/my_submissions.html
```html
{% extends "base.html" %}
{% block content %}
<section class="panel">
  <h1>{{ t("submission.my_title") }}</h1>
  {% if submitted %}
  <p class="meta">{{ t("submission.my_submitted_message") }}</p>
  {% endif %}
  {% if submissions %}
  <p class="list-summary">{{ t("pagination.results_range", start=((page - 1) * 20 + 1), end=((page - 1) * 20 + submissions|length), total=total_count) }}</p>
  <div class="cards">
    {% for submission in submissions %}
    <article class="card">
      {% if submission.images %}
      <img src="/submission-images/{{ submission.images[0].id }}" alt="{{ submission.title }}" class="thumb">
      {% endif %}
      <h3>{{ submission.title }}</h3>
      <p class="meta">{{ submission_status_label(submission.status) }} | {{ submission.created_at|datetime_de }}</p>
      <p class="meta">{{ submission.category or "-" }} | {{ difficulty_label(submission.difficulty) }}</p>
      {% if submission.admin_note %}
      <p class="meta">{{ t("submission.admin_note") }}: {{ submission.admin_note }}</p>
      {% endif %}
    </article>
    {% endfor %}
  </div>
  {% if total_pages > 1 %}
  <div class="pagination">
    <div class="pagination-links">
      {% if page > 1 %}
      <a href="/my-submissions?page={{ page - 1 }}">{{ t("pagination.previous") }}</a>
      {% else %}
      <span class="disabled">{{ t("pagination.previous") }}</span>
      {% endif %}
      {% for item in pagination_items %}
      {% if item is none %}
      <span class="ellipsis">...</span>
      {% elif item == page %}
      <span class="active">{{ item }}</span>
      {% else %}
      <a href="/my-submissions?page={{ item }}">{{ item }}</a>
      {% endif %}
      {% endfor %}
      {% if page < total_pages %}
      <a href="/my-submissions?page={{ page + 1 }}">{{ t("pagination.next") }}</a>
      {% else %}
      <span class="disabled">{{ t("pagination.next") }}</span>
      {% endif %}
    </div>
    <span class="pagination-info">{{ t("pagination.page") }} {{ page }} / {{ total_pages }}</span>
  </div>
  {% endif %}
  {% else %}
  <p>{{ t("submission.my_empty") }}</p>
  {% endif %}
</section>
{% endblock %}

```
ZEILEN-ERKLAERUNG
1. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
2. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
3. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
4. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
5. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
6. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
7. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
8. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
9. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
10. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
11. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
12. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
13. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
14. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
15. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
16. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
17. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
18. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
19. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
20. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
21. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
22. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
23. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
24. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
25. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
26. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
27. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
28. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
29. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
30. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
31. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
32. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
33. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
34. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
35. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
36. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
37. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
38. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
39. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
40. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
41. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
42. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
43. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
44. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
45. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
46. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
47. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
48. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
49. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
50. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
51. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
52. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
53. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
54. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
55. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.

## app/templates/admin_submissions.html
```html
{% extends "base.html" %}
{% block content %}
<section class="panel">
  <h1>{{ t("submission.admin_queue_title") }}</h1>
  <form method="get" action="/admin/submissions" class="inline">
    <label>{{ t("submission.status_filter") }}
      <select name="status_filter">
        <option value="pending" {% if status_filter == "pending" %}selected{% endif %}>{{ t("submission.status_pending") }}</option>
        <option value="approved" {% if status_filter == "approved" %}selected{% endif %}>{{ t("submission.status_approved") }}</option>
        <option value="rejected" {% if status_filter == "rejected" %}selected{% endif %}>{{ t("submission.status_rejected") }}</option>
        <option value="all" {% if status_filter == "all" %}selected{% endif %}>{{ t("submission.status_all") }}</option>
      </select>
    </label>
    <button type="submit">{{ t("home.apply") }}</button>
  </form>
  <p class="meta">
    {{ t("submission.stats_pending") }}: {{ status_stats.pending }},
    {{ t("submission.stats_approved") }}: {{ status_stats.approved }},
    {{ t("submission.stats_rejected") }}: {{ status_stats.rejected }}
  </p>
</section>
<section class="panel">
  {% if submissions %}
  <table>
    <thead>
      <tr>
        <th>{{ t("submission.table_date") }}</th>
        <th>{{ t("submission.table_title") }}</th>
        <th>{{ t("submission.table_submitter") }}</th>
        <th>{{ t("submission.table_status") }}</th>
        <th>{{ t("submission.table_action") }}</th>
      </tr>
    </thead>
    <tbody>
      {% for submission in submissions %}
      <tr>
        <td>{{ submission.created_at|datetime_de }}</td>
        <td>{{ submission.title }}</td>
        <td>
          {% if submission.submitter_user %}
          {{ submission.submitter_user.email }}
          {% elif submission.submitter_email %}
          {{ submission.submitter_email }}
          {% else %}
          {{ t("submission.guest") }}
          {% endif %}
        </td>
        <td>{{ submission_status_label(submission.status) }}</td>
        <td><a href="/admin/submissions/{{ submission.id }}">{{ t("submission.open_detail") }}</a></td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
  {% if total_pages > 1 %}
  <div class="pagination">
    <div class="pagination-links">
      {% if page > 1 %}
      <a href="/admin/submissions?status_filter={{ status_filter }}&page={{ page - 1 }}">{{ t("pagination.previous") }}</a>
      {% else %}
      <span class="disabled">{{ t("pagination.previous") }}</span>
      {% endif %}
      {% for item in pagination_items %}
      {% if item is none %}
      <span class="ellipsis">...</span>
      {% elif item == page %}
      <span class="active">{{ item }}</span>
      {% else %}
      <a href="/admin/submissions?status_filter={{ status_filter }}&page={{ item }}">{{ item }}</a>
      {% endif %}
      {% endfor %}
      {% if page < total_pages %}
      <a href="/admin/submissions?status_filter={{ status_filter }}&page={{ page + 1 }}">{{ t("pagination.next") }}</a>
      {% else %}
      <span class="disabled">{{ t("pagination.next") }}</span>
      {% endif %}
    </div>
    <span class="pagination-info">{{ t("pagination.page") }} {{ page }} / {{ total_pages }}</span>
  </div>
  {% endif %}
  {% else %}
  <p>{{ t("submission.admin_empty") }}</p>
  {% endif %}
</section>
{% endblock %}

```
ZEILEN-ERKLAERUNG
1. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
2. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
3. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
4. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
5. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
6. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
7. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
8. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
9. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
10. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
11. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
12. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
13. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
14. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
15. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
16. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
17. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
18. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
19. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
20. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
21. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
22. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
23. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
24. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
25. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
26. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
27. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
28. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
29. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
30. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
31. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
32. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
33. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
34. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
35. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
36. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
37. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
38. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
39. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
40. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
41. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
42. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
43. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
44. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
45. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
46. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
47. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
48. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
49. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
50. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
51. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
52. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
53. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
54. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
55. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
56. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
57. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
58. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
59. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
60. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
61. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
62. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
63. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
64. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
65. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
66. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
67. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
68. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
69. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
70. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
71. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
72. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
73. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
74. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
75. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
76. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
77. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
78. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
79. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
80. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
81. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
82. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
83. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
84. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.

## app/templates/admin_submission_detail.html
```html
{% extends "base.html" %}
{% block content %}
<section class="panel">
  <h1>{{ t("submission.admin_detail_title") }} #{{ submission.id }}</h1>
  <p class="meta">
    {{ submission_status_label(submission.status) }} |
    {{ submission.created_at|datetime_de }} |
    {% if submission.submitter_user %}
    {{ submission.submitter_user.email }}
    {% elif submission.submitter_email %}
    {{ submission.submitter_email }}
    {% else %}
    {{ t("submission.guest") }}
    {% endif %}
  </p>
  {% if message %}
  <p class="meta">{{ message }}</p>
  {% endif %}
  {% if submission.admin_note %}
  <p class="meta">{{ t("submission.admin_note") }}: {{ submission.admin_note }}</p>
  {% endif %}
  <div class="actions">
    <a href="/admin/submissions">{{ t("submission.back_to_queue") }}</a>
  </div>
</section>
<section class="panel">
  <h2>{{ t("submission.preview") }}</h2>
  {% if submission.images %}
  <div class="cards">
    {% for image in submission.images %}
    <article class="card">
      <img src="/submission-images/{{ image.id }}" alt="{{ submission.title }}" class="thumb">
      <p class="meta">{% if image.is_primary %}{{ t("images.primary") }}{% endif %}</p>
      <div class="actions">
        <form method="post" action="/admin/submissions/images/{{ image.id }}/set-primary">
          <button type="submit">{{ t("images.set_primary") }}</button>
        </form>
        <form method="post" action="/admin/submissions/images/{{ image.id }}/delete">
          <button type="submit">{{ t("images.delete") }}</button>
        </form>
      </div>
    </article>
    {% endfor %}
  </div>
  {% else %}
  <p>{{ t("images.empty") }}</p>
  {% endif %}
  <h3>{{ submission.title }}</h3>
  <p>{{ submission.description }}</p>
  <p class="meta">{{ submission.category or "-" }} | {{ difficulty_label(submission.difficulty) }} | {{ submission.prep_time_minutes or "-" }} min</p>
  {% if submission.servings_text %}
  <p class="meta">{{ t("submission.servings") }}: {{ submission.servings_text }}</p>
  {% endif %}
  <h4>{{ t("recipe.ingredients") }}</h4>
  <ul>
    {% for ingredient in submission.ingredients %}
    <li>{{ ingredient.ingredient_name }} {% if ingredient.quantity_text %}({{ ingredient.quantity_text }}){% endif %}{% if ingredient.grams is not none %} - {{ ingredient.grams }} g{% endif %}</li>
    {% else %}
    <li>{{ t("recipe.no_ingredients") }}</li>
    {% endfor %}
  </ul>
  <h4>{{ t("recipe.instructions") }}</h4>
  <pre>{{ submission.instructions }}</pre>
</section>
<section class="panel">
  <h2>{{ t("submission.edit_submission") }}</h2>
  <form method="post" action="/admin/submissions/{{ submission.id }}/edit" enctype="multipart/form-data" class="stack">
    <label>{{ t("submission.title") }} <input type="text" name="title" value="{{ submission.title }}" required></label>
    <label>{{ t("submission.description") }} <textarea name="description" rows="3">{{ submission.description }}</textarea></label>
    <label>{{ t("submission.instructions") }} <textarea name="instructions" rows="8" required>{{ submission.instructions }}</textarea></label>
    <label>{{ t("submission.category") }}
      <select name="category_select" id="category_select">
        {% for option in category_options %}
        <option value="{{ option }}" {% if selected_category == option %}selected{% endif %}>{{ option }}</option>
        {% endfor %}
        <option value="__new__">{{ t("submission.new_category_option") }}</option>
      </select>
    </label>
    <div id="new-category-wrapper" class="stack hidden">
      <label>{{ t("submission.new_category_label") }} <input type="text" id="category_new" name="category_new"></label>
    </div>
    <label>{{ t("submission.difficulty") }}
      <select name="difficulty">
        <option value="easy" {% if submission.difficulty == "easy" %}selected{% endif %}>{{ t("difficulty.easy") }}</option>
        <option value="medium" {% if submission.difficulty == "medium" %}selected{% endif %}>{{ t("difficulty.medium") }}</option>
        <option value="hard" {% if submission.difficulty == "hard" %}selected{% endif %}>{{ t("difficulty.hard") }}</option>
      </select>
    </label>
    <label>{{ t("submission.prep_time") }} <input type="number" min="1" name="prep_time_minutes" value="{{ submission.prep_time_minutes or '' }}"></label>
    <label>{{ t("submission.servings") }} <input type="text" name="servings_text" value="{{ submission.servings_text or '' }}"></label>
    <label>{{ t("submission.ingredients") }} <textarea name="ingredients_text" rows="7">{{ ingredients_text }}</textarea></label>
    <label>{{ t("submission.image_optional") }} <input type="file" name="image" accept="image/png,image/jpeg,image/webp"></label>
    <label class="inline">
      <input type="checkbox" name="set_primary_new_image">
      {{ t("submission.set_primary_new_image") }}
    </label>
    <button type="submit">{{ t("submission.save_changes") }}</button>
  </form>
</section>
<section class="panel">
  <h2>{{ t("submission.moderation_actions") }}</h2>
  <form method="post" action="/admin/submissions/{{ submission.id }}/approve" class="stack">
    <label>{{ t("submission.optional_admin_note") }} <textarea name="admin_note" rows="3">{{ submission.admin_note or "" }}</textarea></label>
    <button type="submit">{{ t("submission.approve_button") }}</button>
  </form>
  <form method="post" action="/admin/submissions/{{ submission.id }}/reject" class="stack">
    <label>{{ t("submission.reject_reason") }} <textarea name="admin_note" rows="3" required></textarea></label>
    <button type="submit">{{ t("submission.reject_button") }}</button>
  </form>
</section>
{% endblock %}

```
ZEILEN-ERKLAERUNG
1. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
2. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
3. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
4. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
5. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
6. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
7. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
8. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
9. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
10. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
11. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
12. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
13. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
14. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
15. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
16. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
17. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
18. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
19. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
20. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
21. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
22. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
23. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
24. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
25. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
26. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
27. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
28. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
29. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
30. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
31. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
32. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
33. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
34. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
35. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
36. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
37. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
38. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
39. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
40. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
41. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
42. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
43. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
44. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
45. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
46. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
47. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
48. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
49. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
50. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
51. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
52. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
53. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
54. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
55. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
56. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
57. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
58. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
59. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
60. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
61. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
62. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
63. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
64. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
65. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
66. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
67. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
68. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
69. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
70. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
71. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
72. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
73. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
74. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
75. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
76. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
77. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
78. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
79. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
80. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
81. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
82. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
83. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
84. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
85. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
86. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
87. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
88. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
89. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
90. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
91. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
92. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
93. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
94. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
95. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
96. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
97. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
98. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
99. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
100. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
101. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
102. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
103. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
104. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
105. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
106. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
107. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
108. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
109. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
110. Diese Zeile enthaelt ein HTML-Element der Benutzeroberflaeche.
111. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.

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

pre {
  white-space: pre-wrap;
  word-break: break-word;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: #f8fafc;
  padding: 0.7rem;
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
248. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
249. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
250. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
251. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
252. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
253. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
254. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
255. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
256. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
257. Diese Zeile ist leer und trennt logisch zwei Abschnitte.
258. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
259. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
260. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
261. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
262. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
263. Diese Zeile setzt die jeweilige Logik oder Darstellung im aktuellen Abschnitt um.
