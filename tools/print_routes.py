from __future__ import annotations

from collections.abc import Iterable

from fastapi.routing import APIRoute

from app.main import app


def _iter_dependency_calls(route: APIRoute) -> Iterable[object]:
    stack = list(route.dependant.dependencies)
    while stack:
        dependency = stack.pop()
        if dependency.call is not None:
            yield dependency.call
        stack.extend(dependency.dependencies)


def _is_admin_only(route: APIRoute) -> bool:
    for call in _iter_dependency_calls(route):
        name = getattr(call, "__name__", "")
        if name == "get_admin_user":
            return True
    return False


def _format_tags(route: APIRoute) -> str:
    if not route.tags:
        return "-"
    return ", ".join(str(tag) for tag in route.tags)


def _iter_route_rows() -> Iterable[tuple[str, str, str, str, str]]:
    collected: list[tuple[str, str, str, str, str]] = []
    for route in app.routes:
        if not isinstance(route, APIRoute):
            continue
        methods = sorted(method for method in route.methods or set() if method not in {"HEAD", "OPTIONS"})
        tags = _format_tags(route)
        admin_only = "yes" if _is_admin_only(route) else "no"
        for method in methods:
            collected.append((method, route.path, route.name, tags, admin_only))
    collected.sort(key=lambda item: (item[1], item[0]))
    return collected


def main() -> None:
    print("| METHOD | PATH | NAME | TAGS | ADMIN_ONLY |")
    print("|---|---|---|---|---|")
    for method, path, name, tags, admin_only in _iter_route_rows():
        print(f"| {method} | {path} | {name} | {tags} | {admin_only} |")


if __name__ == "__main__":
    main()
