# MealMate Security Checklist

Diese Checkliste hilft beim manuellen Test der Production-Sicherheitsfunktionen.

## 1) Login Rate Limit

1. Sende 6 Login-POSTs innerhalb von 1 Minute an `/login`.
2. Erwartung: Die ersten 5 Requests werden normal verarbeitet.
3. Erwartung: Der 6. Request liefert `429 Too Many Requests`.
4. Erwartung: Response enthaelt Rate-Limit Header (z. B. `X-RateLimit-*`).

## 2) Register Rate Limit

1. Sende 4 Register-POSTs innerhalb von 1 Minute an `/register`.
2. Erwartung: Nach 3 Requests greift der Limiter.
3. Erwartung: Der 4. Request liefert `429`.

## 3) CSRF Schutz ohne Token

1. Oeffne eine geschuetzte POST-Route ohne `csrf_token` Feld oder `X-CSRF-Token` Header.
2. Beispiel: `curl -X POST http://localhost:8000/logout`.
3. Erwartung: Response `403` mit Hinweis auf fehlgeschlagene CSRF-Validierung.

## 4) CSRF Schutz mit Token

1. Lade zuerst eine GET-Seite, damit `csrf_token` Cookie gesetzt wird.
2. Sende dann POST mit passendem Header `X-CSRF-Token: <cookie-wert>`.
3. Erwartung: Request wird normal akzeptiert (`200` oder Redirect `303`).

## 5) Security Headers

1. Fuehre `curl -I http://localhost:8000/` aus.
2. Erwartung: Header enthalten mindestens:
3. `Content-Security-Policy`
4. `X-Content-Type-Options: nosniff`
5. `X-Frame-Options: DENY`
6. `Referrer-Policy: strict-origin-when-cross-origin`
7. `Permissions-Policy: geolocation=(), microphone=(), camera=()`
8. In Prod/HTTPS zusaetzlich `Strict-Transport-Security`.

## 6) Bild-Upload Hardening

1. Lade eine Datei mit falschem MIME-Typ hoch.
2. Erwartung: `400 Bad Request`.
3. Lade ein Bild groesser als `MAX_UPLOAD_MB` hoch.
4. Erwartung: `413 Request Entity Too Large` oder klarer Fehler.
5. Lade ein Bild mit passendem MIME aber falschen Magic Bytes hoch.
6. Erwartung: `400 Bad Request`.

## 7) CSV Upload Hardening (Admin)

1. Lade eine CSV groesser als `MAX_CSV_UPLOAD_MB` hoch.
2. Erwartung: `413 Request Entity Too Large`.
3. Lade eine Datei ohne `.csv` Endung hoch.
4. Erwartung: `400 Bad Request`.
5. Pruefe, dass kein freier Dateipfad im Request verarbeitet wird.

## 8) Allowed Hosts

1. Setze in ENV `ALLOWED_HOSTS` auf eine feste Domain.
2. Sende einen Request mit falschem Host Header.
3. Erwartung: `400 Bad Request` durch TrustedHostMiddleware.

## 9) Request ID

1. Fuehre einen normalen Request auf `/` aus.
2. Erwartung: Response enthaelt Header `X-Request-ID`.
3. Pruefe Logs: dieselbe `request_id` ist im Request-Log sichtbar.
