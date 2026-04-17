# Geaenderte Dateien
- app/i18n/de.py
- app/i18n/__init__.py
- app/views.py
- app/config.py
- app/dependencies.py
- app/security.py
- app/routers/auth.py
- app/routers/admin.py
- app/middleware.py
- app/image_utils.py
- app/main.py
- app/templates/base.html
- app/templates/home.html
- app/templates/auth_login.html
- app/templates/auth_register.html
- app/templates/recipe_form.html
- app/templates/recipe_detail.html
- app/templates/admin.html
- app/templates/favorites.html
- app/templates/my_recipes.html
- app/templates/me.html
- app/templates/partials/recipe_list.html
- app/templates/partials/favorite_button.html
- app/templates/partials/recipe_images.html
- app/templates/error_404.html
- app/templates/error_500.html

## app/i18n/de.py
```python
DE_TEXTS: dict[str, str] = {
    "app.name": "MealMate",
    "nav.discover": "Rezepte entdecken",
    "nav.create_recipe": "Rezept erstellen",
    "nav.my_recipes": "Meine Rezepte",
    "nav.favorites": "Favoriten",
    "nav.profile": "Mein Profil",
    "nav.admin": "Admin",
    "nav.login": "Anmelden",
    "nav.register": "Registrieren",
    "nav.logout": "Abmelden",
    "home.title": "Rezepte entdecken",
    "home.title_contains": "Titel enthaelt",
    "home.category": "Kategorie",
    "home.difficulty": "Schwierigkeit",
    "home.ingredient": "Zutat",
    "home.apply": "Anwenden",
    "sort.newest": "Neueste",
    "sort.oldest": "Aelteste",
    "sort.highest_rated": "Beste Bewertung",
    "sort.lowest_rated": "Schlechteste Bewertung",
    "sort.prep_time": "Zubereitungszeit",
    "pagination.previous": "Zurueck",
    "pagination.next": "Weiter",
    "pagination.page": "Seite",
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
    "recipe_form.prep_time": "Zubereitungszeit (Minuten)",
    "recipe_form.difficulty": "Schwierigkeit",
    "recipe_form.ingredients": "Zutaten (Format: name|menge|gramm)",
    "recipe_form.optional_image": "Optionales Bild",
    "recipe_form.save": "Speichern",
    "recipe_form.create": "Erstellen",
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
    "error.review_not_found": "Bewertung nicht gefunden.",
    "error.image_not_found": "Bild nicht gefunden.",
    "error.recipe_permission": "Keine ausreichenden Rechte fuer dieses Rezept.",
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
ZEILEN-ERKL?RUNG
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
28. Diese Zeile setzt einen Teil der Implementierung um.
29. Diese Zeile setzt einen Teil der Implementierung um.
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
46. Diese Zeile setzt einen Teil der Implementierung um.
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
59. Diese Zeile setzt einen Teil der Implementierung um.
60. Diese Zeile setzt einen Teil der Implementierung um.
61. Diese Zeile setzt einen Teil der Implementierung um.
62. Diese Zeile setzt einen Teil der Implementierung um.
63. Diese Zeile setzt einen Teil der Implementierung um.
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
84. Diese Zeile setzt einen Teil der Implementierung um.
85. Diese Zeile setzt einen Teil der Implementierung um.
86. Diese Zeile setzt einen Teil der Implementierung um.
87. Diese Zeile setzt einen Teil der Implementierung um.
88. Diese Zeile setzt einen Teil der Implementierung um.
89. Diese Zeile setzt einen Teil der Implementierung um.
90. Diese Zeile setzt einen Teil der Implementierung um.
91. Diese Zeile setzt einen Teil der Implementierung um.
92. Diese Zeile setzt einen Teil der Implementierung um.
93. Diese Zeile setzt einen Teil der Implementierung um.
94. Diese Zeile setzt einen Teil der Implementierung um.
95. Diese Zeile setzt einen Teil der Implementierung um.
96. Diese Zeile setzt einen Teil der Implementierung um.
97. Diese Zeile setzt einen Teil der Implementierung um.
98. Diese Zeile setzt einen Teil der Implementierung um.
99. Diese Zeile setzt einen Teil der Implementierung um.
100. Diese Zeile setzt einen Teil der Implementierung um.
101. Diese Zeile setzt einen Teil der Implementierung um.
102. Diese Zeile setzt einen Teil der Implementierung um.
103. Diese Zeile setzt einen Teil der Implementierung um.
104. Diese Zeile setzt einen Teil der Implementierung um.
105. Diese Zeile setzt einen Teil der Implementierung um.
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
135. Diese Zeile setzt einen Teil der Implementierung um.
136. Diese Zeile setzt einen Teil der Implementierung um.
137. Diese Zeile setzt einen Teil der Implementierung um.
138. Diese Zeile setzt einen Teil der Implementierung um.
139. Diese Zeile setzt einen Teil der Implementierung um.
140. Diese Zeile setzt einen Teil der Implementierung um.
141. Diese Zeile setzt einen Teil der Implementierung um.
142. Diese Zeile setzt einen Teil der Implementierung um.
143. Diese Zeile setzt einen Teil der Implementierung um.
144. Diese Zeile setzt einen Teil der Implementierung um.
145. Diese Zeile setzt einen Teil der Implementierung um.
146. Diese Zeile setzt einen Teil der Implementierung um.
147. Diese Zeile setzt einen Teil der Implementierung um.
148. Diese Zeile setzt einen Teil der Implementierung um.
149. Diese Zeile setzt einen Teil der Implementierung um.
150. Diese Zeile setzt einen Teil der Implementierung um.
151. Diese Zeile setzt einen Teil der Implementierung um.
152. Diese Zeile setzt einen Teil der Implementierung um.
153. Diese Zeile setzt einen Teil der Implementierung um.
154. Diese Zeile setzt einen Teil der Implementierung um.
155. Diese Zeile setzt einen Teil der Implementierung um.

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
ZEILEN-ERKL?RUNG
1. Diese Zeile importiert benoetigte Abhaengigkeiten.
2. Diese Zeile importiert benoetigte Abhaengigkeiten.
3. Diese Zeile importiert benoetigte Abhaengigkeiten.
4. Diese Zeile ist absichtlich leer.
5. Diese Zeile importiert benoetigte Abhaengigkeiten.
6. Diese Zeile ist absichtlich leer.
7. Diese Zeile setzt einen Teil der Implementierung um.
8. Diese Zeile setzt einen Teil der Implementierung um.
9. Diese Zeile setzt einen Teil der Implementierung um.
10. Diese Zeile setzt einen Teil der Implementierung um.
11. Diese Zeile setzt einen Teil der Implementierung um.
12. Diese Zeile ist absichtlich leer.
13. Diese Zeile setzt einen Teil der Implementierung um.
14. Diese Zeile setzt einen Teil der Implementierung um.
15. Diese Zeile setzt einen Teil der Implementierung um.
16. Diese Zeile setzt einen Teil der Implementierung um.
17. Diese Zeile ist absichtlich leer.
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
28. Diese Zeile setzt einen Teil der Implementierung um.
29. Diese Zeile setzt einen Teil der Implementierung um.
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
46. Diese Zeile setzt einen Teil der Implementierung um.
47. Diese Zeile ist absichtlich leer.
48. Diese Zeile ist absichtlich leer.
49. Diese Zeile startet eine Funktionsdefinition.
50. Diese Zeile setzt einen Teil der Implementierung um.
51. Diese Zeile gehoert zur Fehlerbehandlung.
52. Diese Zeile setzt einen Teil der Implementierung um.
53. Diese Zeile gehoert zur Fehlerbehandlung.
54. Diese Zeile setzt einen Teil der Implementierung um.
55. Diese Zeile ist absichtlich leer.
56. Diese Zeile ist absichtlich leer.
57. Diese Zeile startet eine Funktionsdefinition.
58. Diese Zeile steuert den bedingten Ablauf.
59. Diese Zeile setzt einen Teil der Implementierung um.
60. Diese Zeile setzt einen Teil der Implementierung um.
61. Diese Zeile setzt einen Teil der Implementierung um.
62. Diese Zeile ist absichtlich leer.
63. Diese Zeile ist absichtlich leer.
64. Diese Zeile startet eine Funktionsdefinition.
65. Diese Zeile steuert den bedingten Ablauf.
66. Diese Zeile setzt einen Teil der Implementierung um.
67. Diese Zeile setzt einen Teil der Implementierung um.
68. Diese Zeile setzt einen Teil der Implementierung um.
69. Diese Zeile ist absichtlich leer.
70. Diese Zeile ist absichtlich leer.
71. Diese Zeile startet eine Funktionsdefinition.
72. Diese Zeile steuert den bedingten Ablauf.
73. Diese Zeile setzt einen Teil der Implementierung um.
74. Diese Zeile setzt einen Teil der Implementierung um.
75. Diese Zeile ist absichtlich leer.
76. Diese Zeile ist absichtlich leer.
77. Diese Zeile startet eine Funktionsdefinition.
78. Diese Zeile steuert den bedingten Ablauf.
79. Diese Zeile setzt einen Teil der Implementierung um.
80. Diese Zeile steuert den bedingten Ablauf.
81. Diese Zeile setzt einen Teil der Implementierung um.
82. Diese Zeile setzt einen Teil der Implementierung um.
83. Diese Zeile steuert den bedingten Ablauf.
84. Diese Zeile setzt einen Teil der Implementierung um.
85. Diese Zeile setzt einen Teil der Implementierung um.
86. Diese Zeile steuert den bedingten Ablauf.
87. Diese Zeile setzt einen Teil der Implementierung um.
88. Diese Zeile setzt einen Teil der Implementierung um.
89. Diese Zeile steuert den bedingten Ablauf.
90. Diese Zeile setzt einen Teil der Implementierung um.
91. Diese Zeile setzt einen Teil der Implementierung um.
92. Diese Zeile steuert den bedingten Ablauf.
93. Diese Zeile setzt einen Teil der Implementierung um.
94. Diese Zeile setzt einen Teil der Implementierung um.

## app/views.py
```python
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from app.i18n import datetime_de, difficulty_label, role_label, t

templates = Jinja2Templates(directory="app/templates")
templates.env.globals["t"] = t
templates.env.globals["difficulty_label"] = difficulty_label
templates.env.globals["role_label"] = role_label
templates.env.filters["datetime_de"] = datetime_de


def redirect(url: str, status_code: int = 303) -> RedirectResponse:
    return RedirectResponse(url=url, status_code=status_code)
```
ZEILEN-ERKL?RUNG
1. Diese Zeile importiert benoetigte Abhaengigkeiten.
2. Diese Zeile importiert benoetigte Abhaengigkeiten.
3. Diese Zeile ist absichtlich leer.
4. Diese Zeile importiert benoetigte Abhaengigkeiten.
5. Diese Zeile ist absichtlich leer.
6. Diese Zeile setzt einen Teil der Implementierung um.
7. Diese Zeile setzt einen Teil der Implementierung um.
8. Diese Zeile setzt einen Teil der Implementierung um.
9. Diese Zeile setzt einen Teil der Implementierung um.
10. Diese Zeile setzt einen Teil der Implementierung um.
11. Diese Zeile ist absichtlich leer.
12. Diese Zeile ist absichtlich leer.
13. Diese Zeile startet eine Funktionsdefinition.
14. Diese Zeile setzt einen Teil der Implementierung um.

## app/config.py
```python
from functools import lru_cache
from typing import Annotated, Literal

from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore", case_sensitive=False)

    app_name: str = "MealMate"
    app_env: Literal["dev", "prod"] = "dev"
    app_url: AnyHttpUrl = "http://localhost:8000"
    secret_key: str = "change-me"
    algorithm: str = "HS256"
    token_expire_minutes: int = 60
    database_url: str = "sqlite:///./mealmate.db"
    allowed_hosts: Annotated[list[str], NoDecode] = ["*"]
    cookie_secure: bool | None = None
    force_https: bool | None = None
    log_level: str = "INFO"
    csrf_cookie_name: str = "csrf_token"
    csrf_header_name: str = "X-CSRF-Token"
    max_upload_mb: int = 4
    max_csv_upload_mb: int = 10
    allowed_image_types: Annotated[list[str], NoDecode] = ["image/png", "image/jpeg", "image/webp"]
    auto_seed_kochwiki: bool = False
    kochwiki_csv_path: str = "rezepte_kochwiki_clean_3713.csv"
    import_download_images: bool = False
    seed_admin_email: str = "admin@mealmate.local"
    seed_admin_password: str = "AdminPass123!"

    @field_validator("allowed_image_types", mode="before")
    @classmethod
    def parse_allowed_image_types(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, list):
            return [item.strip() for item in value if item.strip()]
        return [item.strip() for item in value.split(",") if item.strip()]

    @field_validator("allowed_hosts", mode="before")
    @classmethod
    def parse_allowed_hosts(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, list):
            hosts = [item.strip() for item in value if item.strip()]
        else:
            hosts = [item.strip() for item in value.split(",") if item.strip()]
        return hosts or ["*"]

    @field_validator("log_level", mode="before")
    @classmethod
    def parse_log_level(cls, value: str) -> str:
        return str(value).strip().upper() or "INFO"

    @property
    def sqlalchemy_database_url(self) -> str:
        url = self.database_url.strip()
        if url.startswith("postgres://"):
            return "postgresql+psycopg://" + url[len("postgres://") :]
        if url.startswith("postgresql://"):
            return "postgresql+psycopg://" + url[len("postgresql://") :]
        return url

    @property
    def is_sqlite(self) -> bool:
        return self.sqlalchemy_database_url.startswith("sqlite")

    @property
    def prod_mode(self) -> bool:
        return self.app_env == "prod"

    @property
    def resolved_cookie_secure(self) -> bool:
        if self.cookie_secure is None:
            return self.prod_mode
        return self.cookie_secure

    @property
    def resolved_force_https(self) -> bool:
        if self.force_https is None:
            return self.prod_mode
        return self.force_https


@lru_cache
def get_settings() -> Settings:
    return Settings()
