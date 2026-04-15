"""seed default canonical category mappings

Revision ID: 20260304_0011
Revises: 20260304_0010
Create Date: 2026-03-04 13:05:00
"""

from datetime import datetime, timezone
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20260304_0011"
down_revision: Union[str, None] = "20260304_0010"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

DEFAULT_MAPPINGS: list[tuple[str, str, int]] = [
    ("frühstück", "Frühstück", 10),
    ("fruehstueck", "Frühstück", 10),
    ("brunch", "Frühstück", 10),
    ("müsli", "Frühstück", 10),
    ("muesli", "Frühstück", 10),
    ("porridge", "Frühstück", 10),
    ("mittag", "Mittagessen", 20),
    ("lunch", "Mittagessen", 20),
    ("abend", "Abendessen", 20),
    ("dinner", "Abendessen", 20),
    ("kuchen", "Backen", 25),
    ("torte", "Backen", 25),
    ("plätzchen", "Backen", 25),
    ("plaetzchen", "Backen", 25),
    ("gebäck", "Backen", 25),
    ("gebaeck", "Backen", 25),
    ("brot", "Backen", 25),
    ("bröt", "Backen", 25),
    ("broet", "Backen", 25),
    ("dessert", "Dessert", 30),
    ("pudding", "Dessert", 30),
    ("creme", "Dessert", 30),
    ("suppe", "Suppe & Eintopf", 30),
    ("eintopf", "Suppe & Eintopf", 30),
    ("brühe", "Suppe & Eintopf", 30),
    ("bruehe", "Suppe & Eintopf", 30),
    ("gulasch", "Suppe & Eintopf", 30),
    ("chili", "Suppe & Eintopf", 30),
    ("salat", "Salat", 30),
    ("getränk", "Getränke", 30),
    ("getraenk", "Getränke", 30),
    ("cocktail", "Getränke", 30),
    ("smoothie", "Getränke", 30),
    ("saft", "Getränke", 30),
    ("tee", "Getränke", 30),
    ("kaffee", "Getränke", 30),
    ("snack", "Snack", 30),
    ("fingerfood", "Snack", 30),
    ("häpp", "Snack", 30),
    ("haepp", "Snack", 30),
    ("wrap", "Snack", 30),
    ("beilage", "Beilage", 35),
    ("sauce", "Beilage", 35),
    ("soße", "Beilage", 35),
    ("sosse", "Beilage", 35),
    ("dip", "Beilage", 35),
    ("pesto", "Beilage", 35),
    ("reis", "Beilage", 35),
    ("kartoffel", "Beilage", 35),
    ("knödel", "Beilage", 35),
    ("knoedel", "Beilage", 35),
]


def upgrade() -> None:
    connection = op.get_bind()
    current_count = connection.execute(sa.text("SELECT COUNT(*) FROM category_mappings")).scalar_one()
    if int(current_count) > 0:
        return

    now = datetime.now(timezone.utc)
    category_mappings = sa.table(
        "category_mappings",
        sa.column("pattern", sa.String(length=120)),
        sa.column("canonical_category", sa.String(length=60)),
        sa.column("priority", sa.Integer()),
        sa.column("enabled", sa.Boolean()),
        sa.column("created_at", sa.DateTime(timezone=True)),
    )
    rows = [
        {
            "pattern": pattern,
            "canonical_category": canonical_category,
            "priority": priority,
            "enabled": True,
            "created_at": now,
        }
        for pattern, canonical_category, priority in DEFAULT_MAPPINGS
    ]
    op.bulk_insert(category_mappings, rows)


def downgrade() -> None:
    connection = op.get_bind()
    patterns = [pattern for pattern, _, _ in DEFAULT_MAPPINGS]
    if not patterns:
        return
    placeholders = ", ".join(f":p{index}" for index, _ in enumerate(patterns))
    query = sa.text(f"DELETE FROM category_mappings WHERE pattern IN ({placeholders})")
    params = {f"p{index}": pattern for index, pattern in enumerate(patterns)}
    connection.execute(query, params)
