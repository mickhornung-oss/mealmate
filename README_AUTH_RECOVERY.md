# MealMate Auth & Account Recovery

## Features

- Login per E-Mail oder Benutzername.
- Jeder User besitzt `user_uid` (UUID, nicht erratbar).
- Username setzen/aendern mit Validierung und Eindeutigkeit.
- Passwort aendern im Profil.
- Passwort vergessen + Reset-Link mit Single-Use-Token.
- Schlanke Security-Events fuer Login/Reset/Username/Password.

## Datenmodell

- `users`:
  - `user_uid`, `username`, `username_normalized`
  - `last_login_at`, `last_login_ip`, `last_login_user_agent`
- `password_reset_tokens`:
  - nur `token_hash` gespeichert (nie Raw-Token)
  - `expires_at` (30 Minuten), `used_at` fuer Single-Use
- `security_events`:
  - minimale Audit-Daten, automatisch begrenzt

## Login

- Feld: `E-Mail oder Benutzername`
- Lookup:
  - mit `@` => `email`
  - sonst => `username_normalized`
- Fehler immer generisch.

## Passwort-Reset

1. `GET/POST /auth/forgot-password`
2. Antwort immer gleich (kein Account-Leak)
3. Bei vorhandenem User:
   - Token erzeugen
   - nur Hash speichern
   - Link `{APP_URL}/auth/reset-password?token=<raw>`
4. `GET/POST /auth/reset-password`
5. Token wird nach Nutzung auf `used_at` gesetzt

## Mail-Versand

- DEV: Outbox-Datei (`MAIL_OUTBOX_PATH`)
- PROD: SMTP (`SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM`)
- In PROD wird der Raw-Token nicht geloggt.

## Rate Limits

- `POST /auth/login`: `5/min` pro IP
- `POST /auth/forgot-password`: `5/min` pro IP
- `POST /auth/reset-password`: `5/min` pro IP
- `POST /auth/change-password`: `3/min` pro User
- `POST /profile/username`: `5/min` pro User

## Tests

`tests/test_auth_recovery.py` deckt ab:

- Login mit E-Mail und Username
- Forgot-Password ohne Existence-Leak
- Reset-Token Single-Use
- Passwortwechsel mit Pflicht auf altes Passwort
- Username Pattern + Unique
- `user_uid` fuer neue Nutzer
