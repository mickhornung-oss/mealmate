Ge?nderte Dateien:
- app/i18n/locales/de.json
- app/templates/admin.html
- app/templates/admin_categories.html
- app/templates/admin_categories_qa.html
- app/templates/submit_recipe.html
- tools/diagnostics/check_umlauts.py

## app/i18n/locales/de.json
```json
{
  "admin.action": "Aktion",
  "admin.category_distinct_count": "Anzahl eindeutiger Kategorien",
  "admin.category_stats_title": "Kategorien-Status",
  "admin.category_top": "Top 10 Kategorien",
  "admin.confirm_warnings_required": "Warnungen vorhanden: Setze 'Trotz Warnungen fortsetzen', um den Import zu starten.",
  "admin.creator": "Ersteller",
  "admin.csv_path": "CSV-Pfad",
  "admin.download_example": "CSV Beispiel herunterladen",
  "admin.download_template": "CSV Template herunterladen",
  "admin.dry_run": "Nur prüfen (Dry Run)",
  "admin.dry_run_done": "Dry-Run abgeschlossen, es wurden keine Daten geschrieben.",
  "admin.email": "E-Mail",
  "admin.force_with_warnings": "Trotz Warnungen fortsetzen",
  "admin.id": "ID",
  "admin.import_blocked_errors": "Import blockiert: Bitte behebe zuerst die fehlerhaften Zeilen.",
  "admin.import_difficulty_values": "Difficulty-Werte: easy, medium, hard",
  "admin.import_encoding_delimiter": "Encoding: utf-8-sig, Delimiter standardmäßig ';' (',' als Fallback)",
  "admin.import_help_intro": "Bitte nutze das kanonische Importformat, damit der Import stabil und ohne Duplikate läuft.",
  "admin.import_help_title": "CSV-Format Hilfe",
  "admin.import_ingredients_example": "Ingredients Beispiel: 2 Eier | 200g Mehl | 1 Prise Salz oder JSON-Liste",
  "admin.import_optional_columns": "Empfohlene Spalten: description, category, difficulty, prep_time_minutes, servings_text, ingredients, image_url, source_uuid",
  "admin.import_required_columns": "Pflichtspalten: title, instructions",
  "admin.import_result_title": "Import-Ergebnis",
  "admin.import_title": "CSV manuell importieren",
  "admin.import_warning_text": "Standard ist Insert-Only; Update Existing nur aktivieren, wenn bewusst gewünscht.",
  "admin.insert_only": "Nur neue hinzufügen (UPSERT SAFE)",
  "admin.preview_button": "Vorschau erstellen",
  "admin.preview_delimiter": "Erkannter Delimiter",
  "admin.preview_done": "Vorschau wurde erstellt.",
  "admin.preview_errors_title": "Fehlerliste",
  "admin.preview_fatal_rows": "Zeilen mit Fehlern",
  "admin.preview_notes": "Hinweise",
  "admin.preview_row": "Zeile",
  "admin.preview_status": "Status",
  "admin.preview_title": "Import-Vorschau",
  "admin.preview_total_rows": "Gesamtzeilen",
  "admin.preview_warnings_title": "Warnungsliste",
  "admin.recipes": "Rezepte",
  "admin.report_errors": "Fehler",
  "admin.report_inserted": "Neu",
  "admin.report_skipped": "Übersprungen",
  "admin.report_updated": "Aktualisiert",
  "admin.report_warnings": "Warnungen",
  "admin.role": "Rolle",
  "admin.save": "Speichern",
  "admin.seed_done": "Seed-Status: bereits ausgeführt.",
  "admin.seed_run": "Einmaligen KochWiki-Seed ausführen",
  "admin.seed_title": "KochWiki-Seed (einmalig)",
  "admin.source": "Quelle",
  "admin.start_import": "Import starten",
  "admin.title": "Admin-Bereich",
  "admin.title_column": "Titel",
  "admin.update_existing": "Existierende aktualisieren (Warnung: nur ausgewählte Felder!)",
  "admin.upload_label": "CSV-Upload",
  "admin.users": "Nutzer",
  "app.name": "Hell's Kitchen and Heaven",
  "auth.change_password_button": "Passwort aktualisieren",
  "auth.change_password_title": "Passwort ändern",
  "auth.change_email_confirm_button": "E-Mail jetzt aktualisieren",
  "auth.change_email_confirm_hint": "Du bestätigst die neue E-Mail-Adresse: {email}",
  "auth.change_email_confirm_title": "E-Mail-Änderung bestätigen",
  "auth.change_email_current": "Aktuelle E-Mail: {email}",
  "auth.change_email_open_link": "E-Mail-Adresse ändern",
  "auth.change_email_request_button": "Bestätigungslink senden",
  "auth.change_email_requested": "Bitte prüfe deine neue E-Mail und bestätige den Link.",
  "auth.change_email_reissue_hint": "Wenn der Link abgelaufen ist, fordere bitte einen neuen Link an.",
  "auth.change_email_retry_link": "Neue E-Mail-Änderung anfordern",
  "auth.change_email_title": "E-Mail ändern",
  "auth.confirm_password": "Passwort bestätigen",
  "auth.email": "E-Mail",
  "auth.email_change_body": "Bitte bestätige deine neue E-Mail-Adresse mit diesem Link: {confirm_link}",
  "auth.email_change_same_email": "Die neue E-Mail entspricht bereits deiner aktuellen Adresse.",
  "auth.email_change_subject": "Hell's Kitchen and Heaven E-Mail-Änderung bestätigen",
  "auth.email_change_success": "E-Mail wurde erfolgreich aktualisiert.",
  "auth.forgot_generic_response": "Wenn der Account existiert, wurde eine E-Mail gesendet.",
  "auth.forgot_password_button": "Reset-Link anfordern",
  "auth.forgot_password_hint": "Gib deine E-Mail oder deinen Benutzernamen ein, um einen Reset-Link zu erhalten.",
  "auth.forgot_password_link": "Passwort vergessen?",
  "auth.forgot_password_title": "Passwort vergessen",
  "auth.identifier": "E-Mail oder Benutzername",
  "auth.login": "Anmelden",
  "auth.login_button": "Anmelden",
  "auth.login_title": "Anmelden",
  "auth.new_password": "Neues Passwort",
  "auth.new_email_label": "Neue E-Mail",
  "auth.old_password": "Altes Passwort",
  "auth.password": "Passwort",
  "auth.password_changed_success": "Passwort wurde erfolgreich geändert.",
  "auth.register": "Konto erstellen",
  "auth.register_button": "Konto erstellen",
  "auth.register_title": "Registrieren",
  "auth.reset_email_body": "Nutze diesen Link zum Zurücksetzen deines Passworts: {reset_link}",
  "auth.reset_email_subject": "Hell's Kitchen and Heaven Passwort-Reset",
  "auth.reset_password_button": "Passwort zurücksetzen",
  "auth.reset_password_title": "Passwort zurücksetzen",
  "auth.reset_success": "Passwort wurde zurückgesetzt, bitte neu anmelden.",
  "difficulty.easy": "Einfach",
  "difficulty.hard": "Schwer",
  "difficulty.medium": "Mittel",
  "discover.filter.apply": "Anwenden",
  "discover.filter.all_images": "Alle Bilder",
  "discover.filter.category": "Kategorie",
  "discover.filter.difficulty": "Schwierigkeit",
  "discover.filter.image": "Bilder",
  "discover.filter.ingredient": "Zutat",
  "discover.filter.title_contains": "Titel enthält",
  "discover.filter.with_image": "Nur mit Bild",
  "discover.sort.newest": "Neueste",
  "discover.sort.oldest": "Älteste",
  "discover.sort.prep_time": "Zubereitungszeit",
  "discover.sort.rating_asc": "Schlechteste Bewertung",
  "discover.sort.rating_desc": "Beste Bewertung",
  "discover.title": "Rezepte entdecken",
  "empty.no_recipes": "Keine Rezepte gefunden.",
  "error.404_text": "Die angeforderte Seite existiert nicht oder wurde verschoben.",
  "error.404_title": "404 - Seite nicht gefunden",
  "error.500_text": "Beim Verarbeiten der Anfrage ist ein unerwarteter Fehler aufgetreten.",
  "error.500_title": "500 - Interner Fehler",
  "error.admin_required": "Administratorrechte erforderlich.",
  "error.auth_required": "Anmeldung erforderlich.",
  "error.csrf_failed": "CSRF-Prüfung fehlgeschlagen.",
  "error.csv_empty": "Die hochgeladene CSV-Datei ist leer.",
  "error.csv_not_found_prefix": "CSV-Datei nicht gefunden",
  "error.csv_only": "Es sind nur CSV-Uploads erlaubt.",
  "error.csv_too_large": "CSV-Upload ist zu groß.",
  "error.csv_upload_required": "Bitte eine CSV-Datei hochladen.",
  "error.email_registered": "Diese E-Mail ist bereits registriert.",
  "error.image_change_file_missing": "Zu diesem Antrag wurde keine Bilddatei gefunden.",
  "error.image_change_request_not_found": "Bildänderungsantrag nicht gefunden.",
  "error.image_change_request_not_pending": "Dieser Bildänderungsantrag ist nicht mehr ausstehend.",
  "error.email_change_token_invalid": "Link ungültig oder abgelaufen. Bitte erneut anfordern.",
  "error.email_invalid": "Bitte gib eine gültige E-Mail-Adresse ein.",
  "error.email_unavailable": "Diese E-Mail ist nicht verfügbar.",
  "error.field_int": "{field} muss eine ganze Zahl sein.",
  "error.field_positive": "{field} muss größer als null sein.",
  "error.home_link": "Zur Startseite",
  "error.image_format_mismatch": "Das Bildformat passt nicht zum Content-Type.",
  "error.image_invalid": "Die hochgeladene Datei ist kein gültiges Bild.",
  "error.image_not_found": "Bild nicht gefunden.",
  "error.image_resolve_prefix": "Die Bild-URL konnte nicht aufgelöst werden",
  "error.image_too_large": "Bild ist zu groß. Maximal {max_mb} MB.",
  "error.image_too_small": "Die hochgeladene Datei ist zu klein für ein gültiges Bild.",
  "error.image_url_scheme": "Die title_image_url muss mit http:// oder https:// beginnen.",
  "error.import_finished_insert": "Import im Modus 'nur neu' abgeschlossen.",
  "error.import_finished_update": "Import im Modus 'bestehende aktualisieren' abgeschlossen.",
  "error.internal": "Interner Serverfehler.",
  "error.invalid_credentials": "Ungültige Zugangsdaten.",
  "error.magic_mismatch": "Dateisignatur passt nicht zum Content-Type.",
  "error.mime_unsupported": "Nicht unterstützter MIME-Typ '{content_type}'.",
  "error.no_image_url": "Keine Bild-URL verfügbar.",
  "error.not_found": "Ressource nicht gefunden.",
  "error.password_confirm_mismatch": "Passwort und Bestätigung stimmen nicht überein.",
  "error.password_min_length": "Das Passwort muss mindestens 10 Zeichen enthalten.",
  "error.password_number": "Das Passwort muss mindestens eine Zahl enthalten.",
  "error.password_old_invalid": "Das alte Passwort ist ungültig.",
  "error.password_special": "Das Passwort muss mindestens ein Sonderzeichen enthalten.",
  "error.password_upper": "Das Passwort muss mindestens einen Grossbuchstaben enthalten.",
  "error.rating_range": "Die Bewertung muss zwischen 1 und 5 liegen.",
  "error.recipe_not_found": "Rezept nicht gefunden.",
  "error.recipe_permission": "Keine ausreichenden Rechte für dieses Rezept.",
  "error.reset_token_invalid": "Der Reset-Link ist ungültig oder abgelaufen.",
  "error.review_not_found": "Bewertung nicht gefunden.",
  "error.review_permission": "Keine ausreichenden Rechte für diese Bewertung.",
  "error.role_invalid": "Die Rolle muss 'user' oder 'admin' sein.",
  "error.seed_already_done": "Der KochWiki-Seed ist bereits als abgeschlossen markiert.",
  "error.seed_finished_errors": "Der Seed wurde mit Fehlern beendet; Marker wurde nicht gesetzt.",
  "error.seed_not_empty": "Der Seed darf nur bei leerer Rezepttabelle laufen.",
  "error.seed_success": "Der KochWiki-Seed wurde erfolgreich abgeschlossen und markiert.",
  "error.submission_already_published": "Diese Einreichung wurde bereits veröffentlicht.",
  "error.submission_not_found": "Einreichung nicht gefunden.",
  "error.submission_permission": "Keine ausreichenden Rechte für diese Einreichung.",
  "error.submission_reject_reason_required": "Bitte einen Ablehnungsgrund angeben.",
  "error.title_instructions_required": "Titel und Anleitung sind erforderlich.",
  "error.trace": "Stacktrace (nur Dev)",
  "error.user_not_found": "Nutzer nicht gefunden.",
  "error.username_invalid": "Benutzername muss 3-30 Zeichen haben und darf nur a-z, A-Z, 0-9, Punkt, Unterstrich oder Bindestrich enthalten.",
  "error.username_taken": "Dieser Benutzername ist bereits vergeben.",
  "error.webp_signature": "Ungültige WEBP-Dateisignatur.",
  "favorite.add": "Zu Favoriten",
  "favorite.remove": "Aus Favoriten entfernen",
  "favorites.empty": "Keine Favoriten gespeichert.",
  "favorites.remove": "Favorit entfernen",
  "favorites.title": "Favoriten",
  "home.all_categories": "Alle Kategorien",
  "home.apply": "Anwenden",
  "home.category": "Kategorie",
  "home.difficulty": "Schwierigkeit",
  "home.featured_hint": "Ausgewählte Rezepte mit Bild und guter Bewertung.",
  "home.featured_subtitle": "Lass dich von beliebten Ideen inspirieren.",
  "home.featured_title": "Empfohlen",
  "home.hero_apply": "Anwenden",
  "home.hero_eyebrow": "Willkommen",
  "home.hero_search_placeholder": "Titel enthält",
  "home.hero_subtitle": "Entdecke Rezepte, speichere Favoriten und teile deine Ideen.",
  "home.hero_title": "Hell's Kitchen and Heaven",
  "home.ingredient": "Zutat",
  "home.per_page": "Pro Seite",
  "home.quick_categories": "Schnelle Kategorien",
  "home.title": "Rezepte entdecken",
  "home.title_contains": "Titel enthält",
  "images.admin_use_direct_upload": "Admins nutzen den direkten Bild-Upload für Rezepte.",
  "images.delete": "Löschen",
  "images.empty": "Noch keine Bilder vorhanden.",
  "images.login_to_propose": "Bitte anmelden, um ein Bild vorzuschlagen.",
  "images.new_file": "Neue Bilddatei",
  "images.pending_badge": "Bildvorschlag ausstehend",
  "images.placeholder": "Kein Bild vorhanden",
  "images.plus_title": "Bild hinzufügen",
  "images.primary": "Hauptbild",
  "images.propose_change": "Bildänderung vorschlagen",
  "images.request_submitted": "Danke, Bildänderung wurde zur Prüfung eingereicht.",
  "images.set_primary": "Als Hauptbild setzen",
  "images.title": "Bilder",
  "images.upload": "Bild hochladen",
  "images.uploaded": "Bild wurde hochgeladen.",
  "images.user_change_note": "Als Nutzer wird die Bildänderung erst nach Admin-Freigabe sichtbar.",
  "image_change.admin_empty": "Keine Bildänderungen in der Warteschlange.",
  "image_change.admin_title": "Bildänderungen (Prüfung)",
  "image_change.approved": "Bildänderung wurde freigegeben.",
  "image_change.compare_title": "Bildvergleich",
  "image_change.current_image": "Aktuelles Bild",
  "image_change.detail_title": "Bildänderungsantrag",
  "image_change.open_queue": "Bildänderungen öffnen",
  "image_change.pending_count": "Ausstehende Anträge: {count}",
  "image_change.proposed_image": "Vorgeschlagenes Bild",
  "image_change.rejected": "Bildänderung wurde abgelehnt.",
  "image_change.review_done": "Diese Bildänderung wurde bereits entschieden.",
  "moderation.approve": "Freigeben",
  "moderation.pending": "Ausstehend",
  "moderation.reject": "Ablehnen",
  "moderation.title": "Moderations-Warteschlange",
  "my_recipes.empty": "Noch keine Rezepte vorhanden.",
  "my_recipes.title": "Meine Rezepte",
  "nav.admin": "Admin",
  "nav.admin_submissions": "Moderation",
  "nav.create_recipe": "Rezept erstellen",
  "nav.discover": "Rezepte entdecken",
  "nav.favorites": "Favoriten",
  "nav.language": "Sprache",
  "nav.login": "Anmelden",
  "nav.logout": "Abmelden",
  "nav.my_recipes": "Meine Rezepte",
  "nav.my_submissions": "Meine Einreichungen",
  "nav.profile": "Mein Profil",
  "nav.publish_recipe": "Rezept veröffentlichen",
  "nav.register": "Registrieren",
  "nav.submit": "Rezept einreichen",
  "nav.submit_recipe": "Rezept einreichen",
  "pagination.first": "Erste",
  "pagination.last": "Letzte",
  "pagination.next": "Weiter",
  "pagination.page": "Seite",
  "pagination.prev": "Zurück",
  "pagination.previous": "Zurück",
  "pagination.results_range": "Zeige {start}-{end} von {total} Rezepten",
  "profile.email": "E-Mail",
  "profile.joined": "Registriert am",
  "profile.role": "Rolle",
  "profile.title": "Mein Profil",
  "profile.user_uid": "Deine Nutzer-ID",
  "profile.username": "Benutzername",
  "profile.username_change_title": "Benutzername ändern",
  "profile.username_save": "Benutzernamen speichern",
  "profile.username_updated": "Benutzername wurde aktualisiert.",
  "recipe.average_rating": "Durchschnittliche Bewertung",
  "recipe.comment": "Kommentar",
  "recipe.delete": "Löschen",
  "recipe.edit": "Bearbeiten",
  "recipe.ingredients": "Zutaten",
  "recipe.instructions": "Anleitung",
  "recipe.no_ingredients": "Keine Zutaten gespeichert.",
  "recipe.no_results": "Keine Rezepte gefunden.",
  "recipe.no_reviews": "Noch keine Bewertungen vorhanden.",
  "recipe.pdf_download": "PDF herunterladen",
  "recipe.rating": "Bewertung",
  "recipe.rating_short": "Bewertung",
  "recipe.review_count_label": "Bewertungen",
  "recipe.reviews": "Bewertungen",
  "recipe.save_review": "Bewertung speichern",
  "recipe_form.category": "Kategorie",
  "recipe_form.create": "Erstellen",
  "recipe_form.create_title": "Rezept veröffentlichen",
  "recipe_form.description": "Beschreibung",
  "recipe_form.difficulty": "Schwierigkeit",
  "recipe_form.edit_title": "Rezept bearbeiten",
  "recipe_form.ingredients": "Zutaten (Format: name|menge|gramm)",
  "recipe_form.instructions": "Anleitung",
  "recipe_form.new_category_label": "Neue Kategorie",
  "recipe_form.new_category_option": "Neue Kategorie...",
  "recipe_form.optional_image": "Optionales Bild",
  "recipe_form.prep_time": "Zubereitungszeit (Minuten)",
  "recipe_form.save": "Speichern",
  "recipe_form.title": "Titel",
  "recipe_form.title_image_url": "Titelbild-URL",
  "role.admin": "Administrator",
  "role.user": "Nutzer",
  "sort.highest_rated": "Beste Bewertung",
  "sort.lowest_rated": "Schlechteste Bewertung",
  "sort.newest": "Neueste",
  "sort.oldest": "Älteste",
  "sort.prep_time": "Zubereitungszeit",
  "submission.admin_detail_title": "Einreichung",
  "submission.admin_empty": "Keine Einreichungen gefunden.",
  "submission.admin_note": "Admin-Notiz",
  "submission.admin_queue_link": "Zur Moderations-Warteschlange",
  "submission.admin_queue_title": "Moderations-Warteschlange",
  "submission.approve_button": "Freigeben",
  "submission.approved": "Einreichung wurde freigegeben.",
  "submission.back_to_queue": "Zurück zur Warteschlange",
  "submission.category": "Kategorie",
  "submission.default_description": "Rezept-Einreichung",
  "submission.description": "Beschreibung",
  "submission.difficulty": "Schwierigkeit",
  "submission.edit_submission": "Einreichung bearbeiten",
  "submission.guest": "Gast",
  "submission.image_deleted": "Bild wurde entfernt.",
  "submission.image_optional": "Optionales Bild",
  "submission.image_primary": "Hauptbild wurde gesetzt.",
  "submission.ingredients": "Zutaten (Format: name|menge|gramm)",
  "submission.instructions": "Anleitung",
  "submission.moderation_actions": "Moderations-Aktionen",
  "submission.my_empty": "Du hast noch keine Einreichungen.",
  "submission.my_submitted_message": "Deine Einreichung wurde gespeichert und wartet auf Prüfung.",
  "submission.my_title": "Meine Einreichungen",
  "submission.new_category_label": "Neue Kategorie",
  "submission.new_category_option": "Neue Kategorie...",
  "submission.open_detail": "Details",
  "submission.optional_admin_note": "Admin-Notiz (optional)",
  "submission.prep_time": "Zubereitungszeit (Minuten, optional)",
  "submission.preview": "Vorschau",
  "submission.reject_button": "Ablehnen",
  "submission.reject_reason": "Ablehnungsgrund",
  "submission.rejected": "Einreichung wurde abgelehnt.",
  "submission.save_changes": "Änderungen speichern",
  "submission.servings": "Portionen (optional)",
  "submission.set_primary_new_image": "Neues Bild als Hauptbild setzen",
  "submission.stats_approved": "Freigegeben",
  "submission.stats_pending": "Ausstehend",
  "submission.stats_rejected": "Abgelehnt",
  "submission.status_all": "Alle",
  "submission.status_approved": "Freigegeben",
  "submission.status_filter": "Status",
  "submission.status_pending": "Ausstehend",
  "submission.status_rejected": "Abgelehnt",
  "submission.submit_button": "Zur Prüfung einreichen",
  "submission.submit_hint": "Einreichungen werden vor der Veröffentlichung durch das Admin-Team geprüft.",
  "submission.submit_title": "Rezept einreichen",
  "submission.submitter_email": "Kontakt-E-Mail (optional)",
  "submission.table_action": "Aktion",
  "submission.table_date": "Datum",
  "submission.table_status": "Status",
  "submission.table_submitter": "Einreicher",
  "submission.table_title": "Titel",
  "submission.thank_you": "Vielen Dank! Dein Rezept wurde eingereicht und wird geprüft.",
  "submission.title": "Titel",
  "submission.updated": "Einreichung wurde aktualisiert."
}
```
ZEILEN-ERKL?RUNG
1. Diese Zeile startet das JSON-Objekt mit allen deutschen UI-Texten.
2. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `admin.action`.
3. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `admin.category_distinct_count`.
4. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `admin.category_stats_title`.
5. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `admin.category_top`.
6. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `admin.confirm_warnings_required`.
7. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `admin.creator`.
8. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `admin.csv_path`.
9. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `admin.download_example`.
10. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `admin.download_template`.
11. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `admin.dry_run`.
12. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `admin.dry_run_done`.
13. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `admin.email`.
14. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `admin.force_with_warnings`.
15. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `admin.id`.
16. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `admin.import_blocked_errors`.
17. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `admin.import_difficulty_values`.
18. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `admin.import_encoding_delimiter`.
19. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `admin.import_help_intro`.
20. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `admin.import_help_title`.
21. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `admin.import_ingredients_example`.
22. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `admin.import_optional_columns`.
23. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `admin.import_required_columns`.
24. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `admin.import_result_title`.
25. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `admin.import_title`.
26. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `admin.import_warning_text`.
27. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `admin.insert_only`.
28. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `admin.preview_button`.
29. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `admin.preview_delimiter`.
30. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `admin.preview_done`.
31. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `admin.preview_errors_title`.
32. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `admin.preview_fatal_rows`.
33. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `admin.preview_notes`.
34. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `admin.preview_row`.
35. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `admin.preview_status`.
36. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `admin.preview_title`.
37. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `admin.preview_total_rows`.
38. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `admin.preview_warnings_title`.
39. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `admin.recipes`.
40. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `admin.report_errors`.
41. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `admin.report_inserted`.
42. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `admin.report_skipped`.
43. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `admin.report_updated`.
44. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `admin.report_warnings`.
45. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `admin.role`.
46. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `admin.save`.
47. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `admin.seed_done`.
48. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `admin.seed_run`.
49. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `admin.seed_title`.
50. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `admin.source`.
51. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `admin.start_import`.
52. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `admin.title`.
53. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `admin.title_column`.
54. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `admin.update_existing`.
55. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `admin.upload_label`.
56. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `admin.users`.
57. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `app.name`.
58. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `auth.change_password_button`.
59. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `auth.change_password_title`.
60. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `auth.change_email_confirm_button`.
61. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `auth.change_email_confirm_hint`.
62. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `auth.change_email_confirm_title`.
63. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `auth.change_email_current`.
64. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `auth.change_email_open_link`.
65. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `auth.change_email_request_button`.
66. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `auth.change_email_requested`.
67. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `auth.change_email_reissue_hint`.
68. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `auth.change_email_retry_link`.
69. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `auth.change_email_title`.
70. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `auth.confirm_password`.
71. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `auth.email`.
72. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `auth.email_change_body`.
73. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `auth.email_change_same_email`.
74. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `auth.email_change_subject`.
75. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `auth.email_change_success`.
76. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `auth.forgot_generic_response`.
77. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `auth.forgot_password_button`.
78. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `auth.forgot_password_hint`.
79. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `auth.forgot_password_link`.
80. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `auth.forgot_password_title`.
81. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `auth.identifier`.
82. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `auth.login`.
83. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `auth.login_button`.
84. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `auth.login_title`.
85. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `auth.new_password`.
86. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `auth.new_email_label`.
87. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `auth.old_password`.
88. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `auth.password`.
89. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `auth.password_changed_success`.
90. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `auth.register`.
91. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `auth.register_button`.
92. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `auth.register_title`.
93. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `auth.reset_email_body`.
94. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `auth.reset_email_subject`.
95. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `auth.reset_password_button`.
96. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `auth.reset_password_title`.
97. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `auth.reset_success`.
98. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `difficulty.easy`.
99. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `difficulty.hard`.
100. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `difficulty.medium`.
101. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `discover.filter.apply`.
102. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `discover.filter.all_images`.
103. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `discover.filter.category`.
104. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `discover.filter.difficulty`.
105. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `discover.filter.image`.
106. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `discover.filter.ingredient`.
107. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `discover.filter.title_contains`.
108. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `discover.filter.with_image`.
109. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `discover.sort.newest`.
110. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `discover.sort.oldest`.
111. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `discover.sort.prep_time`.
112. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `discover.sort.rating_asc`.
113. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `discover.sort.rating_desc`.
114. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `discover.title`.
115. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `empty.no_recipes`.
116. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `error.404_text`.
117. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `error.404_title`.
118. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `error.500_text`.
119. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `error.500_title`.
120. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `error.admin_required`.
121. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `error.auth_required`.
122. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `error.csrf_failed`.
123. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `error.csv_empty`.
124. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `error.csv_not_found_prefix`.
125. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `error.csv_only`.
126. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `error.csv_too_large`.
127. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `error.csv_upload_required`.
128. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `error.email_registered`.
129. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `error.image_change_file_missing`.
130. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `error.image_change_request_not_found`.
131. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `error.image_change_request_not_pending`.
132. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `error.email_change_token_invalid`.
133. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `error.email_invalid`.
134. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `error.email_unavailable`.
135. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `error.field_int`.
136. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `error.field_positive`.
137. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `error.home_link`.
138. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `error.image_format_mismatch`.
139. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `error.image_invalid`.
140. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `error.image_not_found`.
141. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `error.image_resolve_prefix`.
142. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `error.image_too_large`.
143. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `error.image_too_small`.
144. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `error.image_url_scheme`.
145. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `error.import_finished_insert`.
146. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `error.import_finished_update`.
147. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `error.internal`.
148. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `error.invalid_credentials`.
149. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `error.magic_mismatch`.
150. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `error.mime_unsupported`.
151. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `error.no_image_url`.
152. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `error.not_found`.
153. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `error.password_confirm_mismatch`.
154. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `error.password_min_length`.
155. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `error.password_number`.
156. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `error.password_old_invalid`.
157. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `error.password_special`.
158. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `error.password_upper`.
159. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `error.rating_range`.
160. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `error.recipe_not_found`.
161. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `error.recipe_permission`.
162. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `error.reset_token_invalid`.
163. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `error.review_not_found`.
164. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `error.review_permission`.
165. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `error.role_invalid`.
166. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `error.seed_already_done`.
167. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `error.seed_finished_errors`.
168. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `error.seed_not_empty`.
169. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `error.seed_success`.
170. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `error.submission_already_published`.
171. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `error.submission_not_found`.
172. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `error.submission_permission`.
173. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `error.submission_reject_reason_required`.
174. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `error.title_instructions_required`.
175. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `error.trace`.
176. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `error.user_not_found`.
177. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `error.username_invalid`.
178. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `error.username_taken`.
179. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `error.webp_signature`.
180. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `favorite.add`.
181. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `favorite.remove`.
182. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `favorites.empty`.
183. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `favorites.remove`.
184. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `favorites.title`.
185. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `home.all_categories`.
186. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `home.apply`.
187. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `home.category`.
188. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `home.difficulty`.
189. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `home.featured_hint`.
190. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `home.featured_subtitle`.
191. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `home.featured_title`.
192. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `home.hero_apply`.
193. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `home.hero_eyebrow`.
194. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `home.hero_search_placeholder`.
195. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `home.hero_subtitle`.
196. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `home.hero_title`.
197. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `home.ingredient`.
198. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `home.per_page`.
199. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `home.quick_categories`.
200. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `home.title`.
201. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `home.title_contains`.
202. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `images.admin_use_direct_upload`.
203. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `images.delete`.
204. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `images.empty`.
205. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `images.login_to_propose`.
206. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `images.new_file`.
207. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `images.pending_badge`.
208. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `images.placeholder`.
209. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `images.plus_title`.
210. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `images.primary`.
211. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `images.propose_change`.
212. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `images.request_submitted`.
213. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `images.set_primary`.
214. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `images.title`.
215. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `images.upload`.
216. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `images.uploaded`.
217. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `images.user_change_note`.
218. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `image_change.admin_empty`.
219. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `image_change.admin_title`.
220. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `image_change.approved`.
221. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `image_change.compare_title`.
222. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `image_change.current_image`.
223. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `image_change.detail_title`.
224. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `image_change.open_queue`.
225. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `image_change.pending_count`.
226. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `image_change.proposed_image`.
227. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `image_change.rejected`.
228. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `image_change.review_done`.
229. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `moderation.approve`.
230. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `moderation.pending`.
231. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `moderation.reject`.
232. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `moderation.title`.
233. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `my_recipes.empty`.
234. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `my_recipes.title`.
235. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `nav.admin`.
236. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `nav.admin_submissions`.
237. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `nav.create_recipe`.
238. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `nav.discover`.
239. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `nav.favorites`.
240. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `nav.language`.
241. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `nav.login`.
242. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `nav.logout`.
243. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `nav.my_recipes`.
244. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `nav.my_submissions`.
245. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `nav.profile`.
246. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `nav.publish_recipe`.
247. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `nav.register`.
248. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `nav.submit`.
249. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `nav.submit_recipe`.
250. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `pagination.first`.
251. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `pagination.last`.
252. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `pagination.next`.
253. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `pagination.page`.
254. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `pagination.prev`.
255. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `pagination.previous`.
256. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `pagination.results_range`.
257. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `profile.email`.
258. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `profile.joined`.
259. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `profile.role`.
260. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `profile.title`.
261. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `profile.user_uid`.
262. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `profile.username`.
263. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `profile.username_change_title`.
264. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `profile.username_save`.
265. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `profile.username_updated`.
266. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `recipe.average_rating`.
267. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `recipe.comment`.
268. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `recipe.delete`.
269. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `recipe.edit`.
270. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `recipe.ingredients`.
271. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `recipe.instructions`.
272. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `recipe.no_ingredients`.
273. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `recipe.no_results`.
274. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `recipe.no_reviews`.
275. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `recipe.pdf_download`.
276. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `recipe.rating`.
277. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `recipe.rating_short`.
278. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `recipe.review_count_label`.
279. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `recipe.reviews`.
280. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `recipe.save_review`.
281. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `recipe_form.category`.
282. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `recipe_form.create`.
283. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `recipe_form.create_title`.
284. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `recipe_form.description`.
285. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `recipe_form.difficulty`.
286. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `recipe_form.edit_title`.
287. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `recipe_form.ingredients`.
288. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `recipe_form.instructions`.
289. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `recipe_form.new_category_label`.
290. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `recipe_form.new_category_option`.
291. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `recipe_form.optional_image`.
292. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `recipe_form.prep_time`.
293. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `recipe_form.save`.
294. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `recipe_form.title`.
295. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `recipe_form.title_image_url`.
296. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `role.admin`.
297. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `role.user`.
298. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `sort.highest_rated`.
299. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `sort.lowest_rated`.
300. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `sort.newest`.
301. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `sort.oldest`.
302. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `sort.prep_time`.
303. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `submission.admin_detail_title`.
304. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `submission.admin_empty`.
305. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `submission.admin_note`.
306. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `submission.admin_queue_link`.
307. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `submission.admin_queue_title`.
308. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `submission.approve_button`.
309. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `submission.approved`.
310. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `submission.back_to_queue`.
311. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `submission.category`.
312. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `submission.default_description`.
313. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `submission.description`.
314. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `submission.difficulty`.
315. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `submission.edit_submission`.
316. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `submission.guest`.
317. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `submission.image_deleted`.
318. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `submission.image_optional`.
319. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `submission.image_primary`.
320. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `submission.ingredients`.
321. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `submission.instructions`.
322. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `submission.moderation_actions`.
323. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `submission.my_empty`.
324. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `submission.my_submitted_message`.
325. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `submission.my_title`.
326. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `submission.new_category_label`.
327. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `submission.new_category_option`.
328. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `submission.open_detail`.
329. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `submission.optional_admin_note`.
330. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `submission.prep_time`.
331. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `submission.preview`.
332. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `submission.reject_button`.
333. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `submission.reject_reason`.
334. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `submission.rejected`.
335. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `submission.save_changes`.
336. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `submission.servings`.
337. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `submission.set_primary_new_image`.
338. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `submission.stats_approved`.
339. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `submission.stats_pending`.
340. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `submission.stats_rejected`.
341. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `submission.status_all`.
342. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `submission.status_approved`.
343. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `submission.status_filter`.
344. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `submission.status_pending`.
345. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `submission.status_rejected`.
346. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `submission.submit_button`.
347. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `submission.submit_hint`.
348. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `submission.submit_title`.
349. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `submission.submitter_email`.
350. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `submission.table_action`.
351. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `submission.table_date`.
352. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `submission.table_status`.
353. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `submission.table_submitter`.
354. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `submission.table_title`.
355. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `submission.thank_you`.
356. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `submission.title`.
357. Diese Zeile definiert den deutschen ?bersetzungstext f?r den Schl?ssel `submission.updated`.
358. Diese Zeile schlie?t das JSON-Objekt mit allen deutschen UI-Texten.

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
  <p><a href="/admin/categories">Kategorien aufräumen</a></p>