```
ZEILEN-ERKL?RUNG
1. Diese Zeile importiert benoetigte Abhaengigkeiten.
2. Diese Zeile importiert benoetigte Abhaengigkeiten.
3. Diese Zeile ist absichtlich leer.
4. Diese Zeile importiert benoetigte Abhaengigkeiten.
5. Diese Zeile importiert benoetigte Abhaengigkeiten.
6. Diese Zeile ist absichtlich leer.
7. Diese Zeile ist absichtlich leer.
8. Diese Zeile startet eine Klassendefinition.
9. Diese Zeile setzt einen Teil der Implementierung um.
10. Diese Zeile ist absichtlich leer.
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
28. Diese Zeile setzt einen Teil der Implementierung um.
29. Diese Zeile setzt einen Teil der Implementierung um.
30. Diese Zeile setzt einen Teil der Implementierung um.
31. Diese Zeile setzt einen Teil der Implementierung um.
32. Diese Zeile ist absichtlich leer.
33. Diese Zeile definiert einen Dekorator fuer den folgenden Block.
34. Diese Zeile definiert einen Dekorator fuer den folgenden Block.
35. Diese Zeile startet eine Funktionsdefinition.
36. Diese Zeile steuert den bedingten Ablauf.
37. Diese Zeile setzt einen Teil der Implementierung um.
38. Diese Zeile setzt einen Teil der Implementierung um.
39. Diese Zeile ist absichtlich leer.
40. Diese Zeile definiert einen Dekorator fuer den folgenden Block.
41. Diese Zeile definiert einen Dekorator fuer den folgenden Block.
42. Diese Zeile startet eine Funktionsdefinition.
43. Diese Zeile steuert den bedingten Ablauf.
44. Diese Zeile setzt einen Teil der Implementierung um.
45. Diese Zeile steuert den bedingten Ablauf.
46. Diese Zeile setzt einen Teil der Implementierung um.
47. Diese Zeile setzt einen Teil der Implementierung um.
48. Diese Zeile ist absichtlich leer.
49. Diese Zeile definiert einen Dekorator fuer den folgenden Block.
50. Diese Zeile definiert einen Dekorator fuer den folgenden Block.
51. Diese Zeile startet eine Funktionsdefinition.
52. Diese Zeile setzt einen Teil der Implementierung um.
53. Diese Zeile ist absichtlich leer.
54. Diese Zeile definiert einen Dekorator fuer den folgenden Block.
55. Diese Zeile startet eine Funktionsdefinition.
56. Diese Zeile setzt einen Teil der Implementierung um.
57. Diese Zeile steuert den bedingten Ablauf.
58. Diese Zeile setzt einen Teil der Implementierung um.
59. Diese Zeile steuert den bedingten Ablauf.
60. Diese Zeile setzt einen Teil der Implementierung um.
61. Diese Zeile setzt einen Teil der Implementierung um.
62. Diese Zeile ist absichtlich leer.
63. Diese Zeile definiert einen Dekorator fuer den folgenden Block.
64. Diese Zeile startet eine Funktionsdefinition.
65. Diese Zeile setzt einen Teil der Implementierung um.
66. Diese Zeile ist absichtlich leer.
67. Diese Zeile definiert einen Dekorator fuer den folgenden Block.
68. Diese Zeile startet eine Funktionsdefinition.
69. Diese Zeile setzt einen Teil der Implementierung um.
70. Diese Zeile ist absichtlich leer.
71. Diese Zeile definiert einen Dekorator fuer den folgenden Block.
72. Diese Zeile startet eine Funktionsdefinition.
73. Diese Zeile steuert den bedingten Ablauf.
74. Diese Zeile setzt einen Teil der Implementierung um.
75. Diese Zeile setzt einen Teil der Implementierung um.
76. Diese Zeile ist absichtlich leer.
77. Diese Zeile definiert einen Dekorator fuer den folgenden Block.
78. Diese Zeile startet eine Funktionsdefinition.
79. Diese Zeile steuert den bedingten Ablauf.
80. Diese Zeile setzt einen Teil der Implementierung um.
81. Diese Zeile setzt einen Teil der Implementierung um.
82. Diese Zeile ist absichtlich leer.
83. Diese Zeile ist absichtlich leer.
84. Diese Zeile definiert einen Dekorator fuer den folgenden Block.
85. Diese Zeile startet eine Funktionsdefinition.
86. Diese Zeile setzt einen Teil der Implementierung um.

## app/dependencies.py
```python
from typing import Any

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.i18n import t
from app.models import User
from app.security import decode_access_token
from app.services import extract_token

settings = get_settings()


def get_current_user_optional(request: Request, db: Session = Depends(get_db)) -> User | None:
    cookie_token = request.cookies.get("access_token")
    header_token = extract_token(request.headers.get("Authorization"))
    raw_token = cookie_token or header_token
    token = extract_token(raw_token)
    if not token:
        return None
    try:
        payload = decode_access_token(token)
    except ValueError:
        return None
    subject = str(payload.get("sub", ""))
    if not subject:
        return None
    user = db.scalar(select(User).where(User.email == subject))
    if user:
        request.state.current_user = user
        request.state.rate_limit_user_key = f"user:{user.id}"
    return user


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    user = get_current_user_optional(request, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=t("error.auth_required"))
    return user


def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=t("error.admin_required"))
    return current_user


def template_context(request: Request, current_user: User | None, **kwargs: Any) -> dict[str, Any]:
    csrf_token = getattr(request.state, "csrf_token", None) or request.cookies.get("csrf_token")
    request_id = getattr(request.state, "request_id", None)
    base = {
        "request": request,
        "current_user": current_user,
        "csrf_token": csrf_token,
        "csrf_header_name": settings.csrf_header_name,
        "request_id": request_id,
    }
    base.update(kwargs)
    return base
```
ZEILEN-ERKL?RUNG
1. Diese Zeile importiert benoetigte Abhaengigkeiten.
2. Diese Zeile ist absichtlich leer.
3. Diese Zeile importiert benoetigte Abhaengigkeiten.
4. Diese Zeile importiert benoetigte Abhaengigkeiten.
5. Diese Zeile importiert benoetigte Abhaengigkeiten.
6. Diese Zeile ist absichtlich leer.
7. Diese Zeile importiert benoetigte Abhaengigkeiten.
8. Diese Zeile importiert benoetigte Abhaengigkeiten.
9. Diese Zeile importiert benoetigte Abhaengigkeiten.
10. Diese Zeile importiert benoetigte Abhaengigkeiten.
11. Diese Zeile importiert benoetigte Abhaengigkeiten.
12. Diese Zeile importiert benoetigte Abhaengigkeiten.
13. Diese Zeile ist absichtlich leer.
14. Diese Zeile setzt einen Teil der Implementierung um.
15. Diese Zeile ist absichtlich leer.
16. Diese Zeile ist absichtlich leer.
17. Diese Zeile startet eine Funktionsdefinition.
18. Diese Zeile setzt einen Teil der Implementierung um.
19. Diese Zeile setzt einen Teil der Implementierung um.
20. Diese Zeile setzt einen Teil der Implementierung um.
21. Diese Zeile setzt einen Teil der Implementierung um.
22. Diese Zeile steuert den bedingten Ablauf.
23. Diese Zeile setzt einen Teil der Implementierung um.
24. Diese Zeile gehoert zur Fehlerbehandlung.
25. Diese Zeile setzt einen Teil der Implementierung um.
26. Diese Zeile gehoert zur Fehlerbehandlung.
27. Diese Zeile setzt einen Teil der Implementierung um.
28. Diese Zeile setzt einen Teil der Implementierung um.
29. Diese Zeile steuert den bedingten Ablauf.
30. Diese Zeile setzt einen Teil der Implementierung um.
31. Diese Zeile setzt einen Teil der Implementierung um.
32. Diese Zeile steuert den bedingten Ablauf.
33. Diese Zeile setzt einen Teil der Implementierung um.
34. Diese Zeile setzt einen Teil der Implementierung um.
35. Diese Zeile setzt einen Teil der Implementierung um.
36. Diese Zeile ist absichtlich leer.
37. Diese Zeile ist absichtlich leer.
38. Diese Zeile startet eine Funktionsdefinition.
39. Diese Zeile setzt einen Teil der Implementierung um.
40. Diese Zeile steuert den bedingten Ablauf.
41. Diese Zeile setzt einen Teil der Implementierung um.
42. Diese Zeile setzt einen Teil der Implementierung um.
43. Diese Zeile ist absichtlich leer.
44. Diese Zeile ist absichtlich leer.
45. Diese Zeile startet eine Funktionsdefinition.
46. Diese Zeile steuert den bedingten Ablauf.
47. Diese Zeile setzt einen Teil der Implementierung um.
48. Diese Zeile setzt einen Teil der Implementierung um.
49. Diese Zeile ist absichtlich leer.
50. Diese Zeile ist absichtlich leer.
51. Diese Zeile startet eine Funktionsdefinition.
52. Diese Zeile setzt einen Teil der Implementierung um.
53. Diese Zeile setzt einen Teil der Implementierung um.
54. Diese Zeile setzt einen Teil der Implementierung um.
55. Diese Zeile setzt einen Teil der Implementierung um.
56. Diese Zeile setzt einen Teil der Implementierung um.
57. Diese Zeile setzt einen Teil der Implementierung um.
58. Diese Zeile setzt einen Teil der Implementierung um.
59. Diese Zeile setzt einen Teil der Implementierung um.
60. Diese Zeile setzt einen Teil der Implementierung um.
61. Diese Zeile setzt einen Teil der Implementierung um.
62. Diese Zeile setzt einen Teil der Implementierung um.

## app/security.py
```python
from datetime import datetime, timedelta, timezone
import re

from jose import JWTError, jwt
from pwdlib import PasswordHash

from app.config import get_settings
from app.i18n import t

password_hash = PasswordHash.recommended()
settings = get_settings()


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)


def validate_password_policy(password: str) -> str | None:
    if len(password) < 10:
        return t("error.password_min_length")
    if not re.search(r"[A-Z]", password):
        return t("error.password_upper")
    if not re.search(r"\d", password):
        return t("error.password_number")
    if not re.search(r"[^A-Za-z0-9]", password):
        return t("error.password_special")
    return None


