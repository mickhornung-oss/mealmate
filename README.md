# MealMate

Production-nahe FastAPI Web-App mit server-rendered HTML (Jinja2), HTMX, SQLAlchemy 2.0, Alembic, JWT-Auth und SQLite/Postgres-Unterstuetzung.

## Features

- Register/Login/Logout mit JWT in HttpOnly-Cookie
- Rollen: `user` und `admin`
- Rezept-CRUD (Owner oder Admin)
- Discover mit Filtern, Sortierung, Pagination und HTMX-Partial-Updates
- Zutaten normalisiert ueber `ingredients` und `recipe_ingredients`
- Reviews (1-5), Durchschnitts-Rating und Review-Count
- Favoriten
- Bild-Upload in DB (`recipe_images`), MIME- und Groessen-Checks
- Admin-Import (`/admin/import-recipes`) fuer CSV/JSON mit robustem Feld-Mapping
- PDF-Download je Rezept (`/recipes/{id}/pdf`) via ReportLab

## Lokal starten

```bash
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
py -m alembic -c alembic.ini upgrade head
py scripts/seed_admin.py
py -m uvicorn app.main:app --reload
```

App: http://localhost:8000  
Admin Login: `admin@mealmate.local` / `AdminPass123!`

## Docker starten

```bash
docker compose up --build
```

## KochWiki CSV importieren

```bash
py scripts/import_csv_to_db.py --file rezepte_kochwiki_clean_3713.csv
```

## Wichtige Endpunkte

- `POST /recipes/{id}/images` (Owner/Admin)
- `GET /images/{image_id}`
- `DELETE /images/{image_id}` (Owner/Admin)
- `POST /admin/import-recipes` (Admin)
- `GET /recipes/{id}/pdf`
