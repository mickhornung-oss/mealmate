from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from pathlib import Path
import re


PROJECT_ROOT = Path(__file__).resolve().parents[2]
REPORT_PATH = PROJECT_ROOT / "diagnostics" / "encoding_audit.md"

SCAN_GLOBS = (
    "app/**/*.py",
    "app/templates/**/*.html",
    "app/static/**/*.css",
    "app/static/**/*.js",
    "app/i18n/**/*.json",
    "app/i18n/**/*.py",
    "tests/**/*.py",
    "alembic/**/*.py",
    "migrations/**/*.py",
)

SUSPICIOUS_UI_TOKENS = (
    "zurueck",
    "uebersetz",
    "veroeff",
    "aender",
    "loesch",
    "grossbuchstaben",
    "fruehst",
    "oeffent",
    "ueber",
    "fuer",
    "gueltig",
    "pruef",
)

SUSPICIOUS_TOKEN_REGEX = re.compile(
    r"(?i)\b(" + "|".join(re.escape(token) for token in SUSPICIOUS_UI_TOKENS) + r")\w*\b"
)

SKIP_DIR_NAMES = {
    ".git",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    "node_modules",
}


@dataclass
class DecodeIssue:
    path: str
    reason: str
    guessed_encoding: str | None = None


@dataclass
class TextIssue:
    path: str
    line: int
    issue: str
    snippet: str


@dataclass
class AuditReport:
    decode_issues: list[DecodeIssue] = field(default_factory=list)
    replacement_issues: list[TextIssue] = field(default_factory=list)
    suspicious_issues: list[TextIssue] = field(default_factory=list)
    scanned_files: int = 0

    @property
    def has_errors(self) -> bool:
        return bool(self.decode_issues or self.replacement_issues or self.suspicious_issues)


def _guess_encoding(raw_bytes: bytes) -> str | None:
    try:
        import charset_normalizer  # type: ignore

        match = charset_normalizer.from_bytes(raw_bytes).best()
        if match and match.encoding:
            return str(match.encoding)
    except Exception:
        pass
    try:
        import chardet  # type: ignore

        detected = chardet.detect(raw_bytes)
        encoding = detected.get("encoding")
        return str(encoding) if encoding else None
    except Exception:
        return None


def _iter_target_files() -> list[Path]:
    files: dict[str, Path] = {}
    for pattern in SCAN_GLOBS:
        for path in PROJECT_ROOT.glob(pattern):
            if not path.is_file():
                continue
            if any(part in SKIP_DIR_NAMES for part in path.parts):
                continue
            files[str(path)] = path
    return sorted(files.values(), key=lambda item: str(item).lower())


def _is_ui_like_file(path: Path) -> bool:
    rel = path.relative_to(PROJECT_ROOT).as_posix()
    if rel == "app/i18n/locales/de.json":
        return True
    return rel.startswith("app/templates/") or rel.startswith("app/routers/")


def run_audit() -> AuditReport:
    report = AuditReport()
    for file_path in _iter_target_files():
        report.scanned_files += 1
        rel = file_path.relative_to(PROJECT_ROOT).as_posix()
        raw = file_path.read_bytes()
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            report.decode_issues.append(
                DecodeIssue(
                    path=rel,
                    reason=f"utf-8 decode failed at byte {exc.start}",
                    guessed_encoding=_guess_encoding(raw),
                )
            )
            continue

        lines = text.splitlines()
        for line_no, line in enumerate(lines, start=1):
            if "\ufffd" in line:
                report.replacement_issues.append(
                    TextIssue(
                        path=rel,
                        line=line_no,
                        issue="contains replacement character U+FFFD",
                        snippet=line.strip()[:200],
                    )
                )
            if _is_ui_like_file(file_path):
                if SUSPICIOUS_TOKEN_REGEX.search(line):
                    if "http://" in line or "https://" in line:
                        continue
                    report.suspicious_issues.append(
                        TextIssue(
                            path=rel,
                            line=line_no,
                            issue="suspicious umlaut replacement token",
                            snippet=line.strip()[:200],
                        )
                    )
    return report


def _render_markdown(report: AuditReport) -> str:
    lines: list[str] = []
    lines.append("# Encoding Audit")
    lines.append("")
    lines.append(f"- Scanned files: {report.scanned_files}")
    lines.append(f"- Decode issues: {len(report.decode_issues)}")
    lines.append(f"- Replacement char issues: {len(report.replacement_issues)}")
    lines.append(f"- Suspicious UI transliteration issues: {len(report.suspicious_issues)}")
    lines.append("")

    lines.append("## Decode Issues")
    if report.decode_issues:
        lines.append("")
        lines.append("| File | Reason | Guessed Encoding |")
        lines.append("| --- | --- | --- |")
        for item in report.decode_issues:
            guessed = item.guessed_encoding or "-"
            lines.append(f"| `{item.path}` | {item.reason} | {guessed} |")
    else:
        lines.append("")
        lines.append("Keine Decode-Probleme gefunden.")
    lines.append("")

    lines.append("## Replacement Character Issues")
    if report.replacement_issues:
        lines.append("")
        lines.append("| File | Line | Snippet |")
        lines.append("| --- | ---: | --- |")
        for item in report.replacement_issues:
            snippet = item.snippet.replace("|", "\\|")
            lines.append(f"| `{item.path}` | {item.line} | {snippet} |")
    else:
        lines.append("")
        lines.append("Keine U+FFFD-Zeichen gefunden.")
    lines.append("")

    lines.append("## Suspicious UI Transliteration Issues")
    if report.suspicious_issues:
        lines.append("")
        lines.append("| File | Line | Snippet |")
        lines.append("| --- | ---: | --- |")
        for item in report.suspicious_issues:
            snippet = item.snippet.replace("|", "\\|")
            lines.append(f"| `{item.path}` | {item.line} | {snippet} |")
    else:
        lines.append("")
        lines.append("Keine verdächtigen UI-Ersatzschreibungen gefunden.")
    lines.append("")
    return "\n".join(lines)


def write_report(report: AuditReport) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(_render_markdown(report), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="UTF-8 audit for MealMate source files")
    parser.add_argument(
        "--report-path",
        default=str(REPORT_PATH),
        help="Path to write markdown report (default: diagnostics/encoding_audit.md)",
    )
    args = parser.parse_args(argv)

    report = run_audit()
    output_path = Path(args.report_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(_render_markdown(report), encoding="utf-8")

    print(f"[encoding-audit] scanned_files={report.scanned_files}")
    print(f"[encoding-audit] decode_issues={len(report.decode_issues)}")
    print(f"[encoding-audit] replacement_issues={len(report.replacement_issues)}")
    print(f"[encoding-audit] suspicious_ui_issues={len(report.suspicious_issues)}")
    print(f"[encoding-audit] report={output_path}")

    return 1 if report.has_errors else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