def create_access_token(subject: str, role: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.token_expire_minutes)
    payload = {"sub": subject, "role": role, "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def decode_access_token(token: str) -> dict[str, str]:
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except JWTError as exc:
        raise ValueError("Invalid token") from exc
```
ZEILEN-ERKL?RUNG
1. Diese Zeile importiert benoetigte Abhaengigkeiten.
2. Diese Zeile importiert benoetigte Abhaengigkeiten.
3. Diese Zeile ist absichtlich leer.
4. Diese Zeile importiert benoetigte Abhaengigkeiten.
5. Diese Zeile importiert benoetigte Abhaengigkeiten.
6. Diese Zeile ist absichtlich leer.
7. Diese Zeile importiert benoetigte Abhaengigkeiten.
8. Diese Zeile importiert benoetigte Abhaengigkeiten.
9. Diese Zeile ist absichtlich leer.
10. Diese Zeile setzt einen Teil der Implementierung um.
11. Diese Zeile setzt einen Teil der Implementierung um.
12. Diese Zeile ist absichtlich leer.
13. Diese Zeile ist absichtlich leer.
14. Diese Zeile startet eine Funktionsdefinition.
15. Diese Zeile setzt einen Teil der Implementierung um.
16. Diese Zeile ist absichtlich leer.
17. Diese Zeile ist absichtlich leer.
18. Diese Zeile startet eine Funktionsdefinition.
19. Diese Zeile setzt einen Teil der Implementierung um.
20. Diese Zeile ist absichtlich leer.
21. Diese Zeile ist absichtlich leer.
22. Diese Zeile startet eine Funktionsdefinition.
23. Diese Zeile steuert den bedingten Ablauf.
24. Diese Zeile setzt einen Teil der Implementierung um.
25. Diese Zeile steuert den bedingten Ablauf.
26. Diese Zeile setzt einen Teil der Implementierung um.
27. Diese Zeile steuert den bedingten Ablauf.
28. Diese Zeile setzt einen Teil der Implementierung um.
29. Diese Zeile steuert den bedingten Ablauf.
30. Diese Zeile setzt einen Teil der Implementierung um.
31. Diese Zeile setzt einen Teil der Implementierung um.
32. Diese Zeile ist absichtlich leer.
33. Diese Zeile ist absichtlich leer.
34. Diese Zeile startet eine Funktionsdefinition.
35. Diese Zeile setzt einen Teil der Implementierung um.
36. Diese Zeile setzt einen Teil der Implementierung um.
37. Diese Zeile setzt einen Teil der Implementierung um.
38. Diese Zeile ist absichtlich leer.
39. Diese Zeile ist absichtlich leer.
40. Diese Zeile startet eine Funktionsdefinition.
41. Diese Zeile gehoert zur Fehlerbehandlung.
42. Diese Zeile setzt einen Teil der Implementierung um.
43. Diese Zeile gehoert zur Fehlerbehandlung.
44. Diese Zeile setzt einen Teil der Implementierung um.

## app/routers/auth.py
```python
from fastapi import APIRouter, Depends, Form, HTTPException, Request, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.dependencies import get_current_user, get_current_user_optional, template_context
from app.i18n import t
from app.models import User
from app.rate_limit import key_by_ip, limiter
from app.security import create_access_token, hash_password, validate_password_policy, verify_password
from app.views import redirect, templates

router = APIRouter(tags=["auth"])
settings = get_settings()


def set_auth_cookie(response, token: str) -> None:
    response.set_cookie(
        key="access_token",
        value=f"Bearer {token}",
        httponly=True,
        secure=settings.resolved_cookie_secure,
        samesite="lax",
        max_age=60 * 60 * 24,
        path="/",
    )


@router.get("/login")
@router.get("/auth/login")
def login_page(request: Request, current_user: User | None = Depends(get_current_user_optional)):
    if current_user:
        return redirect("/")
    return templates.TemplateResponse("auth_login.html", template_context(request, current_user, error=None))


@router.post("/login")
@router.post("/auth/login")
@limiter.limit("5/minute", key_func=key_by_ip)
def login_submit(
    request: Request,
    response: Response,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    _ = response
    user = db.scalar(select(User).where(User.email == email.strip().lower()))
    if not user or not verify_password(password, user.hashed_password):
        response = templates.TemplateResponse(
            "auth_login.html",
            template_context(request, None, error=t("error.invalid_credentials")),
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
        return response
    token = create_access_token(user.email, user.role)
    response = redirect("/")
    set_auth_cookie(response, token)
    return response


@router.get("/register")
@router.get("/auth/register")
def register_page(request: Request, current_user: User | None = Depends(get_current_user_optional)):
    if current_user:
        return redirect("/")
    return templates.TemplateResponse("auth_register.html", template_context(request, current_user, error=None))


@router.post("/register")
@router.post("/auth/register")
@limiter.limit("3/minute", key_func=key_by_ip)
def register_submit(
    request: Request,
    response: Response,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    _ = response
    normalized_email = email.strip().lower()
    password_error = validate_password_policy(password)
    if password_error:
        return templates.TemplateResponse(
            "auth_register.html",
            template_context(request, None, error=password_error),
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    existing = db.scalar(select(User).where(User.email == normalized_email))
    if existing:
        return templates.TemplateResponse(
            "auth_register.html",
            template_context(request, None, error=t("error.email_registered")),
            status_code=status.HTTP_409_CONFLICT,
        )
    user = User(email=normalized_email, hashed_password=hash_password(password), role="user")
    db.add(user)
    db.commit()
    token = create_access_token(user.email, user.role)
    response = redirect("/")
    set_auth_cookie(response, token)
    return response


@router.post("/logout")
def logout():
    response = redirect("/")
    response.delete_cookie("access_token", path="/")
    return response


@router.get("/me")
def me_page(request: Request, current_user: User = Depends(get_current_user)):
    return templates.TemplateResponse("me.html", template_context(request, current_user, user=current_user))


@router.get("/api/me")
def me_api(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "role": current_user.role,
        "created_at": current_user.created_at.isoformat(),
    }


@router.get("/admin-only")
def admin_only(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=t("error.admin_required"))
    return {"message": t("role.admin")}
```
ZEILEN-ERKL?RUNG
1. Diese Zeile importiert benoetigte Abhaengigkeiten.
2. Diese Zeile importiert benoetigte Abhaengigkeiten.
3. Diese Zeile importiert benoetigte Abhaengigkeiten.
4. Diese Zeile ist absichtlich leer.
5. Diese Zeile importiert benoetigte Abhaengigkeiten.
6. Diese Zeile importiert benoetigte Abhaengigkeiten.
7. Diese Zeile importiert benoetigte Abhaengigkeiten.
8. Diese Zeile importiert benoetigte Abhaengigkeiten.
9. Diese Zeile importiert benoetigte Abhaengigkeiten.
10. Diese Zeile importiert benoetigte Abhaengigkeiten.
11. Diese Zeile importiert benoetigte Abhaengigkeiten.
12. Diese Zeile importiert benoetigte Abhaengigkeiten.
13. Diese Zeile ist absichtlich leer.
14. Diese Zeile setzt einen Teil der Implementierung um.
15. Diese Zeile setzt einen Teil der Implementierung um.
16. Diese Zeile ist absichtlich leer.
17. Diese Zeile ist absichtlich leer.
18. Diese Zeile startet eine Funktionsdefinition.
19. Diese Zeile setzt einen Teil der Implementierung um.
20. Diese Zeile setzt einen Teil der Implementierung um.
21. Diese Zeile setzt einen Teil der Implementierung um.
22. Diese Zeile setzt einen Teil der Implementierung um.
23. Diese Zeile setzt einen Teil der Implementierung um.
24. Diese Zeile setzt einen Teil der Implementierung um.
25. Diese Zeile setzt einen Teil der Implementierung um.
26. Diese Zeile setzt einen Teil der Implementierung um.
27. Diese Zeile setzt einen Teil der Implementierung um.
28. Diese Zeile ist absichtlich leer.
29. Diese Zeile ist absichtlich leer.
30. Diese Zeile definiert einen Dekorator fuer den folgenden Block.
31. Diese Zeile definiert einen Dekorator fuer den folgenden Block.
32. Diese Zeile startet eine Funktionsdefinition.
33. Diese Zeile steuert den bedingten Ablauf.
34. Diese Zeile setzt einen Teil der Implementierung um.
35. Diese Zeile setzt einen Teil der Implementierung um.
36. Diese Zeile ist absichtlich leer.
37. Diese Zeile ist absichtlich leer.
38. Diese Zeile definiert einen Dekorator fuer den folgenden Block.
39. Diese Zeile definiert einen Dekorator fuer den folgenden Block.
40. Diese Zeile definiert einen Dekorator fuer den folgenden Block.
41. Diese Zeile startet eine Funktionsdefinition.
42. Diese Zeile setzt einen Teil der Implementierung um.
43. Diese Zeile setzt einen Teil der Implementierung um.
44. Diese Zeile setzt einen Teil der Implementierung um.
45. Diese Zeile setzt einen Teil der Implementierung um.
46. Diese Zeile setzt einen Teil der Implementierung um.
47. Diese Zeile setzt einen Teil der Implementierung um.
48. Diese Zeile setzt einen Teil der Implementierung um.
49. Diese Zeile setzt einen Teil der Implementierung um.
50. Diese Zeile steuert den bedingten Ablauf.
51. Diese Zeile setzt einen Teil der Implementierung um.
52. Diese Zeile setzt einen Teil der Implementierung um.
53. Diese Zeile setzt einen Teil der Implementierung um.
54. Diese Zeile setzt einen Teil der Implementierung um.
55. Diese Zeile setzt einen Teil der Implementierung um.
56. Diese Zeile setzt einen Teil der Implementierung um.
57. Diese Zeile setzt einen Teil der Implementierung um.
58. Diese Zeile setzt einen Teil der Implementierung um.
59. Diese Zeile setzt einen Teil der Implementierung um.
60. Diese Zeile setzt einen Teil der Implementierung um.
61. Diese Zeile ist absichtlich leer.
62. Diese Zeile ist absichtlich leer.
63. Diese Zeile definiert einen Dekorator fuer den folgenden Block.
64. Diese Zeile definiert einen Dekorator fuer den folgenden Block.
65. Diese Zeile startet eine Funktionsdefinition.
66. Diese Zeile steuert den bedingten Ablauf.
67. Diese Zeile setzt einen Teil der Implementierung um.
68. Diese Zeile setzt einen Teil der Implementierung um.
69. Diese Zeile ist absichtlich leer.
70. Diese Zeile ist absichtlich leer.
71. Diese Zeile definiert einen Dekorator fuer den folgenden Block.
72. Diese Zeile definiert einen Dekorator fuer den folgenden Block.
73. Diese Zeile definiert einen Dekorator fuer den folgenden Block.
74. Diese Zeile startet eine Funktionsdefinition.
75. Diese Zeile setzt einen Teil der Implementierung um.
76. Diese Zeile setzt einen Teil der Implementierung um.
77. Diese Zeile setzt einen Teil der Implementierung um.
78. Diese Zeile setzt einen Teil der Implementierung um.
79. Diese Zeile setzt einen Teil der Implementierung um.
80. Diese Zeile setzt einen Teil der Implementierung um.
81. Diese Zeile setzt einen Teil der Implementierung um.
82. Diese Zeile setzt einen Teil der Implementierung um.
83. Diese Zeile setzt einen Teil der Implementierung um.
84. Diese Zeile steuert den bedingten Ablauf.
85. Diese Zeile setzt einen Teil der Implementierung um.
86. Diese Zeile setzt einen Teil der Implementierung um.
87. Diese Zeile setzt einen Teil der Implementierung um.
88. Diese Zeile setzt einen Teil der Implementierung um.
89. Diese Zeile setzt einen Teil der Implementierung um.
90. Diese Zeile setzt einen Teil der Implementierung um.
91. Diese Zeile steuert den bedingten Ablauf.
92. Diese Zeile setzt einen Teil der Implementierung um.
93. Diese Zeile setzt einen Teil der Implementierung um.
94. Diese Zeile setzt einen Teil der Implementierung um.
95. Diese Zeile setzt einen Teil der Implementierung um.
96. Diese Zeile setzt einen Teil der Implementierung um.
97. Diese Zeile setzt einen Teil der Implementierung um.
98. Diese Zeile setzt einen Teil der Implementierung um.
99. Diese Zeile setzt einen Teil der Implementierung um.
100. Diese Zeile setzt einen Teil der Implementierung um.
101. Diese Zeile setzt einen Teil der Implementierung um.
102. Diese Zeile setzt einen Teil der Implementierung um.
103. Diese Zeile setzt einen Teil der Implementierung um.
104. Diese Zeile ist absichtlich leer.
105. Diese Zeile ist absichtlich leer.
106. Diese Zeile definiert einen Dekorator fuer den folgenden Block.
107. Diese Zeile startet eine Funktionsdefinition.
108. Diese Zeile setzt einen Teil der Implementierung um.
109. Diese Zeile setzt einen Teil der Implementierung um.
110. Diese Zeile setzt einen Teil der Implementierung um.
111. Diese Zeile ist absichtlich leer.
112. Diese Zeile ist absichtlich leer.
113. Diese Zeile definiert einen Dekorator fuer den folgenden Block.
114. Diese Zeile startet eine Funktionsdefinition.
115. Diese Zeile setzt einen Teil der Implementierung um.
116. Diese Zeile ist absichtlich leer.
117. Diese Zeile ist absichtlich leer.
118. Diese Zeile definiert einen Dekorator fuer den folgenden Block.
119. Diese Zeile startet eine Funktionsdefinition.
120. Diese Zeile setzt einen Teil der Implementierung um.
121. Diese Zeile setzt einen Teil der Implementierung um.
122. Diese Zeile setzt einen Teil der Implementierung um.
123. Diese Zeile setzt einen Teil der Implementierung um.
124. Diese Zeile setzt einen Teil der Implementierung um.
125. Diese Zeile setzt einen Teil der Implementierung um.
126. Diese Zeile ist absichtlich leer.
127. Diese Zeile ist absichtlich leer.
128. Diese Zeile definiert einen Dekorator fuer den folgenden Block.
129. Diese Zeile startet eine Funktionsdefinition.
130. Diese Zeile steuert den bedingten Ablauf.
131. Diese Zeile setzt einen Teil der Implementierung um.
132. Diese Zeile setzt einen Teil der Implementierung um.

## app/routers/admin.py
```python
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, Response, UploadFile, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.config import get_settings
from app.database import get_db
from app.dependencies import get_admin_user, template_context
from app.i18n import t
from app.models import Recipe, User
from app.rate_limit import key_by_user_or_ip, limiter
from app.services import import_kochwiki_csv, is_meta_true, set_meta_value
from app.views import redirect, templates

router = APIRouter(tags=["admin"])
settings = get_settings()


def admin_dashboard_context(
    request: Request,
    db: Session,
    current_user: User,
    report=None,
    error: str | None = None,
    message: str | None = None,
):
    users = db.scalars(select(User).order_by(User.created_at.desc())).all()
    recipes = db.scalars(
        select(Recipe).order_by(Recipe.created_at.desc()).options(selectinload(Recipe.creator))
    ).all()
    return template_context(
        request,
        current_user,
        users=users,
        recipes=recipes,
        report=report,
        error=error,
        message=message,
        seed_done=is_meta_true(db, "kochwiki_seed_done"),
        default_csv_path=settings.kochwiki_csv_path,
    )


@router.get("/admin")
def admin_panel(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    return templates.TemplateResponse("admin.html", admin_dashboard_context(request, db, current_user))


@router.post("/admin/users/{user_id}/role")
def change_user_role(
    user_id: int,
    role: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    if role not in {"user", "admin"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=t("error.role_invalid"))
    user = db.scalar(select(User).where(User.id == user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=t("error.user_not_found"))
    user.role = role
    db.commit()
    return redirect("/admin")


@router.post("/admin/recipes/{recipe_id}/delete")
def delete_recipe_admin(
    recipe_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    recipe = db.scalar(select(Recipe).where(Recipe.id == recipe_id))
    if not recipe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=t("error.recipe_not_found"))
    db.delete(recipe)
    db.commit()
    return redirect("/admin")


@router.post("/admin/run-kochwiki-seed")
def run_kochwiki_seed(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    if is_meta_true(db, "kochwiki_seed_done"):
        return templates.TemplateResponse(
            "admin.html",
            admin_dashboard_context(request, db, current_user, error=t("error.seed_already_done")),
            status_code=status.HTTP_409_CONFLICT,
        )
    recipes_count = db.scalar(select(func.count()).select_from(Recipe)) or 0
    if recipes_count > 0:
        return templates.TemplateResponse(
            "admin.html",
            admin_dashboard_context(
                request,
                db,
                current_user,
                error=t("error.seed_not_empty"),
            ),
            status_code=status.HTTP_409_CONFLICT,
        )
    seed_path = Path(settings.kochwiki_csv_path)
    if not seed_path.exists():
        return templates.TemplateResponse(
            "admin.html",
            admin_dashboard_context(
                request,
                db,
                current_user,
                error=f"{t('error.csv_not_found_prefix')}: {seed_path}",
            ),
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    report = import_kochwiki_csv(db, seed_path, current_user.id, mode="insert_only")
    if report.errors:
        return templates.TemplateResponse(
            "admin.html",
            admin_dashboard_context(
                request,
                db,
                current_user,
                report=report,
                error=t("error.seed_finished_errors"),
            ),
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    set_meta_value(db, "kochwiki_seed_done", "1")
    db.commit()
    return templates.TemplateResponse(
        "admin.html",
        admin_dashboard_context(
            request,
            db,
            current_user,
            report=report,
            message=t("error.seed_success"),
        ),
    )


@router.post("/admin/import-recipes")
@limiter.limit("2/minute", key_func=key_by_user_or_ip)
async def import_recipes_admin(
    request: Request,
    response: Response,
    file: UploadFile | None = File(None),
    insert_only: str | None = Form("on"),
    update_existing: str | None = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    _ = response
    max_bytes = settings.max_csv_upload_mb * 1024 * 1024
    mode = "insert_only"
    if update_existing:
        mode = "update_existing"
    elif not insert_only:
        mode = "insert_only"
    try:
        if not file or not file.filename:
            raise ValueError(t("error.csv_upload_required"))
        if not file.filename.lower().endswith(".csv"):
            raise ValueError(t("error.csv_only"))
        raw_bytes = await file.read(max_bytes + 1)
        if len(raw_bytes) > max_bytes:
            raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail=t("error.csv_too_large"))
        if not raw_bytes:
            raise ValueError(t("error.csv_empty"))
        report = import_kochwiki_csv(
            db,
            raw_bytes,
            current_user.id,
            mode=mode,
            autocommit=False,
        )
        db.commit()
        message = t("error.import_finished_insert")
        if mode == "update_existing":
            message = t("error.import_finished_update")
        return templates.TemplateResponse(
            "admin.html",
            admin_dashboard_context(request, db, current_user, report=report, message=message),
        )
    except (FileNotFoundError, ValueError) as exc:
        db.rollback()
        return templates.TemplateResponse(
            "admin.html",
            admin_dashboard_context(request, db, current_user, error=str(exc)),
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    except Exception:
        db.rollback()
        raise
```
ZEILEN-ERKL?RUNG
1. Diese Zeile importiert benoetigte Abhaengigkeiten.
2. Diese Zeile ist absichtlich leer.
3. Diese Zeile importiert benoetigte Abhaengigkeiten.
4. Diese Zeile importiert benoetigte Abhaengigkeiten.
5. Diese Zeile importiert benoetigte Abhaengigkeiten.
6. Diese Zeile ist absichtlich leer.
7. Diese Zeile importiert benoetigte Abhaengigkeiten.
8. Diese Zeile importiert benoetigte Abhaengigkeiten.
9. Diese Zeile importiert benoetigte Abhaengigkeiten.
10. Diese Zeile importiert benoetigte Abhaengigkeiten.
11. Diese Zeile importiert benoetigte Abhaengigkeiten.
12. Diese Zeile importiert benoetigte Abhaengigkeiten.
13. Diese Zeile importiert benoetigte Abhaengigkeiten.
14. Diese Zeile importiert benoetigte Abhaengigkeiten.
15. Diese Zeile ist absichtlich leer.
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
43. Diese Zeile ist absichtlich leer.
44. Diese Zeile ist absichtlich leer.
45. Diese Zeile definiert einen Dekorator fuer den folgenden Block.
46. Diese Zeile startet eine Funktionsdefinition.
47. Diese Zeile setzt einen Teil der Implementierung um.
48. Diese Zeile setzt einen Teil der Implementierung um.
49. Diese Zeile setzt einen Teil der Implementierung um.
50. Diese Zeile setzt einen Teil der Implementierung um.
51. Diese Zeile setzt einen Teil der Implementierung um.
52. Diese Zeile ist absichtlich leer.
53. Diese Zeile ist absichtlich leer.
54. Diese Zeile definiert einen Dekorator fuer den folgenden Block.
55. Diese Zeile startet eine Funktionsdefinition.
56. Diese Zeile setzt einen Teil der Implementierung um.
57. Diese Zeile setzt einen Teil der Implementierung um.
58. Diese Zeile setzt einen Teil der Implementierung um.
59. Diese Zeile setzt einen Teil der Implementierung um.
60. Diese Zeile setzt einen Teil der Implementierung um.
61. Diese Zeile steuert den bedingten Ablauf.
62. Diese Zeile setzt einen Teil der Implementierung um.
63. Diese Zeile setzt einen Teil der Implementierung um.
64. Diese Zeile steuert den bedingten Ablauf.
65. Diese Zeile setzt einen Teil der Implementierung um.
66. Diese Zeile setzt einen Teil der Implementierung um.
67. Diese Zeile setzt einen Teil der Implementierung um.
68. Diese Zeile setzt einen Teil der Implementierung um.
69. Diese Zeile ist absichtlich leer.
70. Diese Zeile ist absichtlich leer.
71. Diese Zeile definiert einen Dekorator fuer den folgenden Block.
72. Diese Zeile startet eine Funktionsdefinition.
73. Diese Zeile setzt einen Teil der Implementierung um.
74. Diese Zeile setzt einen Teil der Implementierung um.
75. Diese Zeile setzt einen Teil der Implementierung um.
76. Diese Zeile setzt einen Teil der Implementierung um.
77. Diese Zeile setzt einen Teil der Implementierung um.
78. Diese Zeile steuert den bedingten Ablauf.
79. Diese Zeile setzt einen Teil der Implementierung um.
80. Diese Zeile setzt einen Teil der Implementierung um.
81. Diese Zeile setzt einen Teil der Implementierung um.
82. Diese Zeile setzt einen Teil der Implementierung um.
83. Diese Zeile ist absichtlich leer.
84. Diese Zeile ist absichtlich leer.
85. Diese Zeile definiert einen Dekorator fuer den folgenden Block.
86. Diese Zeile startet eine Funktionsdefinition.
87. Diese Zeile setzt einen Teil der Implementierung um.
88. Diese Zeile setzt einen Teil der Implementierung um.
89. Diese Zeile setzt einen Teil der Implementierung um.
90. Diese Zeile setzt einen Teil der Implementierung um.
91. Diese Zeile steuert den bedingten Ablauf.
92. Diese Zeile setzt einen Teil der Implementierung um.
93. Diese Zeile setzt einen Teil der Implementierung um.
94. Diese Zeile setzt einen Teil der Implementierung um.
95. Diese Zeile setzt einen Teil der Implementierung um.
96. Diese Zeile setzt einen Teil der Implementierung um.
97. Diese Zeile setzt einen Teil der Implementierung um.
98. Diese Zeile steuert den bedingten Ablauf.
99. Diese Zeile setzt einen Teil der Implementierung um.
100. Diese Zeile setzt einen Teil der Implementierung um.
101. Diese Zeile setzt einen Teil der Implementierung um.
102. Diese Zeile setzt einen Teil der Implementierung um.
103. Diese Zeile setzt einen Teil der Implementierung um.
104. Diese Zeile setzt einen Teil der Implementierung um.
105. Diese Zeile setzt einen Teil der Implementierung um.
106. Diese Zeile setzt einen Teil der Implementierung um.
107. Diese Zeile setzt einen Teil der Implementierung um.
108. Diese Zeile setzt einen Teil der Implementierung um.
109. Diese Zeile setzt einen Teil der Implementierung um.
110. Diese Zeile steuert den bedingten Ablauf.
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
122. Diese Zeile steuert den bedingten Ablauf.
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
135. Diese Zeile setzt einen Teil der Implementierung um.
136. Diese Zeile setzt einen Teil der Implementierung um.
137. Diese Zeile setzt einen Teil der Implementierung um.
138. Diese Zeile setzt einen Teil der Implementierung um.
139. Diese Zeile setzt einen Teil der Implementierung um.
140. Diese Zeile setzt einen Teil der Implementierung um.
141. Diese Zeile setzt einen Teil der Implementierung um.
142. Diese Zeile setzt einen Teil der Implementierung um.
143. Diese Zeile setzt einen Teil der Implementierung um.
144. Diese Zeile setzt einen Teil der Implementierung um.
145. Diese Zeile setzt einen Teil der Implementierung um.
146. Diese Zeile ist absichtlich leer.
147. Diese Zeile ist absichtlich leer.
148. Diese Zeile definiert einen Dekorator fuer den folgenden Block.
149. Diese Zeile definiert einen Dekorator fuer den folgenden Block.
150. Diese Zeile startet eine Funktionsdefinition.
151. Diese Zeile setzt einen Teil der Implementierung um.
152. Diese Zeile setzt einen Teil der Implementierung um.
153. Diese Zeile setzt einen Teil der Implementierung um.
154. Diese Zeile setzt einen Teil der Implementierung um.
155. Diese Zeile setzt einen Teil der Implementierung um.
156. Diese Zeile setzt einen Teil der Implementierung um.
157. Diese Zeile setzt einen Teil der Implementierung um.
158. Diese Zeile setzt einen Teil der Implementierung um.
159. Diese Zeile setzt einen Teil der Implementierung um.
160. Diese Zeile setzt einen Teil der Implementierung um.
161. Diese Zeile setzt einen Teil der Implementierung um.
162. Diese Zeile steuert den bedingten Ablauf.
163. Diese Zeile setzt einen Teil der Implementierung um.
164. Diese Zeile steuert den bedingten Ablauf.
165. Diese Zeile setzt einen Teil der Implementierung um.
166. Diese Zeile gehoert zur Fehlerbehandlung.
167. Diese Zeile steuert den bedingten Ablauf.
168. Diese Zeile setzt einen Teil der Implementierung um.
169. Diese Zeile steuert den bedingten Ablauf.
170. Diese Zeile setzt einen Teil der Implementierung um.
171. Diese Zeile setzt einen Teil der Implementierung um.
172. Diese Zeile steuert den bedingten Ablauf.
173. Diese Zeile setzt einen Teil der Implementierung um.
174. Diese Zeile steuert den bedingten Ablauf.
175. Diese Zeile setzt einen Teil der Implementierung um.
176. Diese Zeile setzt einen Teil der Implementierung um.
177. Diese Zeile setzt einen Teil der Implementierung um.
178. Diese Zeile setzt einen Teil der Implementierung um.
179. Diese Zeile setzt einen Teil der Implementierung um.
180. Diese Zeile setzt einen Teil der Implementierung um.
181. Diese Zeile setzt einen Teil der Implementierung um.
182. Diese Zeile setzt einen Teil der Implementierung um.
183. Diese Zeile setzt einen Teil der Implementierung um.
184. Diese Zeile setzt einen Teil der Implementierung um.
185. Diese Zeile steuert den bedingten Ablauf.
186. Diese Zeile setzt einen Teil der Implementierung um.
187. Diese Zeile setzt einen Teil der Implementierung um.
188. Diese Zeile setzt einen Teil der Implementierung um.
189. Diese Zeile setzt einen Teil der Implementierung um.
190. Diese Zeile setzt einen Teil der Implementierung um.
191. Diese Zeile gehoert zur Fehlerbehandlung.
192. Diese Zeile setzt einen Teil der Implementierung um.
193. Diese Zeile setzt einen Teil der Implementierung um.
194. Diese Zeile setzt einen Teil der Implementierung um.
195. Diese Zeile setzt einen Teil der Implementierung um.
196. Diese Zeile setzt einen Teil der Implementierung um.
197. Diese Zeile setzt einen Teil der Implementierung um.
198. Diese Zeile gehoert zur Fehlerbehandlung.
199. Diese Zeile setzt einen Teil der Implementierung um.
200. Diese Zeile setzt einen Teil der Implementierung um.

## app/middleware.py
```python
import logging
import secrets
import time
import uuid

from fastapi import Request
from fastapi.responses import PlainTextResponse, RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import get_settings
from app.i18n import t

settings = get_settings()
logger = logging.getLogger("mealmate.request")

SAFE_METHODS = {"GET", "HEAD", "OPTIONS", "TRACE"}
CSRF_EXEMPT_PREFIXES = ("/health", "/healthz", "/static")


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex
        request.state.request_id = request_id
        started = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            logger.exception(
                "request_failed request_id=%s method=%s path=%s",
                request_id,
                request.method,
                request.url.path,
            )
            raise
        duration_ms = (time.perf_counter() - started) * 1000
        response.headers["X-Request-ID"] = request_id
        logger.info(
            "request_complete request_id=%s method=%s path=%s status=%s duration_ms=%.2f",
            request_id,
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )
        return response


class CSRFMiddleware(BaseHTTPMiddleware):
    def _is_exempt(self, path: str) -> bool:
        return path.startswith(CSRF_EXEMPT_PREFIXES)

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        cookie_name = settings.csrf_cookie_name
        header_name = settings.csrf_header_name
        csrf_cookie = request.cookies.get(cookie_name)
        if request.method in SAFE_METHODS:
            request.state.csrf_token = csrf_cookie or secrets.token_urlsafe(32)
        elif not self._is_exempt(path):
            provided = request.headers.get(header_name)
            if not provided:
                content_type = (request.headers.get("content-type") or "").lower()
                if "application/x-www-form-urlencoded" in content_type or "multipart/form-data" in content_type:
                    try:
                        form = await request.form()
                    except Exception:
                        form = None
                    if form is not None:
                        provided = str(form.get("csrf_token") or "")
            if not csrf_cookie or not provided or not secrets.compare_digest(provided, csrf_cookie):
                return PlainTextResponse(t("error.csrf_failed"), status_code=403)
            request.state.csrf_token = csrf_cookie
        response = await call_next(request)
        if request.method in SAFE_METHODS and not self._is_exempt(path):
            token = getattr(request.state, "csrf_token", None) or secrets.token_urlsafe(32)
            response.set_cookie(
                key=cookie_name,
                value=token,
                httponly=False,
                secure=settings.resolved_cookie_secure,
                samesite="lax",
                max_age=60 * 60 * 24,
                path="/",
            )
        return response


class HTTPSRedirectMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if settings.prod_mode and settings.resolved_force_https and request.url.scheme != "https":
            target_url = request.url.replace(scheme="https")
            return RedirectResponse(url=str(target_url), status_code=307)
        return await call_next(request)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault("Permissions-Policy", "geolocation=(), microphone=(), camera=()")
        csp_parts = [
            "default-src 'self'",
            "img-src 'self' data: https:",
            "style-src 'self'",
            "script-src 'self'",
            "object-src 'none'",
            "base-uri 'self'",
            "frame-ancestors 'none'",
        ]
        response.headers.setdefault("Content-Security-Policy", "; ".join(csp_parts))
        if settings.prod_mode and request.url.scheme == "https":
            response.headers.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
        return response
```
ZEILEN-ERKL?RUNG
1. Diese Zeile importiert benoetigte Abhaengigkeiten.
2. Diese Zeile importiert benoetigte Abhaengigkeiten.
3. Diese Zeile importiert benoetigte Abhaengigkeiten.
4. Diese Zeile importiert benoetigte Abhaengigkeiten.
5. Diese Zeile ist absichtlich leer.
6. Diese Zeile importiert benoetigte Abhaengigkeiten.
7. Diese Zeile importiert benoetigte Abhaengigkeiten.
8. Diese Zeile importiert benoetigte Abhaengigkeiten.
9. Diese Zeile ist absichtlich leer.
10. Diese Zeile importiert benoetigte Abhaengigkeiten.
11. Diese Zeile importiert benoetigte Abhaengigkeiten.
12. Diese Zeile ist absichtlich leer.
13. Diese Zeile setzt einen Teil der Implementierung um.
14. Diese Zeile setzt einen Teil der Implementierung um.
15. Diese Zeile ist absichtlich leer.
16. Diese Zeile setzt einen Teil der Implementierung um.
17. Diese Zeile setzt einen Teil der Implementierung um.
18. Diese Zeile ist absichtlich leer.
19. Diese Zeile ist absichtlich leer.
20. Diese Zeile startet eine Klassendefinition.
21. Diese Zeile startet eine Funktionsdefinition.
22. Diese Zeile setzt einen Teil der Implementierung um.
23. Diese Zeile setzt einen Teil der Implementierung um.
24. Diese Zeile setzt einen Teil der Implementierung um.
25. Diese Zeile gehoert zur Fehlerbehandlung.
26. Diese Zeile setzt einen Teil der Implementierung um.
27. Diese Zeile gehoert zur Fehlerbehandlung.
28. Diese Zeile setzt einen Teil der Implementierung um.
29. Diese Zeile setzt einen Teil der Implementierung um.
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
47. Diese Zeile ist absichtlich leer.
48. Diese Zeile startet eine Klassendefinition.
49. Diese Zeile startet eine Funktionsdefinition.
50. Diese Zeile setzt einen Teil der Implementierung um.
51. Diese Zeile ist absichtlich leer.
52. Diese Zeile startet eine Funktionsdefinition.
53. Diese Zeile setzt einen Teil der Implementierung um.
54. Diese Zeile setzt einen Teil der Implementierung um.
55. Diese Zeile setzt einen Teil der Implementierung um.
56. Diese Zeile setzt einen Teil der Implementierung um.
57. Diese Zeile steuert den bedingten Ablauf.
58. Diese Zeile setzt einen Teil der Implementierung um.
59. Diese Zeile steuert den bedingten Ablauf.
60. Diese Zeile setzt einen Teil der Implementierung um.
61. Diese Zeile steuert den bedingten Ablauf.
62. Diese Zeile setzt einen Teil der Implementierung um.
63. Diese Zeile steuert den bedingten Ablauf.
64. Diese Zeile gehoert zur Fehlerbehandlung.
65. Diese Zeile setzt einen Teil der Implementierung um.
66. Diese Zeile gehoert zur Fehlerbehandlung.
67. Diese Zeile setzt einen Teil der Implementierung um.
68. Diese Zeile steuert den bedingten Ablauf.
69. Diese Zeile setzt einen Teil der Implementierung um.
70. Diese Zeile steuert den bedingten Ablauf.
71. Diese Zeile setzt einen Teil der Implementierung um.
72. Diese Zeile setzt einen Teil der Implementierung um.
73. Diese Zeile setzt einen Teil der Implementierung um.
74. Diese Zeile steuert den bedingten Ablauf.
75. Diese Zeile setzt einen Teil der Implementierung um.
76. Diese Zeile setzt einen Teil der Implementierung um.
77. Diese Zeile setzt einen Teil der Implementierung um.
78. Diese Zeile setzt einen Teil der Implementierung um.
79. Diese Zeile setzt einen Teil der Implementierung um.
80. Diese Zeile setzt einen Teil der Implementierung um.
81. Diese Zeile setzt einen Teil der Implementierung um.
82. Diese Zeile setzt einen Teil der Implementierung um.
83. Diese Zeile setzt einen Teil der Implementierung um.
84. Diese Zeile setzt einen Teil der Implementierung um.
85. Diese Zeile setzt einen Teil der Implementierung um.
86. Diese Zeile ist absichtlich leer.
87. Diese Zeile ist absichtlich leer.
88. Diese Zeile startet eine Klassendefinition.
89. Diese Zeile startet eine Funktionsdefinition.
90. Diese Zeile steuert den bedingten Ablauf.
91. Diese Zeile setzt einen Teil der Implementierung um.
92. Diese Zeile setzt einen Teil der Implementierung um.
93. Diese Zeile setzt einen Teil der Implementierung um.
94. Diese Zeile ist absichtlich leer.
95. Diese Zeile ist absichtlich leer.
96. Diese Zeile startet eine Klassendefinition.
97. Diese Zeile startet eine Funktionsdefinition.
98. Diese Zeile setzt einen Teil der Implementierung um.
99. Diese Zeile setzt einen Teil der Implementierung um.
100. Diese Zeile setzt einen Teil der Implementierung um.
101. Diese Zeile setzt einen Teil der Implementierung um.
102. Diese Zeile setzt einen Teil der Implementierung um.
103. Diese Zeile setzt einen Teil der Implementierung um.
104. Diese Zeile setzt einen Teil der Implementierung um.
105. Diese Zeile setzt einen Teil der Implementierung um.
106. Diese Zeile setzt einen Teil der Implementierung um.
107. Diese Zeile setzt einen Teil der Implementierung um.
108. Diese Zeile setzt einen Teil der Implementierung um.
109. Diese Zeile setzt einen Teil der Implementierung um.
110. Diese Zeile setzt einen Teil der Implementierung um.
111. Diese Zeile setzt einen Teil der Implementierung um.
112. Diese Zeile setzt einen Teil der Implementierung um.
113. Diese Zeile steuert den bedingten Ablauf.
114. Diese Zeile setzt einen Teil der Implementierung um.
115. Diese Zeile setzt einen Teil der Implementierung um.

## app/image_utils.py
```python
import io
from pathlib import Path
from uuid import uuid4

from PIL import Image, UnidentifiedImageError

from app.config import get_settings
from app.i18n import t

settings = get_settings()

MAGIC_SIGNATURES = {
    "image/jpeg": [b"\xff\xd8\xff"],
    "image/png": [b"\x89PNG\r\n\x1a\n"],
    "image/webp": [b"RIFF"],
}


class ImageValidationError(ValueError):
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.status_code = status_code


def _validate_magic_bytes(content_type: str, file_bytes: bytes) -> None:
    signatures = MAGIC_SIGNATURES.get(content_type, [])
    if not signatures:
        raise ImageValidationError(t("error.mime_unsupported", content_type=content_type))
    if content_type == "image/webp":
        if not (file_bytes.startswith(b"RIFF") and file_bytes[8:12] == b"WEBP"):
            raise ImageValidationError(t("error.webp_signature"))
        return
    if not any(file_bytes.startswith(sig) for sig in signatures):
        raise ImageValidationError(t("error.magic_mismatch"))


def _validate_image_decode(content_type: str, file_bytes: bytes) -> None:
    expected_format = {
        "image/jpeg": "JPEG",
        "image/png": "PNG",
        "image/webp": "WEBP",
    }.get(content_type)
    try:
        with Image.open(io.BytesIO(file_bytes)) as image:
            image.verify()
            actual_format = (image.format or "").upper()
    except (UnidentifiedImageError, OSError) as exc:
        raise ImageValidationError(t("error.image_invalid")) from exc
    if expected_format and actual_format != expected_format:
        raise ImageValidationError(t("error.image_format_mismatch"))


def safe_image_filename(original_filename: str, content_type: str) -> str:
    extension = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
    }.get(content_type, "")
    clean_name = Path(original_filename or "").name
    if not extension:
        extension = Path(clean_name).suffix.lower()
    return f"{uuid4().hex}{extension[:10]}"


def validate_image_upload(content_type: str, file_bytes: bytes) -> None:
    if content_type not in settings.allowed_image_types:
        raise ImageValidationError(t("error.mime_unsupported", content_type=content_type))
    max_bytes = settings.max_upload_mb * 1024 * 1024
    if len(file_bytes) > max_bytes:
        raise ImageValidationError(t("error.image_too_large", max_mb=settings.max_upload_mb), status_code=413)
    if len(file_bytes) < 12:
        raise ImageValidationError(t("error.image_too_small"))
    _validate_magic_bytes(content_type, file_bytes)
    _validate_image_decode(content_type, file_bytes)
```
ZEILEN-ERKL?RUNG
1. Diese Zeile importiert benoetigte Abhaengigkeiten.
2. Diese Zeile importiert benoetigte Abhaengigkeiten.
3. Diese Zeile importiert benoetigte Abhaengigkeiten.
4. Diese Zeile ist absichtlich leer.
5. Diese Zeile importiert benoetigte Abhaengigkeiten.
6. Diese Zeile ist absichtlich leer.
7. Diese Zeile importiert benoetigte Abhaengigkeiten.
8. Diese Zeile importiert benoetigte Abhaengigkeiten.
9. Diese Zeile ist absichtlich leer.
10. Diese Zeile setzt einen Teil der Implementierung um.
11. Diese Zeile ist absichtlich leer.
12. Diese Zeile setzt einen Teil der Implementierung um.
13. Diese Zeile setzt einen Teil der Implementierung um.
14. Diese Zeile setzt einen Teil der Implementierung um.
15. Diese Zeile setzt einen Teil der Implementierung um.
16. Diese Zeile setzt einen Teil der Implementierung um.
17. Diese Zeile ist absichtlich leer.
18. Diese Zeile ist absichtlich leer.
19. Diese Zeile startet eine Klassendefinition.
20. Diese Zeile startet eine Funktionsdefinition.
21. Diese Zeile setzt einen Teil der Implementierung um.
22. Diese Zeile setzt einen Teil der Implementierung um.
23. Diese Zeile ist absichtlich leer.
24. Diese Zeile ist absichtlich leer.
25. Diese Zeile startet eine Funktionsdefinition.
26. Diese Zeile setzt einen Teil der Implementierung um.
27. Diese Zeile steuert den bedingten Ablauf.
28. Diese Zeile setzt einen Teil der Implementierung um.
29. Diese Zeile steuert den bedingten Ablauf.
30. Diese Zeile steuert den bedingten Ablauf.
31. Diese Zeile setzt einen Teil der Implementierung um.
32. Diese Zeile setzt einen Teil der Implementierung um.
33. Diese Zeile steuert den bedingten Ablauf.
34. Diese Zeile setzt einen Teil der Implementierung um.
35. Diese Zeile ist absichtlich leer.
36. Diese Zeile ist absichtlich leer.
37. Diese Zeile startet eine Funktionsdefinition.
38. Diese Zeile setzt einen Teil der Implementierung um.
39. Diese Zeile setzt einen Teil der Implementierung um.
40. Diese Zeile setzt einen Teil der Implementierung um.
41. Diese Zeile setzt einen Teil der Implementierung um.
42. Diese Zeile setzt einen Teil der Implementierung um.
43. Diese Zeile gehoert zur Fehlerbehandlung.
44. Diese Zeile setzt einen Teil der Implementierung um.
45. Diese Zeile setzt einen Teil der Implementierung um.
46. Diese Zeile setzt einen Teil der Implementierung um.
47. Diese Zeile gehoert zur Fehlerbehandlung.
48. Diese Zeile setzt einen Teil der Implementierung um.
49. Diese Zeile steuert den bedingten Ablauf.
50. Diese Zeile setzt einen Teil der Implementierung um.
51. Diese Zeile ist absichtlich leer.
52. Diese Zeile ist absichtlich leer.
53. Diese Zeile startet eine Funktionsdefinition.
54. Diese Zeile setzt einen Teil der Implementierung um.
55. Diese Zeile setzt einen Teil der Implementierung um.
56. Diese Zeile setzt einen Teil der Implementierung um.
57. Diese Zeile setzt einen Teil der Implementierung um.
58. Diese Zeile setzt einen Teil der Implementierung um.
59. Diese Zeile setzt einen Teil der Implementierung um.
60. Diese Zeile steuert den bedingten Ablauf.
61. Diese Zeile setzt einen Teil der Implementierung um.
62. Diese Zeile setzt einen Teil der Implementierung um.
63. Diese Zeile ist absichtlich leer.
64. Diese Zeile ist absichtlich leer.
65. Diese Zeile startet eine Funktionsdefinition.
66. Diese Zeile steuert den bedingten Ablauf.
67. Diese Zeile setzt einen Teil der Implementierung um.
68. Diese Zeile setzt einen Teil der Implementierung um.
69. Diese Zeile steuert den bedingten Ablauf.
70. Diese Zeile setzt einen Teil der Implementierung um.
71. Diese Zeile steuert den bedingten Ablauf.
72. Diese Zeile setzt einen Teil der Implementierung um.
73. Diese Zeile setzt einen Teil der Implementierung um.
74. Diese Zeile setzt einen Teil der Implementierung um.

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
from app.routers import admin, auth, recipes
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
ZEILEN-ERKL?RUNG
1. Diese Zeile importiert benoetigte Abhaengigkeiten.
2. Diese Zeile importiert benoetigte Abhaengigkeiten.
3. Diese Zeile importiert benoetigte Abhaengigkeiten.
4. Diese Zeile ist absichtlich leer.
5. Diese Zeile importiert benoetigte Abhaengigkeiten.
6. Diese Zeile importiert benoetigte Abhaengigkeiten.
7. Diese Zeile importiert benoetigte Abhaengigkeiten.
8. Diese Zeile importiert benoetigte Abhaengigkeiten.
9. Diese Zeile importiert benoetigte Abhaengigkeiten.
10. Diese Zeile importiert benoetigte Abhaengigkeiten.
11. Diese Zeile importiert benoetigte Abhaengigkeiten.
12. Diese Zeile importiert benoetigte Abhaengigkeiten.
13. Diese Zeile importiert benoetigte Abhaengigkeiten.
14. Diese Zeile importiert benoetigte Abhaengigkeiten.
15. Diese Zeile ist absichtlich leer.
16. Diese Zeile importiert benoetigte Abhaengigkeiten.
17. Diese Zeile importiert benoetigte Abhaengigkeiten.
18. Diese Zeile importiert benoetigte Abhaengigkeiten.
19. Diese Zeile importiert benoetigte Abhaengigkeiten.
20. Diese Zeile importiert benoetigte Abhaengigkeiten.
21. Diese Zeile importiert benoetigte Abhaengigkeiten.
22. Diese Zeile importiert benoetigte Abhaengigkeiten.
23. Diese Zeile importiert benoetigte Abhaengigkeiten.
24. Diese Zeile importiert benoetigte Abhaengigkeiten.
25. Diese Zeile importiert benoetigte Abhaengigkeiten.
26. Diese Zeile importiert benoetigte Abhaengigkeiten.
27. Diese Zeile importiert benoetigte Abhaengigkeiten.
28. Diese Zeile ist absichtlich leer.
29. Diese Zeile setzt einen Teil der Implementierung um.
30. Diese Zeile setzt einen Teil der Implementierung um.
31. Diese Zeile setzt einen Teil der Implementierung um.
32. Diese Zeile ist absichtlich leer.
33. Diese Zeile setzt einen Teil der Implementierung um.
34. Diese Zeile ist absichtlich leer.
35. Diese Zeile ist absichtlich leer.
36. Diese Zeile startet eine Klassendefinition.
37. Diese Zeile startet eine Funktionsdefinition.
38. Diese Zeile setzt einen Teil der Implementierung um.
39. Diese Zeile setzt einen Teil der Implementierung um.
40. Diese Zeile ist absichtlich leer.
41. Diese Zeile startet eine Funktionsdefinition.
42. Diese Zeile setzt einen Teil der Implementierung um.
43. Diese Zeile steuert den bedingten Ablauf.
44. Diese Zeile setzt einen Teil der Implementierung um.
45. Diese Zeile setzt einen Teil der Implementierung um.
46. Diese Zeile ist absichtlich leer.
47. Diese Zeile ist absichtlich leer.
48. Diese Zeile setzt einen Teil der Implementierung um.
49. Diese Zeile setzt einen Teil der Implementierung um.
50. Diese Zeile setzt einen Teil der Implementierung um.
51. Diese Zeile steuert den bedingten Ablauf.
52. Diese Zeile setzt einen Teil der Implementierung um.
53. Diese Zeile setzt einen Teil der Implementierung um.
54. Diese Zeile setzt einen Teil der Implementierung um.
55. Diese Zeile setzt einen Teil der Implementierung um.
56. Diese Zeile setzt einen Teil der Implementierung um.
57. Diese Zeile setzt einen Teil der Implementierung um.
58. Diese Zeile ist absichtlich leer.
59. Diese Zeile setzt einen Teil der Implementierung um.
60. Diese Zeile setzt einen Teil der Implementierung um.
61. Diese Zeile setzt einen Teil der Implementierung um.
62. Diese Zeile setzt einen Teil der Implementierung um.
63. Diese Zeile ist absichtlich leer.
64. Diese Zeile setzt einen Teil der Implementierung um.
65. Diese Zeile setzt einen Teil der Implementierung um.
66. Diese Zeile setzt einen Teil der Implementierung um.
67. Diese Zeile ist absichtlich leer.
68. Diese Zeile ist absichtlich leer.
69. Diese Zeile definiert einen Dekorator fuer den folgenden Block.
70. Diese Zeile startet eine Funktionsdefinition.
71. Diese Zeile setzt einen Teil der Implementierung um.
72. Diese Zeile steuert den bedingten Ablauf.
73. Diese Zeile setzt einen Teil der Implementierung um.
74. Diese Zeile setzt einen Teil der Implementierung um.
75. Diese Zeile setzt einen Teil der Implementierung um.
76. Diese Zeile setzt einen Teil der Implementierung um.
77. Diese Zeile setzt einen Teil der Implementierung um.
78. Diese Zeile setzt einen Teil der Implementierung um.
79. Diese Zeile setzt einen Teil der Implementierung um.
80. Diese Zeile ist absichtlich leer.
81. Diese Zeile ist absichtlich leer.
82. Diese Zeile definiert einen Dekorator fuer den folgenden Block.
83. Diese Zeile startet eine Funktionsdefinition.
84. Diese Zeile setzt einen Teil der Implementierung um.
85. Diese Zeile setzt einen Teil der Implementierung um.
86. Diese Zeile setzt einen Teil der Implementierung um.
87. Diese Zeile steuert den bedingten Ablauf.
88. Diese Zeile steuert den bedingten Ablauf.
89. Diese Zeile setzt einen Teil der Implementierung um.
90. Diese Zeile setzt einen Teil der Implementierung um.
91. Diese Zeile setzt einen Teil der Implementierung um.
92. Diese Zeile setzt einen Teil der Implementierung um.
93. Diese Zeile setzt einen Teil der Implementierung um.
94. Diese Zeile setzt einen Teil der Implementierung um.
95. Diese Zeile setzt einen Teil der Implementierung um.
96. Diese Zeile steuert den bedingten Ablauf.
97. Diese Zeile setzt einen Teil der Implementierung um.
98. Diese Zeile setzt einen Teil der Implementierung um.
99. Diese Zeile setzt einen Teil der Implementierung um.
100. Diese Zeile setzt einen Teil der Implementierung um.
101. Diese Zeile setzt einen Teil der Implementierung um.
102. Diese Zeile setzt einen Teil der Implementierung um.
103. Diese Zeile ist absichtlich leer.
104. Diese Zeile ist absichtlich leer.
105. Diese Zeile startet eine Funktionsdefinition.
106. Diese Zeile setzt einen Teil der Implementierung um.
107. Diese Zeile steuert den bedingten Ablauf.
108. Diese Zeile setzt einen Teil der Implementierung um.
109. Diese Zeile setzt einen Teil der Implementierung um.
110. Diese Zeile setzt einen Teil der Implementierung um.
111. Diese Zeile steuert den bedingten Ablauf.
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
125. Diese Zeile ist absichtlich leer.
126. Diese Zeile ist absichtlich leer.
127. Diese Zeile startet eine Funktionsdefinition.
128. Diese Zeile steuert den bedingten Ablauf.
129. Diese Zeile setzt einen Teil der Implementierung um.
130. Diese Zeile setzt einen Teil der Implementierung um.
131. Diese Zeile gehoert zur Fehlerbehandlung.
132. Diese Zeile steuert den bedingten Ablauf.
133. Diese Zeile setzt einen Teil der Implementierung um.
134. Diese Zeile setzt einen Teil der Implementierung um.
135. Diese Zeile steuert den bedingten Ablauf.
136. Diese Zeile setzt einen Teil der Implementierung um.
137. Diese Zeile setzt einen Teil der Implementierung um.
138. Diese Zeile steuert den bedingten Ablauf.
139. Diese Zeile setzt einen Teil der Implementierung um.
140. Diese Zeile setzt einen Teil der Implementierung um.
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
151. Diese Zeile setzt einen Teil der Implementierung um.
152. Diese Zeile setzt einen Teil der Implementierung um.
153. Diese Zeile gehoert zur Fehlerbehandlung.
154. Diese Zeile setzt einen Teil der Implementierung um.
155. Diese Zeile ist absichtlich leer.
156. Diese Zeile ist absichtlich leer.
157. Diese Zeile definiert einen Dekorator fuer den folgenden Block.
158. Diese Zeile startet eine Funktionsdefinition.
159. Diese Zeile setzt einen Teil der Implementierung um.
160. Diese Zeile ist absichtlich leer.
161. Diese Zeile ist absichtlich leer.
162. Diese Zeile definiert einen Dekorator fuer den folgenden Block.
163. Diese Zeile definiert einen Dekorator fuer den folgenden Block.
164. Diese Zeile startet eine Funktionsdefinition.
165. Diese Zeile setzt einen Teil der Implementierung um.

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
      {% if current_user %}
      <a href="/recipes/new">{{ t("nav.create_recipe") }}</a>
      <a href="/my-recipes">{{ t("nav.my_recipes") }}</a>
      <a href="/favorites">{{ t("nav.favorites") }}</a>
      <a href="/me">{{ t("nav.profile") }}</a>
      {% if current_user.role == "admin" %}
      <a href="/admin">{{ t("nav.admin") }}</a>
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
14. Diese Zeile setzt einen Teil der Implementierung um.
15. Diese Zeile setzt einen Teil der Implementierung um.
16. Diese Zeile setzt einen Teil der Implementierung um.
17. Diese Zeile enthaelt Jinja-Template-Logik.
18. Diese Zeile setzt einen Teil der Implementierung um.
19. Diese Zeile setzt einen Teil der Implementierung um.
20. Diese Zeile setzt einen Teil der Implementierung um.
21. Diese Zeile setzt einen Teil der Implementierung um.
22. Diese Zeile enthaelt Jinja-Template-Logik.
23. Diese Zeile setzt einen Teil der Implementierung um.
24. Diese Zeile enthaelt Jinja-Template-Logik.
25. Diese Zeile setzt einen Teil der Implementierung um.
26. Diese Zeile setzt einen Teil der Implementierung um.
27. Diese Zeile setzt einen Teil der Implementierung um.
28. Diese Zeile enthaelt Jinja-Template-Logik.
29. Diese Zeile setzt einen Teil der Implementierung um.
30. Diese Zeile setzt einen Teil der Implementierung um.
31. Diese Zeile enthaelt Jinja-Template-Logik.
32. Diese Zeile setzt einen Teil der Implementierung um.
33. Diese Zeile setzt einen Teil der Implementierung um.
34. Diese Zeile setzt einen Teil der Implementierung um.
35. Diese Zeile enthaelt Jinja-Template-Logik.
36. Diese Zeile setzt einen Teil der Implementierung um.
37. Diese Zeile setzt einen Teil der Implementierung um.
38. Diese Zeile setzt einen Teil der Implementierung um.

## app/templates/home.html
```html
{% extends "base.html" %}
{% block content %}
<section class="panel">
  <h1>{{ t("home.title") }}</h1>
  <form class="grid" hx-get="/" hx-target="#recipe-list" hx-push-url="true">
    <input type="text" name="title" value="{{ title }}" placeholder="{{ t('home.title_contains') }}">
    <input type="text" name="category" value="{{ category }}" placeholder="{{ t('home.category') }}">
    <select name="difficulty">
      <option value="">{{ t("home.difficulty") }}</option>
      <option value="easy" {% if difficulty == "easy" %}selected{% endif %}>{{ t("difficulty.easy") }}</option>
      <option value="medium" {% if difficulty == "medium" %}selected{% endif %}>{{ t("difficulty.medium") }}</option>
      <option value="hard" {% if difficulty == "hard" %}selected{% endif %}>{{ t("difficulty.hard") }}</option>
    </select>
    <input type="text" name="ingredient" value="{{ ingredient }}" placeholder="{{ t('home.ingredient') }}">
    <select name="sort">
      <option value="date" {% if sort == "date" %}selected{% endif %}>{{ t("sort.newest") }}</option>
      <option value="prep_time" {% if sort == "prep_time" %}selected{% endif %}>{{ t("sort.prep_time") }}</option>
      <option value="avg_rating" {% if sort == "avg_rating" %}selected{% endif %}>{{ t("sort.highest_rated") }}</option>
    </select>
    <button type="submit">{{ t("home.apply") }}</button>
  </form>
</section>
<section id="recipe-list">
  {% include "partials/recipe_list.html" %}
</section>
{% endblock %}
```
ZEILEN-ERKL?RUNG
1. Diese Zeile enthaelt Jinja-Template-Logik.
2. Diese Zeile enthaelt Jinja-Template-Logik.
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
24. Diese Zeile enthaelt Jinja-Template-Logik.
25. Diese Zeile setzt einen Teil der Implementierung um.
26. Diese Zeile enthaelt Jinja-Template-Logik.

## app/templates/auth_login.html
```html
{% extends "base.html" %}
{% block content %}
<section class="panel narrow">
  <h1>{{ t("auth.login_title") }}</h1>
  {% if error %}<p class="error">{{ error }}</p>{% endif %}
  <form method="post" action="/login" class="stack">
    <label>{{ t("auth.email") }} <input type="email" name="email" required></label>
    <label>{{ t("auth.password") }} <input type="password" name="password" required></label>
    <button type="submit">{{ t("auth.login_button") }}</button>
  </form>
</section>
{% endblock %}
```
ZEILEN-ERKL?RUNG
1. Diese Zeile enthaelt Jinja-Template-Logik.
2. Diese Zeile enthaelt Jinja-Template-Logik.
3. Diese Zeile setzt einen Teil der Implementierung um.
4. Diese Zeile setzt einen Teil der Implementierung um.
5. Diese Zeile enthaelt Jinja-Template-Logik.
6. Diese Zeile setzt einen Teil der Implementierung um.
7. Diese Zeile setzt einen Teil der Implementierung um.
8. Diese Zeile setzt einen Teil der Implementierung um.
9. Diese Zeile setzt einen Teil der Implementierung um.
10. Diese Zeile setzt einen Teil der Implementierung um.
11. Diese Zeile setzt einen Teil der Implementierung um.
12. Diese Zeile enthaelt Jinja-Template-Logik.

## app/templates/auth_register.html
```html
{% extends "base.html" %}
{% block content %}
<section class="panel narrow">
  <h1>{{ t("auth.register_title") }}</h1>
  {% if error %}<p class="error">{{ error }}</p>{% endif %}
  <form method="post" action="/register" class="stack">
    <label>{{ t("auth.email") }} <input type="email" name="email" required></label>
    <label>{{ t("auth.password") }} <input type="password" name="password" minlength="10" required></label>
    <button type="submit">{{ t("auth.register_button") }}</button>
  </form>
</section>
{% endblock %}
```
ZEILEN-ERKL?RUNG
1. Diese Zeile enthaelt Jinja-Template-Logik.
2. Diese Zeile enthaelt Jinja-Template-Logik.
3. Diese Zeile setzt einen Teil der Implementierung um.
4. Diese Zeile setzt einen Teil der Implementierung um.
5. Diese Zeile enthaelt Jinja-Template-Logik.
6. Diese Zeile setzt einen Teil der Implementierung um.
7. Diese Zeile setzt einen Teil der Implementierung um.
8. Diese Zeile setzt einen Teil der Implementierung um.
9. Diese Zeile setzt einen Teil der Implementierung um.
10. Diese Zeile setzt einen Teil der Implementierung um.
11. Diese Zeile setzt einen Teil der Implementierung um.
12. Diese Zeile enthaelt Jinja-Template-Logik.

## app/templates/recipe_form.html
```html
{% extends "base.html" %}
{% block content %}
<section class="panel">
  <h1>{% if form_mode == "edit" %}{{ t("recipe_form.edit_title") }}{% else %}{{ t("recipe_form.create_title") }}{% endif %}</h1>
  {% if error %}<p class="error">{{ error }}</p>{% endif %}
  <form method="post" enctype="multipart/form-data" class="stack" action="{% if form_mode == 'edit' %}/recipes/{{ recipe.id }}/edit{% else %}/recipes/new{% endif %}">
    <label>{{ t("recipe_form.title") }} <input type="text" name="title" value="{{ recipe.title if recipe else '' }}" required></label>
    <label>{{ t("recipe_form.title_image_url") }} <input type="url" name="title_image_url" value="{{ recipe.title_image_url if recipe else '' }}" placeholder="https://..."></label>
    <label>{{ t("recipe_form.description") }} <textarea name="description" rows="3" required>{{ recipe.description if recipe else '' }}</textarea></label>
    <label>{{ t("recipe_form.instructions") }} <textarea name="instructions" rows="8" required>{{ recipe.instructions if recipe else '' }}</textarea></label>
    <label>{{ t("recipe_form.category") }} <input type="text" name="category" value="{{ recipe.category if recipe else '' }}" required></label>
    <label>{{ t("recipe_form.prep_time") }} <input type="number" min="1" name="prep_time_minutes" value="{{ recipe.prep_time_minutes if recipe else 30 }}" required></label>
    <label>{{ t("recipe_form.difficulty") }}
      <select name="difficulty">
        <option value="easy" {% if recipe and recipe.difficulty == "easy" %}selected{% endif %}>{{ t("difficulty.easy") }}</option>
        <option value="medium" {% if not recipe or recipe.difficulty == "medium" %}selected{% endif %}>{{ t("difficulty.medium") }}</option>
        <option value="hard" {% if recipe and recipe.difficulty == "hard" %}selected{% endif %}>{{ t("difficulty.hard") }}</option>
      </select>
    </label>
    <label>{{ t("recipe_form.ingredients") }}
      <textarea name="ingredients_text" rows="8">{{ ingredients_text if ingredients_text else '' }}</textarea>
    </label>
    <label>{{ t("recipe_form.optional_image") }} <input type="file" name="image" accept="image/png,image/jpeg,image/webp"></label>
    <button type="submit">{% if form_mode == "edit" %}{{ t("recipe_form.save") }}{% else %}{{ t("recipe_form.create") }}{% endif %}</button>
  </form>
</section>
{% endblock %}
```
ZEILEN-ERKL?RUNG
1. Diese Zeile enthaelt Jinja-Template-Logik.
2. Diese Zeile enthaelt Jinja-Template-Logik.
3. Diese Zeile setzt einen Teil der Implementierung um.
4. Diese Zeile setzt einen Teil der Implementierung um.
5. Diese Zeile enthaelt Jinja-Template-Logik.
6. Diese Zeile setzt einen Teil der Implementierung um.
7. Diese Zeile setzt einen Teil der Implementierung um.
8. Diese Zeile setzt einen Teil der Implementierung um.
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
27. Diese Zeile enthaelt Jinja-Template-Logik.

## app/templates/recipe_detail.html
```html
{% extends "base.html" %}
{% block content %}
<article class="panel">
  <h1>{{ recipe.title }}</h1>
  <p>{{ recipe.description }}</p>
  <p class="meta">{{ recipe.category }} | {{ difficulty_label(recipe.difficulty) }} | {{ recipe.prep_time_minutes }} min</p>
  <p class="meta">{{ t("recipe.average_rating") }}: {{ "%.2f"|format(avg_rating) }} ({{ review_count }} {{ t("recipe.review_count_label") }})</p>
  <div class="actions">
    <a href="/recipes/{{ recipe.id }}/pdf" target="_blank">{{ t("recipe.pdf_download") }}</a>
    {% if current_user and (current_user.id == recipe.creator_id or current_user.role == "admin") %}
    <a href="/recipes/{{ recipe.id }}/edit">{{ t("recipe.edit") }}</a>
    <form method="post" action="/recipes/{{ recipe.id }}/delete" class="inline">
      <button type="submit">{{ t("recipe.delete") }}</button>
    </form>
    {% endif %}
  </div>
  <div id="favorite-box">
    {% include "partials/favorite_button.html" %}
  </div>
</article>
{% include "partials/recipe_images.html" %}
<section class="panel">
  <h2>{{ t("recipe.ingredients") }}</h2>
  <ul>
    {% for link in recipe.recipe_ingredients %}
    <li>{{ link.ingredient.name }} {{ link.quantity_text }} {% if link.grams %}({{ link.grams }} g){% endif %}</li>
    {% else %}
    <li>{{ t("recipe.no_ingredients") }}</li>
    {% endfor %}
  </ul>
</section>
<section class="panel">
  <h2>{{ t("recipe.instructions") }}</h2>
  {% for paragraph in recipe.instructions.splitlines() %}
  {% if paragraph.strip() %}<p>{{ paragraph }}</p>{% endif %}
  {% endfor %}
</section>
<section class="panel">
  <h2>{{ t("recipe.reviews") }}</h2>
  {% if current_user %}
  <form method="post" action="/recipes/{{ recipe.id }}/reviews" class="stack">
    <label>{{ t("recipe.rating") }}
      <select name="rating">
        <option value="1">1</option>
        <option value="2">2</option>
        <option value="3">3</option>
        <option value="4">4</option>
        <option value="5" selected>5</option>
      </select>
    </label>
    <label>{{ t("recipe.comment") }} <textarea name="comment" rows="3"></textarea></label>
    <button type="submit">{{ t("recipe.save_review") }}</button>
  </form>
  {% endif %}
  {% for review in recipe.reviews %}
  <article class="card">
    <p><strong>{{ review.user.email }}</strong> {{ t("recipe.rating_short") }} {{ review.rating }}/5</p>
    <p>{{ review.comment }}</p>
    {% if current_user and (current_user.id == review.user_id or current_user.role == "admin") %}
    <form method="post" action="/reviews/{{ review.id }}/delete">
      <button type="submit">{{ t("recipe.delete") }}</button>
    </form>
    {% endif %}
  </article>
  {% else %}
  <p>{{ t("recipe.no_reviews") }}</p>
  {% endfor %}
</section>
{% endblock %}
```
ZEILEN-ERKL?RUNG
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
ZEILEN-ERKL?RUNG
1. Diese Zeile enthaelt Jinja-Template-Logik.
2. Diese Zeile enthaelt Jinja-Template-Logik.
3. Diese Zeile setzt einen Teil der Implementierung um.
4. Diese Zeile setzt einen Teil der Implementierung um.
5. Diese Zeile enthaelt Jinja-Template-Logik.
6. Diese Zeile setzt einen Teil der Implementierung um.
7. Diese Zeile enthaelt Jinja-Template-Logik.
8. Diese Zeile enthaelt Jinja-Template-Logik.
9. Diese Zeile setzt einen Teil der Implementierung um.
10. Diese Zeile enthaelt Jinja-Template-Logik.
11. Diese Zeile setzt einen Teil der Implementierung um.
12. Diese Zeile setzt einen Teil der Implementierung um.
13. Diese Zeile setzt einen Teil der Implementierung um.
14. Diese Zeile setzt einen Teil der Implementierung um.
15. Diese Zeile enthaelt Jinja-Template-Logik.
16. Diese Zeile setzt einen Teil der Implementierung um.
17. Diese Zeile enthaelt Jinja-Template-Logik.
18. Diese Zeile setzt einen Teil der Implementierung um.
19. Diese Zeile setzt einen Teil der Implementierung um.
20. Diese Zeile setzt einen Teil der Implementierung um.
21. Diese Zeile enthaelt Jinja-Template-Logik.
22. Diese Zeile setzt einen Teil der Implementierung um.
23. Diese Zeile setzt einen Teil der Implementierung um.
24. Diese Zeile setzt einen Teil der Implementierung um.
25. Diese Zeile setzt einen Teil der Implementierung um.
26. Diese Zeile setzt einen Teil der Implementierung um.
27. Diese Zeile setzt einen Teil der Implementierung um.
28. Diese Zeile setzt einen Teil der Implementierung um.
29. Diese Zeile setzt einen Teil der Implementierung um.
30. Diese Zeile setzt einen Teil der Implementierung um.
31. Diese Zeile enthaelt Jinja-Template-Logik.
32. Diese Zeile setzt einen Teil der Implementierung um.
33. Diese Zeile setzt einen Teil der Implementierung um.
34. Diese Zeile setzt einen Teil der Implementierung um.
35. Diese Zeile enthaelt Jinja-Template-Logik.
36. Diese Zeile setzt einen Teil der Implementierung um.
37. Diese Zeile setzt einen Teil der Implementierung um.
38. Diese Zeile setzt einen Teil der Implementierung um.
39. Diese Zeile enthaelt Jinja-Template-Logik.
40. Diese Zeile setzt einen Teil der Implementierung um.
41. Diese Zeile enthaelt Jinja-Template-Logik.
42. Diese Zeile enthaelt Jinja-Template-Logik.
43. Diese Zeile enthaelt Jinja-Template-Logik.
44. Diese Zeile enthaelt Jinja-Template-Logik.
45. Diese Zeile setzt einen Teil der Implementierung um.
46. Diese Zeile enthaelt Jinja-Template-Logik.
47. Diese Zeile setzt einen Teil der Implementierung um.
48. Diese Zeile enthaelt Jinja-Template-Logik.
49. Diese Zeile setzt einen Teil der Implementierung um.
50. Diese Zeile enthaelt Jinja-Template-Logik.
51. Diese Zeile setzt einen Teil der Implementierung um.
52. Diese Zeile enthaelt Jinja-Template-Logik.
53. Diese Zeile enthaelt Jinja-Template-Logik.
54. Diese Zeile setzt einen Teil der Implementierung um.
55. Diese Zeile setzt einen Teil der Implementierung um.
56. Diese Zeile setzt einen Teil der Implementierung um.
57. Diese Zeile setzt einen Teil der Implementierung um.
58. Diese Zeile setzt einen Teil der Implementierung um.
59. Diese Zeile setzt einen Teil der Implementierung um.
60. Diese Zeile setzt einen Teil der Implementierung um.
61. Diese Zeile setzt einen Teil der Implementierung um.
62. Diese Zeile enthaelt Jinja-Template-Logik.
63. Diese Zeile setzt einen Teil der Implementierung um.
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
77. Diese Zeile enthaelt Jinja-Template-Logik.
78. Diese Zeile setzt einen Teil der Implementierung um.
79. Diese Zeile setzt einen Teil der Implementierung um.
80. Diese Zeile setzt einen Teil der Implementierung um.
81. Diese Zeile setzt einen Teil der Implementierung um.
82. Diese Zeile setzt einen Teil der Implementierung um.
83. Diese Zeile setzt einen Teil der Implementierung um.
84. Diese Zeile setzt einen Teil der Implementierung um.
85. Diese Zeile setzt einen Teil der Implementierung um.
86. Diese Zeile setzt einen Teil der Implementierung um.
87. Diese Zeile setzt einen Teil der Implementierung um.
88. Diese Zeile enthaelt Jinja-Template-Logik.
89. Diese Zeile setzt einen Teil der Implementierung um.
90. Diese Zeile setzt einen Teil der Implementierung um.
91. Diese Zeile setzt einen Teil der Implementierung um.
92. Diese Zeile setzt einen Teil der Implementierung um.
93. Diese Zeile setzt einen Teil der Implementierung um.
94. Diese Zeile setzt einen Teil der Implementierung um.
95. Diese Zeile setzt einen Teil der Implementierung um.
96. Diese Zeile setzt einen Teil der Implementierung um.
97. Diese Zeile setzt einen Teil der Implementierung um.
98. Diese Zeile setzt einen Teil der Implementierung um.
99. Diese Zeile setzt einen Teil der Implementierung um.
100. Diese Zeile enthaelt Jinja-Template-Logik.
101. Diese Zeile setzt einen Teil der Implementierung um.
102. Diese Zeile setzt einen Teil der Implementierung um.
103. Diese Zeile setzt einen Teil der Implementierung um.
104. Diese Zeile enthaelt Jinja-Template-Logik.

## app/templates/favorites.html
```html
{% extends "base.html" %}
{% block content %}
<section class="panel">
  <h1>{{ t("favorites.title") }}</h1>
  <div class="cards">
    {% for recipe in favorite_recipes %}
    <article class="card">
      {% if recipe.images %}
      <img src="/images/{{ recipe.images[0].id }}" alt="{{ recipe.title }}" class="thumb">
      {% elif recipe.title_image_url %}
      <img src="/external-image?url={{ recipe.title_image_url|urlencode }}" alt="{{ recipe.title }}" class="thumb">
      {% endif %}
      <h3><a href="/recipes/{{ recipe.id }}">{{ recipe.title }}</a></h3>
      <p>{{ recipe.category }} | {{ difficulty_label(recipe.difficulty) }} | {{ recipe.prep_time_minutes }} min</p>
      <form method="post" action="/recipes/{{ recipe.id }}/favorite">
        <button type="submit">{{ t("favorites.remove") }}</button>
      </form>
    </article>
    {% else %}
    <p>{{ t("favorites.empty") }}</p>
    {% endfor %}
  </div>
</section>
{% endblock %}
```
ZEILEN-ERKL?RUNG
1. Diese Zeile enthaelt Jinja-Template-Logik.
2. Diese Zeile enthaelt Jinja-Template-Logik.
3. Diese Zeile setzt einen Teil der Implementierung um.
4. Diese Zeile setzt einen Teil der Implementierung um.
5. Diese Zeile setzt einen Teil der Implementierung um.
6. Diese Zeile enthaelt Jinja-Template-Logik.
7. Diese Zeile setzt einen Teil der Implementierung um.
8. Diese Zeile enthaelt Jinja-Template-Logik.
9. Diese Zeile setzt einen Teil der Implementierung um.
10. Diese Zeile enthaelt Jinja-Template-Logik.
11. Diese Zeile setzt einen Teil der Implementierung um.
12. Diese Zeile enthaelt Jinja-Template-Logik.
13. Diese Zeile setzt einen Teil der Implementierung um.
14. Diese Zeile setzt einen Teil der Implementierung um.
15. Diese Zeile setzt einen Teil der Implementierung um.
16. Diese Zeile setzt einen Teil der Implementierung um.
17. Diese Zeile setzt einen Teil der Implementierung um.
18. Diese Zeile setzt einen Teil der Implementierung um.
19. Diese Zeile enthaelt Jinja-Template-Logik.
20. Diese Zeile setzt einen Teil der Implementierung um.
21. Diese Zeile enthaelt Jinja-Template-Logik.
22. Diese Zeile setzt einen Teil der Implementierung um.
23. Diese Zeile setzt einen Teil der Implementierung um.
24. Diese Zeile enthaelt Jinja-Template-Logik.

## app/templates/my_recipes.html
```html
{% extends "base.html" %}
{% block content %}
<section class="panel">
  <h1>{{ t("my_recipes.title") }}</h1>
  <div class="cards">
    {% for recipe in recipes %}
    <article class="card">
      {% if recipe.images %}
      <img src="/images/{{ recipe.images[0].id }}" alt="{{ recipe.title }}" class="thumb">
      {% elif recipe.title_image_url %}
      <img src="/external-image?url={{ recipe.title_image_url|urlencode }}" alt="{{ recipe.title }}" class="thumb">
      {% endif %}
      <h3><a href="/recipes/{{ recipe.id }}">{{ recipe.title }}</a></h3>
      <p>{{ recipe.category }} | {{ difficulty_label(recipe.difficulty) }} | {{ recipe.prep_time_minutes }} min</p>
      <div class="actions">
        <a href="/recipes/{{ recipe.id }}/edit">{{ t("recipe.edit") }}</a>
        <form method="post" action="/recipes/{{ recipe.id }}/delete" class="inline">
          <button type="submit">{{ t("recipe.delete") }}</button>
        </form>
      </div>
    </article>
    {% else %}
    <p>{{ t("my_recipes.empty") }}</p>
    {% endfor %}
  </div>
</section>
{% endblock %}
```
ZEILEN-ERKL?RUNG
1. Diese Zeile enthaelt Jinja-Template-Logik.
2. Diese Zeile enthaelt Jinja-Template-Logik.
3. Diese Zeile setzt einen Teil der Implementierung um.
4. Diese Zeile setzt einen Teil der Implementierung um.
5. Diese Zeile setzt einen Teil der Implementierung um.
6. Diese Zeile enthaelt Jinja-Template-Logik.
7. Diese Zeile setzt einen Teil der Implementierung um.
8. Diese Zeile enthaelt Jinja-Template-Logik.
9. Diese Zeile setzt einen Teil der Implementierung um.
10. Diese Zeile enthaelt Jinja-Template-Logik.
11. Diese Zeile setzt einen Teil der Implementierung um.
12. Diese Zeile enthaelt Jinja-Template-Logik.
13. Diese Zeile setzt einen Teil der Implementierung um.
14. Diese Zeile setzt einen Teil der Implementierung um.
15. Diese Zeile setzt einen Teil der Implementierung um.
16. Diese Zeile setzt einen Teil der Implementierung um.
17. Diese Zeile setzt einen Teil der Implementierung um.
18. Diese Zeile setzt einen Teil der Implementierung um.
19. Diese Zeile setzt einen Teil der Implementierung um.
20. Diese Zeile setzt einen Teil der Implementierung um.
21. Diese Zeile setzt einen Teil der Implementierung um.
22. Diese Zeile enthaelt Jinja-Template-Logik.
23. Diese Zeile setzt einen Teil der Implementierung um.
24. Diese Zeile enthaelt Jinja-Template-Logik.
25. Diese Zeile setzt einen Teil der Implementierung um.
26. Diese Zeile setzt einen Teil der Implementierung um.
27. Diese Zeile enthaelt Jinja-Template-Logik.

## app/templates/me.html
```html
{% extends "base.html" %}
{% block content %}
<section class="panel narrow">
  <h1>{{ t("profile.title") }}</h1>
  <p><strong>{{ t("profile.email") }}:</strong> {{ user.email }}</p>
  <p><strong>{{ t("profile.role") }}:</strong> {{ role_label(user.role) }}</p>
  <p><strong>{{ t("profile.joined") }}:</strong> {{ user.created_at|datetime_de }}</p>
</section>
{% endblock %}
```
ZEILEN-ERKL?RUNG
1. Diese Zeile enthaelt Jinja-Template-Logik.
2. Diese Zeile enthaelt Jinja-Template-Logik.
3. Diese Zeile setzt einen Teil der Implementierung um.
4. Diese Zeile setzt einen Teil der Implementierung um.
5. Diese Zeile setzt einen Teil der Implementierung um.
6. Diese Zeile setzt einen Teil der Implementierung um.
7. Diese Zeile setzt einen Teil der Implementierung um.
8. Diese Zeile setzt einen Teil der Implementierung um.
9. Diese Zeile enthaelt Jinja-Template-Logik.

## app/templates/partials/recipe_list.html
```html
<div class="cards">
  {% for entry in recipes_data %}
  {% set recipe = entry.recipe %}
  <article class="card">
    {% if recipe.images %}
    <img src="/images/{{ recipe.images[0].id }}" alt="{{ recipe.title }}" class="thumb">
    {% elif recipe.title_image_url %}
    <img src="/external-image?url={{ recipe.title_image_url|urlencode }}" alt="{{ recipe.title }}" class="thumb">
    {% endif %}
    <h3><a href="/recipes/{{ recipe.id }}">{{ recipe.title }}</a></h3>
    <p>{{ recipe.description }}</p>
    <p class="meta">{{ recipe.category }} | {{ difficulty_label(recipe.difficulty) }} | {{ recipe.prep_time_minutes }} min</p>
    <p class="meta">{{ t("recipe.rating_short") }} {{ "%.2f"|format(entry.avg_rating) }} ({{ entry.review_count }})</p>
  </article>
  {% else %}
  <p>{{ t("recipe.no_results") }}</p>
  {% endfor %}
</div>
<div class="pagination">
  {% if page > 1 %}
  <a hx-get="/?page={{ page - 1 }}&sort={{ sort }}&title={{ title }}&category={{ category }}&difficulty={{ difficulty }}&ingredient={{ ingredient }}" hx-target="#recipe-list" hx-push-url="true">{{ t("pagination.previous") }}</a>
  {% endif %}
  <span>{{ t("pagination.page") }} {{ page }} / {{ pages }}</span>
  {% if page < pages %}
  <a hx-get="/?page={{ page + 1 }}&sort={{ sort }}&title={{ title }}&category={{ category }}&difficulty={{ difficulty }}&ingredient={{ ingredient }}" hx-target="#recipe-list" hx-push-url="true">{{ t("pagination.next") }}</a>
  {% endif %}
</div>
```
ZEILEN-ERKL?RUNG
1. Diese Zeile setzt einen Teil der Implementierung um.
2. Diese Zeile enthaelt Jinja-Template-Logik.
3. Diese Zeile enthaelt Jinja-Template-Logik.
4. Diese Zeile setzt einen Teil der Implementierung um.
5. Diese Zeile enthaelt Jinja-Template-Logik.
6. Diese Zeile setzt einen Teil der Implementierung um.
7. Diese Zeile enthaelt Jinja-Template-Logik.
8. Diese Zeile setzt einen Teil der Implementierung um.
9. Diese Zeile enthaelt Jinja-Template-Logik.
10. Diese Zeile setzt einen Teil der Implementierung um.
11. Diese Zeile setzt einen Teil der Implementierung um.
12. Diese Zeile setzt einen Teil der Implementierung um.
13. Diese Zeile setzt einen Teil der Implementierung um.
14. Diese Zeile setzt einen Teil der Implementierung um.
15. Diese Zeile enthaelt Jinja-Template-Logik.
16. Diese Zeile setzt einen Teil der Implementierung um.
17. Diese Zeile enthaelt Jinja-Template-Logik.
18. Diese Zeile setzt einen Teil der Implementierung um.
19. Diese Zeile setzt einen Teil der Implementierung um.
20. Diese Zeile enthaelt Jinja-Template-Logik.
21. Diese Zeile setzt einen Teil der Implementierung um.
22. Diese Zeile enthaelt Jinja-Template-Logik.
23. Diese Zeile setzt einen Teil der Implementierung um.
24. Diese Zeile enthaelt Jinja-Template-Logik.
25. Diese Zeile setzt einen Teil der Implementierung um.
26. Diese Zeile enthaelt Jinja-Template-Logik.
27. Diese Zeile setzt einen Teil der Implementierung um.

## app/templates/partials/favorite_button.html
```html
{% if current_user %}
<form method="post" action="/recipes/{{ recipe.id }}/favorite" hx-post="/recipes/{{ recipe.id }}/favorite" hx-target="#favorite-box" hx-swap="outerHTML" id="favorite-box">
  <button type="submit">{% if is_favorite %}{{ t("favorite.remove") }}{% else %}{{ t("favorite.add") }}{% endif %}</button>
</form>
{% endif %}
```
ZEILEN-ERKL?RUNG
1. Diese Zeile enthaelt Jinja-Template-Logik.
2. Diese Zeile setzt einen Teil der Implementierung um.
3. Diese Zeile setzt einen Teil der Implementierung um.
4. Diese Zeile setzt einen Teil der Implementierung um.
5. Diese Zeile enthaelt Jinja-Template-Logik.

## app/templates/partials/recipe_images.html
```html
﻿<section class="panel" id="recipe-images-section">
  <h2>{{ t("images.title") }}</h2>
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
    <label>{{ t("images.new_file") }}
      <input type="file" name="file" accept="image/png,image/jpeg,image/webp" required>
    </label>
    <label class="inline">
      <input type="checkbox" name="set_primary" value="true">
      {{ t("images.set_primary") }}
    </label>
    <button type="submit">{{ t("images.upload") }}</button>
  </form>
  {% endif %}
  <div class="cards">
    {% for image in recipe.images %}
    <article class="card">
      <img src="/images/{{ image.id }}" alt="{{ image.filename }}" class="thumb">
      <p>{{ image.filename }}</p>
      {% if image.is_primary %}
      <p class="meta">{{ t("images.primary") }}</p>
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
          <button type="submit">{{ t("images.set_primary") }}</button>
        </form>
        {% endif %}
        <form
          method="post"
          action="/images/{{ image.id }}/delete"
          hx-post="/images/{{ image.id }}/delete"
          hx-target="#recipe-images-section"
          hx-swap="outerHTML"
        >
          <button type="submit">{{ t("images.delete") }}</button>
        </form>
      </div>
      {% endif %}
    </article>
    {% else %}
    <p>{{ t("images.empty") }}</p>
    {% endfor %}
  </div>
</section>
```
ZEILEN-ERKL?RUNG
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
24. Diese Zeile enthaelt Jinja-Template-Logik.
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

## app/templates/error_404.html
```html
{% extends "base.html" %}
{% block content %}
<section class="panel narrow">
  <h1>{{ t("error.404_title") }}</h1>
  <p>{{ t("error.404_text") }}</p>
  <p><a href="/">{{ t("error.home_link") }}</a></p>
</section>
{% endblock %}
```
ZEILEN-ERKL?RUNG
1. Diese Zeile enthaelt Jinja-Template-Logik.
2. Diese Zeile enthaelt Jinja-Template-Logik.
3. Diese Zeile setzt einen Teil der Implementierung um.
4. Diese Zeile setzt einen Teil der Implementierung um.
5. Diese Zeile setzt einen Teil der Implementierung um.
6. Diese Zeile setzt einen Teil der Implementierung um.
7. Diese Zeile setzt einen Teil der Implementierung um.
8. Diese Zeile enthaelt Jinja-Template-Logik.

## app/templates/error_500.html
```html
{% extends "base.html" %}
{% block content %}
<section class="panel narrow">
  <h1>{{ t("error.500_title") }}</h1>
  <p>{{ t("error.500_text") }}</p>
  <p><a href="/">{{ t("error.home_link") }}</a></p>
  {% if show_trace and error_trace %}
  <h2>{{ t("error.trace") }}</h2>
  <pre>{{ error_trace }}</pre>
  {% endif %}
</section>
{% endblock %}
```
ZEILEN-ERKL?RUNG
1. Diese Zeile enthaelt Jinja-Template-Logik.
2. Diese Zeile enthaelt Jinja-Template-Logik.
3. Diese Zeile setzt einen Teil der Implementierung um.
4. Diese Zeile setzt einen Teil der Implementierung um.
5. Diese Zeile setzt einen Teil der Implementierung um.
6. Diese Zeile setzt einen Teil der Implementierung um.
7. Diese Zeile enthaelt Jinja-Template-Logik.
8. Diese Zeile setzt einen Teil der Implementierung um.
9. Diese Zeile setzt einen Teil der Implementierung um.
10. Diese Zeile enthaelt Jinja-Template-Logik.
11. Diese Zeile setzt einen Teil der Implementierung um.
12. Diese Zeile enthaelt Jinja-Template-Logik.