</section>
<section class="panel">
  <h2>{{ t("image_change.admin_title") }}</h2>
  <p class="meta">{{ t("image_change.pending_count", count=pending_image_change_count) }}</p>
  <p><a href="/admin/image-change-requests">{{ t("image_change.open_queue") }}</a></p>
  {% if pending_image_change_requests %}
  <table>
    <thead>
      <tr>
        <th>{{ t("submission.table_date") }}</th>
        <th>{{ t("submission.table_title") }}</th>
        <th>{{ t("submission.table_submitter") }}</th>
        <th>{{ t("submission.table_action") }}</th>
      </tr>
    </thead>
    <tbody>
      {% for item in pending_image_change_requests %}
      <tr>
        <td>{{ item.created_at|datetime_de }}</td>
        <td><a href="/recipes/{{ item.recipe.id }}">{{ item.recipe.title }}</a></td>
        <td>{{ item.requester_user.email if item.requester_user else "-" }}</td>
        <td><a href="/admin/image-change-requests/{{ item.id }}">{{ t("submission.open_detail") }}</a></td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
  {% else %}
  <p>{{ t("image_change.admin_empty") }}</p>
  {% endif %}
</section>
<section class="panel">
  <h2>{{ t("admin.import_title") }}</h2>
  <div class="stack">
    <h3>{{ t("admin.import_help_title") }}</h3>
    <p class="meta">{{ t("admin.import_help_intro") }}</p>
    <ul>
      <li>{{ t("admin.import_required_columns") }}</li>
      <li>{{ t("admin.import_optional_columns") }}</li>
      <li>{{ t("admin.import_difficulty_values") }}</li>
      <li>{{ t("admin.import_ingredients_example") }}</li>
      <li>{{ t("admin.import_encoding_delimiter") }}</li>
    </ul>
    <div class="actions">
      <a href="/admin/import-template.csv">{{ t("admin.download_template") }}</a>
      <a href="/admin/import-example.csv">{{ t("admin.download_example") }}</a>
    </div>
  </div>
  <form method="post" action="/admin/import-recipes" enctype="multipart/form-data" class="stack">
    <label>{{ t("admin.upload_label") }}
      <input type="file" name="file" accept=".csv" required>
    </label>
    <label class="inline">
      <input type="checkbox" name="insert_only" {% if import_mode == "insert_only" %}checked{% endif %}>
      {{ t("admin.insert_only") }}
    </label>
    <label class="inline">
      <input type="checkbox" name="update_existing" {% if import_mode == "update_existing" %}checked{% endif %}>
      {{ t("admin.update_existing") }}
    </label>
    <label class="inline">
      <input type="checkbox" name="dry_run" {% if import_dry_run %}checked{% endif %}>
      {{ t("admin.dry_run") }}
    </label>
    <label class="inline">
      <input type="checkbox" name="force_with_warnings" {% if import_force_with_warnings %}checked{% endif %}>
      {{ t("admin.force_with_warnings") }}
    </label>
    <p class="meta">{{ t("admin.import_warning_text") }}</p>
    <div class="actions">
      <button type="submit" name="action" value="preview">{{ t("admin.preview_button") }}</button>
      <button type="submit" name="action" value="import">{{ t("admin.start_import") }}</button>
    </div>
  </form>
  {% if preview_report %}
  <h3>{{ t("admin.preview_title") }}</h3>
  <p class="meta">
    {{ t("admin.preview_total_rows") }}: {{ preview_report.total_rows }},
    {{ t("admin.preview_delimiter") }}: {{ preview_report.delimiter }},
    {{ t("admin.preview_fatal_rows") }}: {{ preview_report.fatal_error_rows }}
  </p>
  <p class="meta">
    {{ t("admin.report_inserted") }}: {{ preview_report.inserted }},
    {{ t("admin.report_updated") }}: {{ preview_report.updated }},
    {{ t("admin.report_skipped") }}: {{ preview_report.skipped }},
    {{ t("admin.report_errors") }}: {{ preview_report.errors|length }},
    {{ t("admin.report_warnings") }}: {{ preview_report.warnings|length }}
  </p>
  <table>
    <thead>
      <tr>
        <th>{{ t("admin.preview_row") }}</th>
        <th>{{ t("admin.title_column") }}</th>
        <th>{{ t("home.category") }}</th>
        <th>{{ t("home.difficulty") }}</th>
        <th>{{ t("recipe_form.prep_time") }}</th>
        <th>{{ t("admin.preview_status") }}</th>
        <th>{{ t("admin.preview_notes") }}</th>
      </tr>
    </thead>
    <tbody>
      {% for row in preview_report.preview_rows %}
      <tr>
        <td>{{ row.row_number }}</td>
        <td>{{ row.title }}</td>
        <td>{{ row.category }}</td>
        <td>{{ difficulty_label(row.difficulty) }}</td>
        <td>{{ row.prep_time_minutes }}</td>
        <td>{{ row.status }}</td>
        <td>
          {% if row.errors %}
          {{ row.errors|join("; ") }}
          {% elif row.warnings %}
          {{ row.warnings|join("; ") }}
          {% else %}
          -
          {% endif %}
        </td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
  {% if preview_report.errors %}
  <h4>{{ t("admin.preview_errors_title") }}</h4>
  <ul>
    {% for item in preview_report.errors %}
    <li>{{ item }}</li>
    {% endfor %}
  </ul>
  {% endif %}
  {% if preview_report.warnings %}
  <h4>{{ t("admin.preview_warnings_title") }}</h4>
  <ul>
    {% for item in preview_report.warnings %}
    <li>{{ item }}</li>
    {% endfor %}
  </ul>
  {% endif %}
  {% endif %}
  {% if report %}
  <h3>{{ t("admin.import_result_title") }}</h3>
  <p class="meta">
    {{ t("admin.report_inserted") }}: {{ report.inserted }},
    {{ t("admin.report_updated") }}: {{ report.updated }},
    {{ t("admin.report_skipped") }}: {{ report.skipped }},
    {{ t("admin.report_errors") }}: {{ report.errors|length }},
    {{ t("admin.report_warnings") }}: {{ report.warnings|length }}
  </p>
  {% endif %}
