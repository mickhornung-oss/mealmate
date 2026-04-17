# Email Change

## Zweck

Dieses Modul fuegt eine sichere E-Mail-Aenderung mit Bestaetigungslink hinzu.
Die E-Mail wird erst aktualisiert, nachdem der Link auf der neuen Adresse bestaetigt wurde.

## Ablauf

1. Eingeloggter User oeffnet `GET /auth/change-email`.
2. `POST /auth/change-email/request` prueft die neue E-Mail und erstellt ein Single-Use-Token.
3. Der Link `{APP_URL}/auth/change-email/confirm?token=<raw_token>` wird an die neue E-Mail gesendet.
4. `GET /auth/change-email/confirm` validiert das Token und zeigt die Bestaetigungsseite.
5. `POST /auth/change-email/confirm` aktualisiert `users.email` und markiert das Token als verwendet.

## Sicherheit

- Raw-Token wird nie in der Datenbank gespeichert, nur `token_hash`.
- Token sind single-use (`used_at`) und laufen ab (`expires_at`).
- Alle POST-Routen sind CSRF-geschuetzt.
- Rate-Limits:
  - `POST /auth/change-email/request`: `3/min` pro User und `5/min` pro IP
  - `POST /auth/change-email/confirm`: `5/min` pro IP
- Konflikte werden als "E-Mail nicht verfuegbar" behandelt.

## Datenmodell

Es wird die bestehende Tabelle `password_reset_tokens` wiederverwendet:

- `purpose = "email_change"`
- `new_email_normalized` speichert die angeforderte Zieladresse

Migration: `20260303_0008_email_change_token_field.py`

## ENV-Variablen

- `APP_URL` (z. B. `http://127.0.0.1:8010`)
- `PASSWORD_RESET_TOKEN_MINUTES` (gilt auch fuer E-Mail-Aenderungstoken)
- `MAIL_OUTBOX_EMAIL_CHANGE_PATH` (DEV-Outbox-Datei)
- SMTP in PROD:
  - `SMTP_HOST`
  - `SMTP_PORT`
  - `SMTP_USER`
  - `SMTP_PASSWORD`
  - `SMTP_FROM`

## DEV-Mailer

In `APP_ENV=dev` wird der Link in `MAIL_OUTBOX_EMAIL_CHANGE_PATH` geschrieben.
In `APP_ENV=prod` wird ueber SMTP gesendet.

## Tests

`tests/test_email_change.py` deckt ab:

- Token-Erstellung + Outbox-Versand
- Erfolgreiche Bestaetigung mit Single-Use-Verhalten
- Konfliktfall bei bereits vergebener E-Mail
- Ablauf eines abgelaufenen Tokens
