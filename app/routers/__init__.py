from app.category_canonical import install_canonical_category_overrides

install_canonical_category_overrides()

from app.routers import admin, auth, legal, recipes, submissions, translations

__all__ = ["admin", "auth", "legal", "recipes", "submissions", "translations"]