</section>
<section class="panel">
  <h2>{{ t("admin.category_stats_title") }}</h2>
  <p><a href="/admin/categories">Zum Kategorie-Tool</a></p>
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
ZEILEN-ERKL?RUNG
1. Diese Zeile bindet das Basis-Template f?r die Seite ein.
2. Diese Zeile startet den Content-Block f?r den Seiteninhalt.
3. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
4. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
5. Diese Zeile enth?lt Jinja-Logik oder eine dynamische Ausgabe f?r die UI.
6. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
7. Diese Zeile enth?lt Jinja-Logik oder eine dynamische Ausgabe f?r die UI.
8. Diese Zeile enth?lt Jinja-Logik oder eine dynamische Ausgabe f?r die UI.
9. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
10. Diese Zeile enth?lt Jinja-Logik oder eine dynamische Ausgabe f?r die UI.
11. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
12. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
13. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
14. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
15. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
16. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
17. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
18. Diese Zeile enth?lt Jinja-Logik oder eine dynamische Ausgabe f?r die UI.
19. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
20. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
21. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
22. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
23. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
24. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
25. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
26. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
27. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
28. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
29. Diese Zeile enth?lt Jinja-Logik oder eine dynamische Ausgabe f?r die UI.
30. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
31. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
32. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
33. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
34. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
35. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
36. Diese Zeile enth?lt Jinja-Logik oder eine dynamische Ausgabe f?r die UI.
37. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
38. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
39. Diese Zeile enth?lt Jinja-Logik oder eine dynamische Ausgabe f?r die UI.
40. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
41. Diese Zeile enth?lt Jinja-Logik oder eine dynamische Ausgabe f?r die UI.
42. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
43. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
44. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
45. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
46. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
47. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
48. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
49. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
50. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
51. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
52. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
53. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
54. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
55. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
56. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
57. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
58. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
59. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
60. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
61. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
62. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
63. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
64. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
65. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
66. Diese Zeile enth?lt Jinja-Logik oder eine dynamische Ausgabe f?r die UI.
67. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
68. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
69. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
70. Diese Zeile enth?lt Jinja-Logik oder eine dynamische Ausgabe f?r die UI.
71. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
72. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
73. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
74. Diese Zeile enth?lt Jinja-Logik oder eine dynamische Ausgabe f?r die UI.
75. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
76. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
77. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
78. Diese Zeile enth?lt Jinja-Logik oder eine dynamische Ausgabe f?r die UI.
79. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
80. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
81. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
82. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
83. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
84. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
85. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
86. Diese Zeile enth?lt Jinja-Logik oder eine dynamische Ausgabe f?r die UI.
87. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
88. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
89. Diese Zeile enth?lt Jinja-Logik oder eine dynamische Ausgabe f?r die UI.
90. Diese Zeile enth?lt Jinja-Logik oder eine dynamische Ausgabe f?r die UI.
91. Diese Zeile enth?lt Jinja-Logik oder eine dynamische Ausgabe f?r die UI.
92. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
93. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
94. Diese Zeile enth?lt Jinja-Logik oder eine dynamische Ausgabe f?r die UI.
95. Diese Zeile enth?lt Jinja-Logik oder eine dynamische Ausgabe f?r die UI.
96. Diese Zeile enth?lt Jinja-Logik oder eine dynamische Ausgabe f?r die UI.
97. Diese Zeile enth?lt Jinja-Logik oder eine dynamische Ausgabe f?r die UI.
98. Diese Zeile enth?lt Jinja-Logik oder eine dynamische Ausgabe f?r die UI.
99. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
100. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
101. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
102. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
103. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
104. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
105. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
106. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
107. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
108. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
109. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
110. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
111. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
112. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
113. Diese Zeile enth?lt Jinja-Logik oder eine dynamische Ausgabe f?r die UI.
114. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
115. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
116. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
117. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
118. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
119. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
120. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
121. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
122. Diese Zeile enth?lt Jinja-Logik oder eine dynamische Ausgabe f?r die UI.
123. Diese Zeile enth?lt Jinja-Logik oder eine dynamische Ausgabe f?r die UI.
124. Diese Zeile enth?lt Jinja-Logik oder eine dynamische Ausgabe f?r die UI.
125. Diese Zeile enth?lt Jinja-Logik oder eine dynamische Ausgabe f?r die UI.
126. Diese Zeile enth?lt Jinja-Logik oder eine dynamische Ausgabe f?r die UI.
127. Diese Zeile enth?lt Template-Text f?r die Oberfl?che.
128. Diese Zeile enth?lt Jinja-Logik oder eine dynamische Ausgabe f?r die UI.
129. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
130. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
131. Diese Zeile enth?lt Jinja-Logik oder eine dynamische Ausgabe f?r die UI.
132. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
133. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
134. Diese Zeile enth?lt Jinja-Logik oder eine dynamische Ausgabe f?r die UI.
135. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
136. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
137. Diese Zeile enth?lt Jinja-Logik oder eine dynamische Ausgabe f?r die UI.
138. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
139. Diese Zeile enth?lt Jinja-Logik oder eine dynamische Ausgabe f?r die UI.
140. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
141. Diese Zeile enth?lt Jinja-Logik oder eine dynamische Ausgabe f?r die UI.
142. Diese Zeile enth?lt Jinja-Logik oder eine dynamische Ausgabe f?r die UI.
143. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
144. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
145. Diese Zeile enth?lt Jinja-Logik oder eine dynamische Ausgabe f?r die UI.
146. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
147. Diese Zeile enth?lt Jinja-Logik oder eine dynamische Ausgabe f?r die UI.
148. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
149. Diese Zeile enth?lt Jinja-Logik oder eine dynamische Ausgabe f?r die UI.
150. Diese Zeile enth?lt Jinja-Logik oder eine dynamische Ausgabe f?r die UI.
151. Diese Zeile enth?lt Jinja-Logik oder eine dynamische Ausgabe f?r die UI.
152. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
153. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
154. Diese Zeile enth?lt Jinja-Logik oder eine dynamische Ausgabe f?r die UI.
155. Diese Zeile enth?lt Jinja-Logik oder eine dynamische Ausgabe f?r die UI.
156. Diese Zeile enth?lt Jinja-Logik oder eine dynamische Ausgabe f?r die UI.
157. Diese Zeile enth?lt Jinja-Logik oder eine dynamische Ausgabe f?r die UI.
158. Diese Zeile enth?lt Jinja-Logik oder eine dynamische Ausgabe f?r die UI.
159. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
160. Diese Zeile enth?lt Jinja-Logik oder eine dynamische Ausgabe f?r die UI.
161. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
162. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
163. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
164. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
165. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
166. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
167. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
168. Diese Zeile enth?lt Jinja-Logik oder eine dynamische Ausgabe f?r die UI.
169. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
170. Diese Zeile enth?lt Jinja-Logik oder eine dynamische Ausgabe f?r die UI.
171. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
172. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
173. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
174. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
175. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
176. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
177. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
178. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
179. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
180. Diese Zeile enth?lt Jinja-Logik oder eine dynamische Ausgabe f?r die UI.
181. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
182. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
183. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
184. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
185. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
186. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
187. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
188. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
189. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
190. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
191. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
192. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
193. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
194. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
195. Diese Zeile enth?lt Jinja-Logik oder eine dynamische Ausgabe f?r die UI.
196. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
197. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
198. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
199. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
200. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
201. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
202. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
203. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
204. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
205. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
206. Diese Zeile enth?lt Jinja-Logik oder eine dynamische Ausgabe f?r die UI.
207. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
208. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
209. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
210. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
211. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
212. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
213. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
214. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
215. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
216. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
217. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
218. Diese Zeile enth?lt Jinja-Logik oder eine dynamische Ausgabe f?r die UI.
219. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
220. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
221. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
222. Diese Zeile beendet den Content-Block des Templates.

