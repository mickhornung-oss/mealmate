from __future__ import annotations

import argparse
import re
from collections import defaultdict, deque
from pathlib import Path

EXCLUDE_PARTS = {".git", ".venv", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", "htmlcov"}
TEMPLATE_EXT = ".html"

PY_TEMPLATE_PATTERNS = [
    re.compile(r'TemplateResponse\(\s*"([^"]+)"'),
    re.compile(r"TemplateResponse\(\s*'([^']+)'"),
]

JINJA_REF_PATTERNS = [
    re.compile(r'{%\s*extends\s*"([^"]+)"\s*%}'),
    re.compile(r"{%\s*extends\s*'([^']+)'\s*%}"),
    re.compile(r'{%\s*include\s*"([^"]+)"'),
    re.compile(r"{%\s*include\s*'([^']+)'"),
    re.compile(r'{%\s*import\s*"([^"]+)"'),
    re.compile(r"{%\s*import\s*'([^']+)'"),
    re.compile(r'{%\s*from\s*"([^"]+)"'),
    re.compile(r"{%\s*from\s*'([^']+)'"),
]

STATIC_PATTERNS = [
    re.compile(r'src="/static/([^"]+)"'),
    re.compile(r"src='/static/([^']+)'"),
    re.compile(r'href="/static/([^"]+)"'),
    re.compile(r"href='/static/([^']+)'"),
    re.compile(r'url_for\(\s*"static"\s*,\s*path\s*=\s*"([^"]+)"\s*\)'),
    re.compile(r"url_for\(\s*'static'\s*,\s*path\s*=\s*'([^']+)'\s*\)"),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Find potentially unused templates/static files.")
    parser.add_argument("--output", default="docs/CLEANUP_AUDIT.md", help="Report output path.")
    parser.add_argument("--stdout", action="store_true", help="Also print report to stdout.")
    return parser.parse_args()


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def should_skip(path: Path) -> bool:
    return any(part in EXCLUDE_PARTS for part in path.parts)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="latin-1", errors="ignore")


def collect_template_roots_from_python(root: Path) -> set[str]:
    template_roots: set[str] = set()
    for py_file in root.rglob("*.py"):
        if should_skip(py_file):
            continue
        text = read_text(py_file)
        for pattern in PY_TEMPLATE_PATTERNS:
            for match in pattern.findall(text):
                if match.endswith(TEMPLATE_EXT):
                    template_roots.add(match)
    return template_roots


def collect_template_graph(templates_dir: Path) -> tuple[dict[str, set[str]], set[str]]:
    graph: dict[str, set[str]] = defaultdict(set)
    all_templates: set[str] = set()
    for template_file in templates_dir.rglob(f"*{TEMPLATE_EXT}"):
        rel = template_file.relative_to(templates_dir).as_posix()
        all_templates.add(rel)
        text = read_text(template_file)
        for pattern in JINJA_REF_PATTERNS:
            for ref in pattern.findall(text):
                if ref.endswith(TEMPLATE_EXT):
                    graph[rel].add(ref)
    return graph, all_templates


def walk_reachable_templates(roots: set[str], graph: dict[str, set[str]]) -> set[str]:
    reachable: set[str] = set()
    queue: deque[str] = deque(sorted(roots))
    while queue:
        current = queue.popleft()
        if current in reachable:
            continue
        reachable.add(current)
        for nxt in graph.get(current, set()):
            if nxt not in reachable:
                queue.append(nxt)
    return reachable


def collect_static_references(templates_dir: Path) -> set[str]:
    refs: set[str] = set()
    for template_file in templates_dir.rglob(f"*{TEMPLATE_EXT}"):
        text = read_text(template_file)
        for pattern in STATIC_PATTERNS:
            for match in pattern.findall(text):
                refs.add(match.lstrip("/"))
    return refs


def collect_static_files(static_dir: Path) -> set[str]:
    items: set[str] = set()
    if not static_dir.exists():
        return items
    for static_file in static_dir.rglob("*"):
        if static_file.is_file():
            items.add(static_file.relative_to(static_dir).as_posix())
    return items


def markdown_list(items: list[str], empty_message: str) -> str:
    if not items:
        return f"- {empty_message}"
    return "\n".join(f"- {item}" for item in items)


def build_report(root: Path) -> str:
    templates_dir = root / "app" / "templates"
    static_dir = root / "app" / "static"

    template_roots = collect_template_roots_from_python(root)
    graph, all_templates = collect_template_graph(templates_dir)
    reachable_templates = walk_reachable_templates(template_roots, graph)
    not_referenced_templates = sorted(all_templates - reachable_templates)

    static_refs = collect_static_references(templates_dir)
    static_files = collect_static_files(static_dir)
    not_referenced_static = sorted(static_files - static_refs)

    lines = [
        "# Cleanup Audit",
        "",
        "> Safety note: This is a candidate list only; files are not deleted automatically.",
        "",
        "## Template Reachability",
        f"- Total templates: {len(all_templates)}",
        f"- Roots found in Python routes/views: {len(template_roots)}",
        f"- Reachable templates: {len(reachable_templates)}",
        f"- Candidate unused templates: {len(not_referenced_templates)}",
        "",
        "### Candidate Unused Templates",
        markdown_list(not_referenced_templates, "No template candidates found."),
        "",
        "## Static File Reachability",
        f"- Total static files: {len(static_files)}",
        f"- Referenced static paths in templates: {len(static_refs)}",
        f"- Candidate unused static files: {len(not_referenced_static)}",
        "",
        "### Candidate Unused Static Files",
        markdown_list(not_referenced_static, "No static candidates found."),
        "",
        "## Next Safe Step",
        "- Review each candidate manually before moving files to `_archive/`.",
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()
    root = project_root()
    report = build_report(root)
    output_path = Path(args.output)
    if not output_path.is_absolute():
        output_path = (root / output_path).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding="utf-8")
    print(f"[done] report written: {output_path}")
    if args.stdout:
        print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
