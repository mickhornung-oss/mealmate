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