## app/templates/admin_categories.html
```html
﻿{% extends "base.html" %}
{% block content %}
<section class="panel">
  <h1>Kategorie-Aufräumen</h1>
  <p class="meta">Rohkategorien bleiben erhalten, nur canonical_category wird für UI und Filter gesetzt.</p>
  {% if rebuild_report %}
  <p class="meta">
    Rebuild ({{ rebuild_report.mode }}) abgeschlossen: aktualisiert {{ rebuild_report.updated }}, unverändert {{ rebuild_report.skipped }}.
    {% if rebuild_report.mode == "suspicious" %}Geprüfte auffällige Rezepte: {{ rebuild_report.suspicious_count }}.{% endif %}
  </p>
  {% endif %}
  <div class="actions">
    <a class="btn btn-secondary" href="/admin">Zur Admin-Startseite</a>
    <a class="btn btn-secondary" href="/admin/categories/qa">QA-Diagnose anzeigen</a>
    <form method="post" action="/admin/categories/rebuild?mode=full">
      <button type="submit" class="btn btn-primary">Rebuild komplett</button>
    </form>
    <form method="post" action="/admin/categories/rebuild?mode=suspicious">
      <button type="submit" class="btn btn-secondary">Nur auffällige Rebuilds</button>
    </form>
  </div>
</section>

<section class="panel">
  <h2>Neue Mapping-Regel</h2>
  <form method="post" action="/admin/categories/mappings" class="stack">
    <label>Pattern (Substring, case-insensitive)
      <input type="text" name="pattern" required placeholder="z.B. Suppe, Dessert, Frühstück">
    </label>
    <label>Kanonische Kategorie
      <select name="canonical_category">
        {% for option in standard_canonical_categories %}
        <option value="{{ option }}">{{ option }}</option>
        {% endfor %}
        <option value="__IGNORE__">(IGNORE / nicht zuordnen)</option>
      </select>
    </label>
    <label>Scope
      <select name="scope">
        <option value="raw" selected>raw (nur cleaned_raw_category)</option>
        <option value="fulltext">fulltext (nur wenn raw leer/unspezifisch)</option>
      </select>
    </label>
    <label>Priorität (kleiner = stärker)
      <input type="number" name="priority" value="100" min="0" required>
    </label>
    <label class="inline">
      <input type="checkbox" name="enabled" checked>
      Regel aktiv
    </label>
    <button type="submit" class="btn btn-primary">Mapping speichern</button>
  </form>
</section>

<section class="panel">
  <h2>Top Raw Categories</h2>
  <table>
    <thead>
      <tr>
        <th>Raw Category</th>
        <th>Anzahl</th>
        <th>Vorschlag Canonical</th>
      </tr>
    </thead>
    <tbody>
      {% for item in raw_category_overview %}
      <tr>
        <td>{{ item.raw_category }}</td>
        <td>{{ item.count }}</td>
        <td>{{ item.guessed_canonical }}</td>
      </tr>
      {% else %}
      <tr>
        <td colspan="3">Keine Kategorien vorhanden.</td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
</section>

<section class="panel">
  <h2>Gespeicherte Mapping-Regeln</h2>
  <table>
    <thead>
      <tr>
        <th>ID</th>
        <th>Pattern</th>
        <th>Canonical</th>
        <th>Scope</th>
        <th>Priorität</th>
        <th>Status</th>
        <th>Aktion</th>
      </tr>
    </thead>
    <tbody>
      {% for mapping in category_mappings %}
      <tr>
        <td>{{ mapping.id }}</td>
        <td>{{ mapping.pattern }}</td>
        <td>{{ mapping.canonical_category }}</td>
        <td>{{ mapping.scope or "raw" }}</td>
        <td>{{ mapping.priority }}</td>
        <td>{% if mapping.enabled %}aktiv{% else %}inaktiv{% endif %}</td>
        <td>
          <form method="post" action="/admin/categories/mappings/{{ mapping.id }}/toggle">
            <button type="submit" class="btn {% if mapping.enabled %}btn-danger{% else %}btn-secondary{% endif %}">
              {% if mapping.enabled %}Deaktivieren{% else %}Aktivieren{% endif %}
            </button>
          </form>
        </td>
      </tr>
      {% else %}
      <tr>
        <td colspan="7">Noch keine Mapping-Regeln vorhanden.</td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
</section>
{% endblock %}
```
ZEILEN-ERKL?RUNG
1. Diese Zeile enth?lt Template-Text f?r die Oberfl?che.
2. Diese Zeile startet den Content-Block f?r den Seiteninhalt.
3. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
4. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
5. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
6. Diese Zeile enth?lt Jinja-Logik oder eine dynamische Ausgabe f?r die UI.
7. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
8. Diese Zeile enth?lt Template-Text f?r die Oberfl?che.
9. Diese Zeile enth?lt Jinja-Logik oder eine dynamische Ausgabe f?r die UI.
10. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
11. Diese Zeile enth?lt Jinja-Logik oder eine dynamische Ausgabe f?r die UI.
12. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
13. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
14. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
15. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
16. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
17. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
18. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
19. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
20. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
21. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
22. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
23. Diese Zeile ist absichtlich leer, um die Lesbarkeit zu verbessern.
24. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
25. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
26. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
27. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
28. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
29. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
30. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
31. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
32. Diese Zeile enth?lt Jinja-Logik oder eine dynamische Ausgabe f?r die UI.
33. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
34. Diese Zeile enth?lt Jinja-Logik oder eine dynamische Ausgabe f?r die UI.
35. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
36. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
37. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
38. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
39. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
40. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
41. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
42. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
43. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
44. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
45. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
46. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
47. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
48. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
49. Diese Zeile enth?lt Template-Text f?r die Oberfl?che.
50. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
51. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
52. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
53. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
54. Diese Zeile ist absichtlich leer, um die Lesbarkeit zu verbessern.
55. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
56. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
57. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
58. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
59. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
60. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
61. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
62. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
63. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
64. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
65. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
66. Diese Zeile enth?lt Jinja-Logik oder eine dynamische Ausgabe f?r die UI.
67. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
68. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
69. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
70. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
71. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
72. Diese Zeile enth?lt Jinja-Logik oder eine dynamische Ausgabe f?r die UI.
73. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
74. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
75. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
76. Diese Zeile enth?lt Jinja-Logik oder eine dynamische Ausgabe f?r die UI.
77. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
78. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
79. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
80. Diese Zeile ist absichtlich leer, um die Lesbarkeit zu verbessern.
81. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
82. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
83. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
84. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
85. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
86. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
87. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
88. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
89. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
90. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
91. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
92. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
93. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
94. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
95. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
96. Diese Zeile enth?lt Jinja-Logik oder eine dynamische Ausgabe f?r die UI.
97. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
98. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
99. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
100. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
101. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
102. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
103. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
104. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
105. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
106. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
107. Diese Zeile enth?lt Jinja-Logik oder eine dynamische Ausgabe f?r die UI.
108. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
109. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
110. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
111. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
112. Diese Zeile enth?lt Jinja-Logik oder eine dynamische Ausgabe f?r die UI.
113. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
114. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
115. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
116. Diese Zeile enth?lt Jinja-Logik oder eine dynamische Ausgabe f?r die UI.
117. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
118. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
119. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
120. Diese Zeile beendet den Content-Block des Templates.

