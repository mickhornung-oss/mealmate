from __future__ import annotations

import json
from pathlib import Path


_LOCALE_FILE = Path(__file__).resolve().parent / "locales" / "de.json"
DE_TEXTS: dict[str, str] = json.loads(_LOCALE_FILE.read_text(encoding="utf-8"))

