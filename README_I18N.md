# MealMate i18n

## Zweck

MealMate nutzt JSON-basierte Lokalisierung fuer die Website-Texte.
Aktiv sind `de`, `en` und `fr`, Standard ist `de`.

## Aufloesung der Sprache

Die Sprache wird pro Request in dieser Reihenfolge bestimmt:

1. Query-Parameter `?lang=de|en|fr`
2. Cookie `lang`
3. Header `Accept-Language`
4. Default `de`

Wenn `?lang=...` gesetzt ist, schreibt die App den Cookie `lang` (1 Jahr).

## Struktur

- Locale-Dateien:
  - `app/i18n/locales/de.json`
  - `app/i18n/locales/en.json`
  - `app/i18n/locales/fr.json`
- Service:
  - `app/i18n/service.py`
- Middleware:
  - `app/i18n/middleware.py`

## Verwendung in Templates

In Jinja2 ist `t("key")` global verfuegbar.

Beispiele:

- `{{ t("nav.discover") }}`
- `{{ t("pagination.results_range", start=1, end=10, total=120) }}`

Zusaetzlich sind verfuegbar:

- `current_lang` (z. B. `de`)
- `available_langs` (Liste fuer Sprachumschalter)
- `lang_url(request, "en")` zum Erzeugen von Sprach-URLs

## Fallback-Logik

Wenn ein Key in der aktiven Sprache fehlt:

1. Fallback auf `de.json`
2. wenn dort auch fehlend: Rueckgabe des Keys selbst

## Neue Sprache hinzufuegen (it/es)

1. Neue Datei anlegen, z. B. `app/i18n/locales/it.json`
2. Alle benoetigten Keys ergaenzen
3. In `app/i18n/service.py`:
   - `SUPPORTED_LANGS` erweitern
   - `LANG_LABELS` erweitern
4. App neu starten

## Wichtige Keys (Auszug)

- `nav.discover`
- `nav.submit`
- `nav.admin`
- `discover.title`
- `discover.filter.title_contains`
- `discover.filter.category`
- `discover.filter.difficulty`
- `discover.filter.ingredient`
- `discover.filter.apply`
- `discover.sort.newest`
- `discover.sort.oldest`
- `discover.sort.rating_desc`
- `discover.sort.rating_asc`
- `discover.sort.prep_time`
- `pagination.prev`
- `pagination.next`
- `empty.no_recipes`
- `auth.login`
- `auth.register`
- `admin.title`
- `moderation.title`
- `moderation.pending`
- `moderation.approve`
- `moderation.reject`
- `difficulty.easy`
- `difficulty.medium`
- `difficulty.hard`