## app/templates/admin_categories_qa.html
```html
{% extends "base.html" %}
{% block content %}
<section class="panel">
  <h1>Kategorie-QA Diagnose</h1>
  <p class="meta">Die Liste zeigt auffällige Zuordnungen für manuelle Prüfung.</p>
  <div class="actions">
    <a class="btn btn-secondary" href="/admin/categories">Zurück zum Kategorie-Tool</a>
    <a class="btn btn-secondary" href="/admin">Zur Admin-Startseite</a>
  </div>
</section>

<section class="panel">
  <h2>Auffällige Rezepte (max {{ limit }})</h2>
  <table>
    <thead>
      <tr>
        <th>Recipe ID</th>
        <th>Titel</th>
        <th>Raw Category</th>
        <th>Aktuell Canonical</th>
        <th>Vorschlag Canonical</th>
        <th>Reason</th>
        <th>Auffälligkeit</th>
      </tr>
    </thead>
    <tbody>
      {% for row in qa_rows %}
      <tr>
        <td>{{ row.recipe_id }}</td>
        <td><a href="/recipes/{{ row.recipe_id }}">{{ row.title }}</a></td>
        <td>{{ row.raw_category }}</td>
        <td>{{ row.canonical_category or "-" }}</td>
        <td>{{ row.suggested_canonical }}</td>
        <td>{{ row.reason }}</td>
        <td>{{ row.suspicious_reason }}</td>
      </tr>
      {% else %}
      <tr>
        <td colspan="7">Keine auffälligen Rezepte gefunden.</td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
</section>
{% endblock %}
```
ZEILEN-ERKL?RUNG
1. Diese Zeile bindet das Basis-Template f?r die Seite ein.
2. Diese Zeile startet den Content-Block f?r den Seiteninhalt.
3. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
4. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
5. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
6. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
7. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
8. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
9. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
10. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
11. Diese Zeile ist absichtlich leer, um die Lesbarkeit zu verbessern.
12. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
13. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
14. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
15. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
16. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
17. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
18. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
19. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
20. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
21. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
22. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
23. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
24. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
25. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
26. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
27. Diese Zeile enth?lt Jinja-Logik oder eine dynamische Ausgabe f?r die UI.
28. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
29. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
30. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
31. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
32. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
33. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
34. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
35. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
36. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
37. Diese Zeile enth?lt Jinja-Logik oder eine dynamische Ausgabe f?r die UI.
38. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
39. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
40. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
41. Diese Zeile enth?lt Jinja-Logik oder eine dynamische Ausgabe f?r die UI.
42. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
43. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
44. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
45. Diese Zeile beendet den Content-Block des Templates.

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
      <textarea name="ingredients_text" rows="6" placeholder="Tomate|2 Stück&#10;Olivenöl|1 EL">{{ ingredients_text }}</textarea>
    </label>
    <label>{{ t("submission.image_optional") }} <input type="file" name="image" accept="image/png,image/jpeg,image/webp"></label>
    <button type="submit">{{ t("submission.submit_button") }}</button>
  </form>
