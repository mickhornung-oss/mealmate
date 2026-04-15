from __future__ import annotations

import json
from pathlib import Path


DE_JSON_PATH = Path(__file__).resolve().parents[1] / "app" / "i18n" / "locales" / "de.json"


def test_de_i18n_critical_umlauts() -> None:
    data = json.loads(DE_JSON_PATH.read_text(encoding="utf-8"))
    assert data["pagination.previous"] == "Zurück"
    assert data["submission.save_changes"] == "Änderungen speichern"
    assert data["images.delete"] == "Löschen"
    assert data["nav.publish_recipe"] == "Rezept veröffentlichen"
    assert data["error.password_upper"] == "Das Passwort muss mindestens einen Großbuchstaben enthalten."


def test_de_i18n_contains_no_transliteration_fallback_for_core_labels() -> None:
    data = json.loads(DE_JSON_PATH.read_text(encoding="utf-8"))
    forbidden = ("Zurueck", "Aender", "Loesch", "Uebersetz", "Veroeff", "Grossbuchstaben")
    for key in [
        "pagination.previous",
        "submission.save_changes",
        "images.delete",
        "nav.publish_recipe",
        "error.password_upper",
    ]:
        value = data[key]
        assert not any(token in value for token in forbidden), f"{key} still contains transliteration fallback: {value}"

