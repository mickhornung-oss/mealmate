from __future__ import annotations

from sqlalchemy import Table

from app import models  # noqa: F401
from app.database import Base


def _column_type(column) -> str:
    try:
        return str(column.type)
    except Exception:
        return column.type.__class__.__name__


def _foreign_keys(column) -> str:
    if not column.foreign_keys:
        return "-"
    targets = sorted(fk.target_fullname for fk in column.foreign_keys)
    return ", ".join(targets)


def _print_table(table: Table) -> None:
    print(f"## {table.name}")
    print()
    print("| COLUMN | TYPE | NULLABLE | PK | FK |")
    print("|---|---|---|---|---|")
    for column in table.columns:
        name = column.name
        ctype = _column_type(column)
        nullable = "yes" if column.nullable else "no"
        primary = "yes" if column.primary_key else "no"
        foreign = _foreign_keys(column)
        print(f"| {name} | {ctype} | {nullable} | {primary} | {foreign} |")
    print()


def main() -> None:
    print("# Database Schema")
    print()
    tables = sorted(Base.metadata.tables.values(), key=lambda item: item.name)
    for table in tables:
        _print_table(table)


if __name__ == "__main__":
    main()