</section>
{% endblock %}
```
ZEILEN-ERKL?RUNG
1. Diese Zeile bindet das Basis-Template f?r die Seite ein.
2. Diese Zeile startet den Content-Block f?r den Seiteninhalt.
3. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
4. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
5. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
6. Diese Zeile enth?lt Jinja-Logik oder eine dynamische Ausgabe f?r die UI.
7. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
8. Diese Zeile enth?lt Jinja-Logik oder eine dynamische Ausgabe f?r die UI.
9. Diese Zeile enth?lt Jinja-Logik oder eine dynamische Ausgabe f?r die UI.
10. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
11. Diese Zeile enth?lt Jinja-Logik oder eine dynamische Ausgabe f?r die UI.
12. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
13. Diese Zeile enth?lt Jinja-Logik oder eine dynamische Ausgabe f?r die UI.
14. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
15. Diese Zeile enth?lt Jinja-Logik oder eine dynamische Ausgabe f?r die UI.
16. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
17. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
18. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
19. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
20. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
21. Diese Zeile enth?lt Jinja-Logik oder eine dynamische Ausgabe f?r die UI.
22. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
23. Diese Zeile enth?lt Jinja-Logik oder eine dynamische Ausgabe f?r die UI.
24. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
25. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
26. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
27. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
28. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
29. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
30. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
31. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
32. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
33. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
34. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
35. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
36. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
37. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
38. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
39. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
40. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
41. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
42. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
43. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
44. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
45. Diese Zeile rendert ein HTML-Element f?r die Benutzeroberfl?che.
46. Diese Zeile beendet den Content-Block des Templates.

## tools/diagnostics/check_umlauts.py
```python
from __future__ import annotations

