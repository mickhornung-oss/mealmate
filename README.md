# MealMate

Production-grade FastAPI web app with server-rendered HTML (Jinja2), HTMX, SQLAlchemy 2.0, Alembic, JWT authentication, and SQLite/PostgreSQL support.

**Features:**
- Register/Login/Logout with JWT in HttpOnly cookies  
- Role-based access: `user` and `admin`  
- Recipe CRUD (owner or admin)  
- Recipe discovery with filters, sorting, pagination, and HTMX partial updates  
- Normalized ingredients via `ingredients` and `recipe_ingredients` tables  
- Reviews (1-5 stars) with average rating and count  
- Favorites system  
- Image upload to database with MIME and size validation  
- Admin CSV/JSON recipe import with robust field mapping  
- PDF recipe export via ReportLab  

## Quick Start (Local)

```bash
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
py -m alembic -c alembic.ini upgrade head
py scripts/seed_admin.py
py -m uvicorn app.main:app --reload
```

**Access:**
- App: http://localhost:8000  
- Admin: `admin@mealmate.local` / `AdminPass123!`

## Docker

```bash
docker compose up --build
```

## API Endpoints

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/recipes/{id}/images` | Owner/Admin | Upload recipe image |
| GET | `/images/{image_id}` | Public | Fetch image |
| DELETE | `/images/{image_id}` | Owner/Admin | Delete image |
| POST | `/admin/import-recipes` | Admin | Bulk import CSV/JSON |
| GET | `/recipes/{id}/pdf` | Public | Export recipe as PDF |

## Known Audit Exceptions

- `starlette` & `js2py`: Upstream has open security advisories, stack migration pending
