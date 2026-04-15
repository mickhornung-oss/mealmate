# MealMate Roadmap

Diese Roadmap priorisiert Stabilitaet, Beta-Qualitaet und danach Produktreife.

## Phase 1: Blocker und Stabilitaet (P0)

Zieldefinition:
- Keine kritischen Publish- oder Rechteverletzungen mehr.
- Kernflows fuer User und Admin sind reproduzierbar testbar.

Aufgaben:
1. Publish-Guards dauerhaft absichern (User darf nie direkt publizieren).
2. Moderationsstatus in allen Listings und APIs konsistent erzwingen.
3. E2E Testlauf in lokaler Umgebung stabilisieren (Playwright installiert, reproduzierbar).
4. Fehlerseiten und Fehlermeldungen in Kernflows vereinheitlichen.

Definition of Done:
- `pytest -q` ist gruen.
- Manuelle QA fuer User/Admin Kernjourneys ist Pass.
- Kein bekannter P0 Bug offen.

## Phase 2: Beta Qualitaet (P1)

Zieldefinition:
- Produkt ist fuer externe Beta-Nutzer robust und nachvollziehbar.

Aufgaben:
1. Moderations-Dashboard Usability verbessern (bessere Filter, schnellere Queue-Aktionen).
2. CSV Import Report UX schaerfen (klare Fatal/Warn-Visualisierung).
3. Security Monitoring erweitern (mehr auditierbare Events ohne PII-Leak).
4. Testabdeckung fuer edge cases erhoehen (z. B. parallele Moderation, doppelte Aktionen).

Definition of Done:
- Keine offenen P1 Bugs mit reproduzierbarem Workaround.
- QA Beta Checklist komplett Pass.
- Beta-Dokumentation aktuell und fuer Tester nutzbar.

## Phase 3: UX und Polish (P2)

Zieldefinition:
- Bedienung ist bei grossem Datenbestand effizient und visuell konsistent.

Aufgaben:
1. Discover Performance bei vielen Rezepten verbessern (Query-Optimierungen, Caching wo sinnvoll).
2. Form UX vereinheitlichen (Inline-Feedback, bessere Fehlermeldungspositionierung).
3. Bilder-Workflow fuer User klarer machen (Status-Hinweise und Verlauf von Bildantraegen).
4. PDF Layout feiner abstimmen (Abstaende, optionale Bildskalierung).

Definition of Done:
- Nutzertests bestaetigen bessere Orientierung und geringere Klickwege.
- Keine regressiven Effekte auf Security und Moderation.

## Phase 4: Deploy, Staging, Monitoring (P2/P3)

Zieldefinition:
- Betrieb auf oeffentlicher Infrastruktur ist nachvollziehbar, messbar und wartbar.

Aufgaben:
1. Staging-Umgebung mit Postgres und realistischen Seed-Daten standardisieren.
2. Runtime Monitoring und Alerting vorbereiten (Fehlerquote, Response-Zeiten, Rate-Limit-Spikes).
3. Backup/Restore Prozess fuer produktive DB dokumentieren.
4. Release-Prozess mit Versionierung und Change-Kommunikation finalisieren.

Definition of Done:
- Staging kann jederzeit neu aufgebaut werden.
- Deploy-Ablauf ist als Checkliste dokumentiert und reproduzierbar.
- Monitoring deckt kritische Betriebsmetriken ab.