import json
import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DE_JSON_PATH = PROJECT_ROOT / "app" / "i18n" / "locales" / "de.json"
TEMPLATES_DIR = PROJECT_ROOT / "app" / "templates"
REPORT_PATH = PROJECT_ROOT / "diagnostics" / "umlaut_report.md"

SUSPICIOUS_TOKENS = (
    "aender",
    "aufgeloes",
    "bestaetig",
    "fuer",
    "groesse",
    "gueltig",
    "koennen",
    "loesch",
    "pruef",
    "ueber",
    "uebersetz",
    "uebersprungen",
    "ungueltig",
    "unterstuetz",
    "veroeff",
    "zurueck",
)

TOKEN_REGEX = re.compile("|".join(re.escape(token) for token in SUSPICIOUS_TOKENS), re.IGNORECASE)
QUESTION_MARK_REGEX = re.compile(
    r"[A-Za-zÄÖÜäöüß]\?[A-Za-zÄÖÜäöüß]|^\?[A-Za-zÄÖÜäöüß]"
)


def scan_de_json() -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    data = json.loads(DE_JSON_PATH.read_text(encoding="utf-8"))
    for key, value in sorted(data.items(), key=lambda item: item[0]):
        text = str(value)
        if TOKEN_REGEX.search(text) or QUESTION_MARK_REGEX.search(text):
            issues.append((key, text))
    return issues


def scan_templates() -> list[tuple[str, int, str]]:
    issues: list[tuple[str, int, str]] = []
    for file_path in sorted(TEMPLATES_DIR.rglob("*.html")):
        rel = file_path.relative_to(PROJECT_ROOT).as_posix()
        lines = file_path.read_text(encoding="utf-8").splitlines()
        for index, line in enumerate(lines, start=1):
            has_url_attribute = any(
                marker in line for marker in ('href="', 'action="', 'hx-get="', 'hx-post="')
            )
            has_question_issue = bool(QUESTION_MARK_REGEX.search(line)) and not has_url_attribute
            if TOKEN_REGEX.search(line) or has_question_issue:
                issues.append((rel, index, line.strip()))
    return issues


