"""align canonical category mappings with curated priority list

Revision ID: 20260304_0012
Revises: 20260304_0011
Create Date: 2026-03-04 13:35:00
"""

from datetime import datetime, timezone
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20260304_0012"
down_revision: Union[str, None] = "20260304_0011"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TARGET_MAPPINGS: list[tuple[int, str, str]] = [
    (10, "frühstück", "Frühstück"),
    (10, "brunch", "Frühstück"),
    (10, "müsli", "Frühstück"),
    (10, "porridge", "Frühstück"),
    (15, "mittag", "Mittagessen"),
    (15, "mittagessen", "Mittagessen"),
    (15, "lunch", "Mittagessen"),
    (15, "abend", "Abendessen"),
    (15, "abendessen", "Abendessen"),
    (15, "dinner", "Abendessen"),
    (20, "dessert", "Dessert"),
    (20, "nachspeise", "Dessert"),
    (20, "pudding", "Dessert"),
    (20, "creme", "Dessert"),
    (20, "eis", "Dessert"),
    (22, "kuchen", "Backen"),
    (22, "torte", "Backen"),
    (22, "plätzchen", "Backen"),
    (22, "gebäck", "Backen"),
    (22, "brot", "Backen"),
    (22, "bröt", "Backen"),
    (22, "hefe", "Backen"),
    (25, "suppe", "Suppe & Eintopf"),
    (25, "eintopf", "Suppe & Eintopf"),
    (25, "brühe", "Suppe & Eintopf"),
    (25, "gulasch", "Suppe & Eintopf"),
    (25, "chili", "Suppe & Eintopf"),
    (30, "salat", "Salat"),
    (35, "getränk", "Getränke"),
    (35, "cocktail", "Getränke"),
    (35, "smoothie", "Getränke"),
    (35, "saft", "Getränke"),
    (35, "tee", "Getränke"),
    (35, "kaffee", "Getränke"),
    (40, "beilage", "Beilage"),
    (40, "sauce", "Beilage"),
    (40, "dip", "Beilage"),
    (40, "pesto", "Beilage"),
    (40, "knödel", "Beilage"),
    (40, "kartoffel", "Beilage"),
    (40, "reis", "Beilage"),
    (45, "snack", "Snack"),
    (45, "fingerfood", "Snack"),
    (45, "häpp", "Snack"),
    (45, "wrap", "Snack"),
    (90, "vegetar", "Hauptgericht"),
    (90, "vegan", "Hauptgericht"),
    (999, "schwierig", "__IGNORE__"),
    (999, "rezepte", "__IGNORE__"),
]

LEGACY_PATTERNS_TO_DISABLE = [
    "fruehstueck",
    "muesli",
    "plaetzchen",
    "gebaeck",
    "broet",
    "bruehe",
    "getraenk",
    "haepp",
    "sosse",
    "knoedel",
]


def _find_mapping_row_id(connection, pattern: str) -> int | None:
    row = connection.execute(
        sa.text(
            """
            SELECT id
            FROM category_mappings
            WHERE lower(pattern) = lower(:pattern)
            ORDER BY id ASC
            LIMIT 1
            """
        ),
        {"pattern": pattern},
    ).fetchone()
    return int(row[0]) if row else None


def upgrade() -> None:
    connection = op.get_bind()
    now = datetime.now(timezone.utc)

    for priority, pattern, canonical_category in TARGET_MAPPINGS:
        row_id = _find_mapping_row_id(connection, pattern)
        if row_id is None:
            connection.execute(
                sa.text(
                    """
                    INSERT INTO category_mappings (pattern, canonical_category, priority, enabled, created_at)
                    VALUES (:pattern, :canonical_category, :priority, :enabled, :created_at)
                    """
                ),
                {
                    "pattern": pattern,
                    "canonical_category": canonical_category,
                    "priority": priority,
                    "enabled": True,
                    "created_at": now,
                },
            )
            continue
        connection.execute(
            sa.text(
                """
                UPDATE category_mappings
                SET canonical_category = :canonical_category,
                    priority = :priority,
                    enabled = :enabled
                WHERE id = :id
                """
            ),
            {
                "id": row_id,
                "canonical_category": canonical_category,
                "priority": priority,
                "enabled": True,
            },
        )

    for pattern in LEGACY_PATTERNS_TO_DISABLE:
        connection.execute(
            sa.text(
                """
                UPDATE category_mappings
                SET enabled = :enabled
                WHERE lower(pattern) = lower(:pattern)
                """
            ),
            {"pattern": pattern, "enabled": False},
        )


def downgrade() -> None:
    # Keep user edits and inserted mappings untouched on downgrade to avoid data loss.
    pass
