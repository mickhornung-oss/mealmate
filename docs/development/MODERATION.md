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