def write_report(json_issues: list[tuple[str, str]], template_issues: list[tuple[str, int, str]]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    lines.append("# Umlaut Report")
    lines.append("")
    lines.append("Dieser Report listet potenzielle Ersatzschreibungen in UI-Texten auf.")
    lines.append("")
    lines.append("## de.json")
    lines.append(f"- Treffer: {len(json_issues)}")
    lines.append("")
    if json_issues:
        lines.append("| Key | Wert |")
        lines.append("| --- | --- |")
        for key, value in json_issues:
            safe_value = value.replace("|", "\\|")
            lines.append(f"| `{key}` | {safe_value} |")
    else:
        lines.append("Keine auffälligen Strings gefunden.")
    lines.append("")
    lines.append("## Templates")
    lines.append(f"- Treffer: {len(template_issues)}")
    lines.append("")
    if template_issues:
        lines.append("| Datei | Zeile | Inhalt |")
        lines.append("| --- | ---: | --- |")
        for rel, line_no, content in template_issues:
            safe_content = content.replace("|", "\\|")
            lines.append(f"| `{rel}` | {line_no} | {safe_content} |")
    else:
        lines.append("Keine auffälligen Strings gefunden.")
    lines.append("")
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    json_issues = scan_de_json()
    template_issues = scan_templates()
    write_report(json_issues, template_issues)
    print(f"Report written: {REPORT_PATH}")
    print(f"de.json issues: {len(json_issues)}")
    print(f"template issues: {len(template_issues)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```
ZEILEN-ERKL?RUNG
1. Diese Zeile importiert ein ben?tigtes Python-Modul.
2. Diese Zeile ist absichtlich leer, um die Lesbarkeit zu verbessern.
3. Diese Zeile importiert ein ben?tigtes Python-Modul.
4. Diese Zeile importiert ein ben?tigtes Python-Modul.
5. Diese Zeile importiert ein ben?tigtes Python-Modul.
6. Diese Zeile ist absichtlich leer, um die Lesbarkeit zu verbessern.
7. Diese Zeile ist absichtlich leer, um die Lesbarkeit zu verbessern.
8. Diese Zeile enth?lt Programmlogik f?r den Umlaut-Diagnosecheck.
9. Diese Zeile enth?lt Programmlogik f?r den Umlaut-Diagnosecheck.
10. Diese Zeile enth?lt Programmlogik f?r den Umlaut-Diagnosecheck.
11. Diese Zeile enth?lt Programmlogik f?r den Umlaut-Diagnosecheck.
12. Diese Zeile ist absichtlich leer, um die Lesbarkeit zu verbessern.
13. Diese Zeile enth?lt Programmlogik f?r den Umlaut-Diagnosecheck.
14. Diese Zeile enth?lt Programmlogik f?r den Umlaut-Diagnosecheck.
15. Diese Zeile enth?lt Programmlogik f?r den Umlaut-Diagnosecheck.
16. Diese Zeile enth?lt Programmlogik f?r den Umlaut-Diagnosecheck.
17. Diese Zeile enth?lt Programmlogik f?r den Umlaut-Diagnosecheck.
18. Diese Zeile enth?lt Programmlogik f?r den Umlaut-Diagnosecheck.
19. Diese Zeile enth?lt Programmlogik f?r den Umlaut-Diagnosecheck.
20. Diese Zeile enth?lt Programmlogik f?r den Umlaut-Diagnosecheck.
21. Diese Zeile enth?lt Programmlogik f?r den Umlaut-Diagnosecheck.
22. Diese Zeile enth?lt Programmlogik f?r den Umlaut-Diagnosecheck.
23. Diese Zeile enth?lt Programmlogik f?r den Umlaut-Diagnosecheck.
24. Diese Zeile enth?lt Programmlogik f?r den Umlaut-Diagnosecheck.
25. Diese Zeile enth?lt Programmlogik f?r den Umlaut-Diagnosecheck.
26. Diese Zeile enth?lt Programmlogik f?r den Umlaut-Diagnosecheck.
27. Diese Zeile enth?lt Programmlogik f?r den Umlaut-Diagnosecheck.
28. Diese Zeile enth?lt Programmlogik f?r den Umlaut-Diagnosecheck.
29. Diese Zeile enth?lt Programmlogik f?r den Umlaut-Diagnosecheck.
30. Diese Zeile enth?lt Programmlogik f?r den Umlaut-Diagnosecheck.
31. Diese Zeile ist absichtlich leer, um die Lesbarkeit zu verbessern.
32. Diese Zeile enth?lt Programmlogik f?r den Umlaut-Diagnosecheck.
33. Diese Zeile enth?lt Programmlogik f?r den Umlaut-Diagnosecheck.
34. Diese Zeile enth?lt Programmlogik f?r den Umlaut-Diagnosecheck.
35. Diese Zeile enth?lt Programmlogik f?r den Umlaut-Diagnosecheck.
36. Diese Zeile ist absichtlich leer, um die Lesbarkeit zu verbessern.
37. Diese Zeile ist absichtlich leer, um die Lesbarkeit zu verbessern.
38. Diese Zeile definiert eine Python-Funktion im Diagnosewerkzeug.
39. Diese Zeile enth?lt Programmlogik f?r den Umlaut-Diagnosecheck.
40. Diese Zeile enth?lt Programmlogik f?r den Umlaut-Diagnosecheck.
41. Diese Zeile enth?lt Programmlogik f?r den Umlaut-Diagnosecheck.
42. Diese Zeile enth?lt Programmlogik f?r den Umlaut-Diagnosecheck.
43. Diese Zeile enth?lt Programmlogik f?r den Umlaut-Diagnosecheck.
44. Diese Zeile enth?lt Programmlogik f?r den Umlaut-Diagnosecheck.
45. Diese Zeile enth?lt Programmlogik f?r den Umlaut-Diagnosecheck.
46. Diese Zeile ist absichtlich leer, um die Lesbarkeit zu verbessern.
47. Diese Zeile ist absichtlich leer, um die Lesbarkeit zu verbessern.
48. Diese Zeile definiert eine Python-Funktion im Diagnosewerkzeug.
49. Diese Zeile enth?lt Programmlogik f?r den Umlaut-Diagnosecheck.
50. Diese Zeile enth?lt Programmlogik f?r den Umlaut-Diagnosecheck.
51. Diese Zeile enth?lt Programmlogik f?r den Umlaut-Diagnosecheck.
52. Diese Zeile enth?lt Programmlogik f?r den Umlaut-Diagnosecheck.
53. Diese Zeile enth?lt Programmlogik f?r den Umlaut-Diagnosecheck.
54. Diese Zeile enth?lt Programmlogik f?r den Umlaut-Diagnosecheck.
55. Diese Zeile enth?lt Programmlogik f?r den Umlaut-Diagnosecheck.
56. Diese Zeile enth?lt Programmlogik f?r den Umlaut-Diagnosecheck.
57. Diese Zeile enth?lt Programmlogik f?r den Umlaut-Diagnosecheck.
58. Diese Zeile enth?lt Programmlogik f?r den Umlaut-Diagnosecheck.
59. Diese Zeile enth?lt Programmlogik f?r den Umlaut-Diagnosecheck.
60. Diese Zeile enth?lt Programmlogik f?r den Umlaut-Diagnosecheck.
61. Diese Zeile ist absichtlich leer, um die Lesbarkeit zu verbessern.
62. Diese Zeile ist absichtlich leer, um die Lesbarkeit zu verbessern.
63. Diese Zeile definiert eine Python-Funktion im Diagnosewerkzeug.
64. Diese Zeile enth?lt Programmlogik f?r den Umlaut-Diagnosecheck.
65. Diese Zeile enth?lt Programmlogik f?r den Umlaut-Diagnosecheck.
66. Diese Zeile enth?lt Programmlogik f?r den Umlaut-Diagnosecheck.
67. Diese Zeile enth?lt Programmlogik f?r den Umlaut-Diagnosecheck.
68. Diese Zeile enth?lt Programmlogik f?r den Umlaut-Diagnosecheck.
69. Diese Zeile enth?lt Programmlogik f?r den Umlaut-Diagnosecheck.
70. Diese Zeile enth?lt Programmlogik f?r den Umlaut-Diagnosecheck.
71. Diese Zeile enth?lt Programmlogik f?r den Umlaut-Diagnosecheck.
72. Diese Zeile enth?lt Programmlogik f?r den Umlaut-Diagnosecheck.
73. Diese Zeile enth?lt Programmlogik f?r den Umlaut-Diagnosecheck.
74. Diese Zeile enth?lt Programmlogik f?r den Umlaut-Diagnosecheck.
75. Diese Zeile enth?lt Programmlogik f?r den Umlaut-Diagnosecheck.
76. Diese Zeile enth?lt Programmlogik f?r den Umlaut-Diagnosecheck.
77. Diese Zeile enth?lt Programmlogik f?r den Umlaut-Diagnosecheck.
78. Diese Zeile enth?lt Programmlogik f?r den Umlaut-Diagnosecheck.
79. Diese Zeile enth?lt Programmlogik f?r den Umlaut-Diagnosecheck.
80. Diese Zeile enth?lt Programmlogik f?r den Umlaut-Diagnosecheck.
81. Diese Zeile enth?lt Programmlogik f?r den Umlaut-Diagnosecheck.
82. Diese Zeile enth?lt Programmlogik f?r den Umlaut-Diagnosecheck.
83. Diese Zeile enth?lt Programmlogik f?r den Umlaut-Diagnosecheck.
84. Diese Zeile enth?lt Programmlogik f?r den Umlaut-Diagnosecheck.
85. Diese Zeile enth?lt Programmlogik f?r den Umlaut-Diagnosecheck.
86. Diese Zeile enth?lt Programmlogik f?r den Umlaut-Diagnosecheck.
87. Diese Zeile enth?lt Programmlogik f?r den Umlaut-Diagnosecheck.
88. Diese Zeile enth?lt Programmlogik f?r den Umlaut-Diagnosecheck.
89. Diese Zeile enth?lt Programmlogik f?r den Umlaut-Diagnosecheck.
90. Diese Zeile enth?lt Programmlogik f?r den Umlaut-Diagnosecheck.
91. Diese Zeile enth?lt Programmlogik f?r den Umlaut-Diagnosecheck.
92. Diese Zeile enth?lt Programmlogik f?r den Umlaut-Diagnosecheck.
93. Diese Zeile enth?lt Programmlogik f?r den Umlaut-Diagnosecheck.
94. Diese Zeile enth?lt Programmlogik f?r den Umlaut-Diagnosecheck.
95. Diese Zeile ist absichtlich leer, um die Lesbarkeit zu verbessern.
96. Diese Zeile ist absichtlich leer, um die Lesbarkeit zu verbessern.
97. Diese Zeile definiert eine Python-Funktion im Diagnosewerkzeug.
98. Diese Zeile enth?lt Programmlogik f?r den Umlaut-Diagnosecheck.
99. Diese Zeile enth?lt Programmlogik f?r den Umlaut-Diagnosecheck.
100. Diese Zeile enth?lt Programmlogik f?r den Umlaut-Diagnosecheck.
101. Diese Zeile enth?lt Programmlogik f?r den Umlaut-Diagnosecheck.
102. Diese Zeile enth?lt Programmlogik f?r den Umlaut-Diagnosecheck.
103. Diese Zeile enth?lt Programmlogik f?r den Umlaut-Diagnosecheck.
104. Diese Zeile enth?lt Programmlogik f?r den Umlaut-Diagnosecheck.
105. Diese Zeile ist absichtlich leer, um die Lesbarkeit zu verbessern.
106. Diese Zeile ist absichtlich leer, um die Lesbarkeit zu verbessern.
107. Diese Zeile startet den direkten Skriptaufruf im CLI-Modus.
108. Diese Zeile enth?lt Programmlogik f?r den Umlaut-Diagnosecheck.
