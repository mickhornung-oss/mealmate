Ge?nderte Dateien:
- app/dev_seed_accounts.py
- tools/seed_accounts.py
- tests/test_seed_accounts.py

### app/dev_seed_accounts.py
```python
from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import User
from app.security import hash_password, normalize_username


@dataclass(frozen=True)
class AccountSeedSpec:
    email: str
    username: str
    role: str
    password: str


@dataclass(frozen=True)
class AccountSeedRow:
    email: str
    username: str
    role: str
    password: str
    status: str


@dataclass
class AccountSeedReport:
    created: int = 0
    updated: int = 0
    unchanged: int = 0
    rows: list[AccountSeedRow] | None = None

    def __post_init__(self) -> None:
        if self.rows is None:
            self.rows = []


DEFAULT_ACCOUNT_SPECS: tuple[AccountSeedSpec, ...] = (
    AccountSeedSpec("admin1@mealmate.local", "admin1", "admin", "AdminPass123!"),
    AccountSeedSpec("admin2@mealmate.local", "admin2", "admin", "AdminPass123!"),
    AccountSeedSpec("admin3@mealmate.local", "admin3", "admin", "AdminPass123!"),
    AccountSeedSpec("user1@mealmate.local", "user1", "user", "UserPass123!"),
    AccountSeedSpec("user2@mealmate.local", "user2", "user", "UserPass123!"),
    AccountSeedSpec("user3@mealmate.local", "user3", "user", "UserPass123!"),
)


def dev_seed_allowed(app_env: str, allow_dev_seed: bool) -> bool:
    return app_env == "dev" or bool(allow_dev_seed)


def ensure_dev_seed_allowed(app_env: str, allow_dev_seed: bool) -> None:
    if dev_seed_allowed(app_env, allow_dev_seed):
        return
    raise RuntimeError(
        "Testaccount-Seed ist nur in APP_ENV=dev oder mit ALLOW_DEV_SEED=1 erlaubt."
    )


def _collect_taken_username_norms(db: Session) -> set[str]:
    rows = db.scalars(select(User.username_normalized).where(User.username_normalized.is_not(None))).all()
    return {value for value in rows if value}


def _find_available_username(preferred_normalized: str, taken: set[str]) -> tuple[str, bool]:
    if preferred_normalized not in taken:
        return preferred_normalized, False
    base = preferred_normalized[:24]
    index = 2
    while True:
        candidate = f"{base}{index}"
        candidate = candidate[:30]
        if candidate not in taken:
            return candidate, True
        index += 1


def seed_test_accounts(
    db: Session,
    specs: tuple[AccountSeedSpec, ...] = DEFAULT_ACCOUNT_SPECS,
) -> AccountSeedReport:
    report = AccountSeedReport()
    taken_usernames = _collect_taken_username_norms(db)
    users_by_email = {
        user.email.lower(): user
        for user in db.scalars(select(User).where(User.email.in_([item.email for item in specs]))).all()
    }

    for spec in specs:
        email_normalized = spec.email.strip().lower()
        desired_username_norm = normalize_username(spec.username)
        existing_user = users_by_email.get(email_normalized)
        if existing_user:
            if existing_user.username_normalized:
                taken_usernames.add(existing_user.username_normalized)
            report.unchanged += 1
            report.rows.append(
                AccountSeedRow(
                    email=existing_user.email,
                    username=existing_user.username or spec.username,
                    role=existing_user.role,
                    password=spec.password,
                    status="skipped-existing-email",
                )
            )
            continue

        username_norm, adjusted = _find_available_username(desired_username_norm, taken_usernames)
        username_text = username_norm
        user = User(
            email=email_normalized,
            username=username_text,
            username_normalized=username_norm,
            hashed_password=hash_password(spec.password),
            role=spec.role,
        )
        db.add(user)
        users_by_email[email_normalized] = user
        taken_usernames.add(username_norm)
        report.created += 1
        status = "created-adjusted-username" if adjusted else "created"
        report.rows.append(
            AccountSeedRow(
                email=email_normalized,
                username=username_text,
                role=spec.role,
                password=spec.password,
                status=status,
            )
        )
    return report
```
ZEILEN-ERKL?RUNG
1. Diese Zeile importiert ben?tigte Module oder Funktionen.
2. Diese Zeile ist bewusst leer f?r bessere Lesbarkeit.
3. Diese Zeile importiert ben?tigte Module oder Funktionen.
4. Diese Zeile ist bewusst leer f?r bessere Lesbarkeit.
5. Diese Zeile importiert ben?tigte Module oder Funktionen.
6. Diese Zeile importiert ben?tigte Module oder Funktionen.
7. Diese Zeile ist bewusst leer f?r bessere Lesbarkeit.
8. Diese Zeile importiert ben?tigte Module oder Funktionen.
9. Diese Zeile importiert ben?tigte Module oder Funktionen.
10. Diese Zeile ist bewusst leer f?r bessere Lesbarkeit.
11. Diese Zeile ist bewusst leer f?r bessere Lesbarkeit.
12. Diese Zeile markiert die folgende Klasse als Dataclass.
13. Diese Zeile definiert eine Klasse f?r Seed-Daten oder Reports.
14. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
15. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
16. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
17. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
18. Diese Zeile ist bewusst leer f?r bessere Lesbarkeit.
19. Diese Zeile ist bewusst leer f?r bessere Lesbarkeit.
20. Diese Zeile markiert die folgende Klasse als Dataclass.
21. Diese Zeile definiert eine Klasse f?r Seed-Daten oder Reports.
22. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
23. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
24. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
25. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
26. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
27. Diese Zeile ist bewusst leer f?r bessere Lesbarkeit.
28. Diese Zeile ist bewusst leer f?r bessere Lesbarkeit.
29. Diese Zeile markiert die folgende Klasse als Dataclass.
30. Diese Zeile definiert eine Klasse f?r Seed-Daten oder Reports.
31. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
32. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
33. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
34. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
35. Diese Zeile ist bewusst leer f?r bessere Lesbarkeit.
36. Diese Zeile definiert eine Funktion des Seed-Workflows.
37. Diese Zeile pr?ft eine Bedingung im Ablauf.
38. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
39. Diese Zeile ist bewusst leer f?r bessere Lesbarkeit.
40. Diese Zeile ist bewusst leer f?r bessere Lesbarkeit.
41. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
42. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
43. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
44. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
45. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
46. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
47. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
48. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
49. Diese Zeile ist bewusst leer f?r bessere Lesbarkeit.
50. Diese Zeile ist bewusst leer f?r bessere Lesbarkeit.
51. Diese Zeile definiert eine Funktion des Seed-Workflows.
52. Diese Zeile gibt den berechneten Wert an den Aufrufer zur?ck.
53. Diese Zeile ist bewusst leer f?r bessere Lesbarkeit.
54. Diese Zeile ist bewusst leer f?r bessere Lesbarkeit.
55. Diese Zeile definiert eine Funktion des Seed-Workflows.
56. Diese Zeile pr?ft eine Bedingung im Ablauf.
57. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
58. Diese Zeile l?st bewusst eine Exception aus.
59. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
60. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
61. Diese Zeile ist bewusst leer f?r bessere Lesbarkeit.
62. Diese Zeile ist bewusst leer f?r bessere Lesbarkeit.
63. Diese Zeile definiert eine Funktion des Seed-Workflows.
64. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
65. Diese Zeile gibt den berechneten Wert an den Aufrufer zur?ck.
66. Diese Zeile ist bewusst leer f?r bessere Lesbarkeit.
67. Diese Zeile ist bewusst leer f?r bessere Lesbarkeit.
68. Diese Zeile definiert eine Funktion des Seed-Workflows.
69. Diese Zeile pr?ft eine Bedingung im Ablauf.
70. Diese Zeile gibt den berechneten Wert an den Aufrufer zur?ck.
71. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
72. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
73. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
74. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
75. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
76. Diese Zeile pr?ft eine Bedingung im Ablauf.
77. Diese Zeile gibt den berechneten Wert an den Aufrufer zur?ck.
78. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
79. Diese Zeile ist bewusst leer f?r bessere Lesbarkeit.
80. Diese Zeile ist bewusst leer f?r bessere Lesbarkeit.
81. Diese Zeile definiert eine Funktion des Seed-Workflows.
82. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
83. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
84. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
85. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
86. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
87. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
88. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
89. Diese Zeile startet eine Schleife ?ber mehrere Elemente.
90. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
91. Diese Zeile ist bewusst leer f?r bessere Lesbarkeit.
92. Diese Zeile startet eine Schleife ?ber mehrere Elemente.
93. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
94. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
95. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
96. Diese Zeile pr?ft eine Bedingung im Ablauf.
97. Diese Zeile pr?ft eine Bedingung im Ablauf.
98. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
99. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
100. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
101. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
102. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
103. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
104. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
105. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
106. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
107. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
108. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
109. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
110. Diese Zeile ist bewusst leer f?r bessere Lesbarkeit.
111. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
112. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
113. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
114. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
115. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
116. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
117. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
118. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
119. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
120. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
121. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
122. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
123. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
124. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
125. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
126. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
127. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
128. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
129. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
130. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
131. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
132. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
133. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
134. Diese Zeile gibt den berechneten Wert an den Aufrufer zur?ck.

### tools/seed_accounts.py
```python
from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Iterable

from app.config import get_settings
from app.database import SessionLocal
from app.dev_seed_accounts import ensure_dev_seed_allowed, seed_test_accounts


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Erzeugt idempotent 3 Admins und 3 User fuer lokale Tests."
    )
    return parser


def _render_table(rows: Iterable[list[str]]) -> str:
    rows_list = list(rows)
    widths = [max(len(row[index]) for row in rows_list) for index in range(len(rows_list[0]))]
    lines: list[str] = []
    for row_index, row in enumerate(rows_list):
        line = " | ".join(cell.ljust(widths[idx]) for idx, cell in enumerate(row))
        lines.append(line)
        if row_index == 0:
            lines.append("-+-".join("-" * width for width in widths))
    return "\n".join(lines)


def _read_env_file_value(key: str, env_file: Path) -> str | None:
    if not env_file.exists():
        return None
    for raw_line in env_file.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        left, right = line.split("=", 1)
        if left.strip() == key:
            return right.strip()
    return None


def _parse_bool_env(value: str | None) -> bool:
    if value is None:
        return False
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _resolve_allow_dev_seed() -> bool:
    from_process = os.getenv("ALLOW_DEV_SEED")
    if from_process is not None:
        return _parse_bool_env(from_process)
    from_file = _read_env_file_value("ALLOW_DEV_SEED", Path(".env"))
    return _parse_bool_env(from_file)


def main() -> int:
    _ = build_parser().parse_args()
    settings = get_settings()
    try:
        ensure_dev_seed_allowed(settings.app_env, _resolve_allow_dev_seed())
    except RuntimeError as exc:
        print(f"ABBRUCH: {exc}")
        return 1

    with SessionLocal() as db:
        report = seed_test_accounts(db)
        db.commit()

    print("Seed abgeschlossen.")
    print(f"Erstellt: {report.created}")
    print(f"Aktualisiert: {report.updated}")
    print(f"Unveraendert: {report.unchanged}")
    print("")
    header = ["Email", "Username", "Role", "Passwort", "Status"]
    table_rows = [header]
    for row in report.rows or []:
        table_rows.append([row.email, row.username, row.role, row.password, row.status])
    print(_render_table(table_rows))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```
ZEILEN-ERKL?RUNG
1. Diese Zeile importiert ben?tigte Module oder Funktionen.
2. Diese Zeile ist bewusst leer f?r bessere Lesbarkeit.
3. Diese Zeile importiert ben?tigte Module oder Funktionen.
4. Diese Zeile importiert ben?tigte Module oder Funktionen.
5. Diese Zeile importiert ben?tigte Module oder Funktionen.
6. Diese Zeile importiert ben?tigte Module oder Funktionen.
7. Diese Zeile ist bewusst leer f?r bessere Lesbarkeit.
8. Diese Zeile importiert ben?tigte Module oder Funktionen.
9. Diese Zeile importiert ben?tigte Module oder Funktionen.
10. Diese Zeile importiert ben?tigte Module oder Funktionen.
11. Diese Zeile ist bewusst leer f?r bessere Lesbarkeit.
12. Diese Zeile ist bewusst leer f?r bessere Lesbarkeit.
13. Diese Zeile definiert eine Funktion des Seed-Workflows.
14. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
15. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
16. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
17. Diese Zeile gibt den berechneten Wert an den Aufrufer zur?ck.
18. Diese Zeile ist bewusst leer f?r bessere Lesbarkeit.
19. Diese Zeile ist bewusst leer f?r bessere Lesbarkeit.
20. Diese Zeile definiert eine Funktion des Seed-Workflows.
21. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
22. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
23. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
24. Diese Zeile startet eine Schleife ?ber mehrere Elemente.
25. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
26. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
27. Diese Zeile pr?ft eine Bedingung im Ablauf.
28. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
29. Diese Zeile gibt den berechneten Wert an den Aufrufer zur?ck.
30. Diese Zeile ist bewusst leer f?r bessere Lesbarkeit.
31. Diese Zeile ist bewusst leer f?r bessere Lesbarkeit.
32. Diese Zeile definiert eine Funktion des Seed-Workflows.
33. Diese Zeile pr?ft eine Bedingung im Ablauf.
34. Diese Zeile gibt den berechneten Wert an den Aufrufer zur?ck.
35. Diese Zeile startet eine Schleife ?ber mehrere Elemente.
36. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
37. Diese Zeile pr?ft eine Bedingung im Ablauf.
38. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
39. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
40. Diese Zeile pr?ft eine Bedingung im Ablauf.
41. Diese Zeile gibt den berechneten Wert an den Aufrufer zur?ck.
42. Diese Zeile gibt den berechneten Wert an den Aufrufer zur?ck.
43. Diese Zeile ist bewusst leer f?r bessere Lesbarkeit.
44. Diese Zeile ist bewusst leer f?r bessere Lesbarkeit.
45. Diese Zeile definiert eine Funktion des Seed-Workflows.
46. Diese Zeile pr?ft eine Bedingung im Ablauf.
47. Diese Zeile gibt den berechneten Wert an den Aufrufer zur?ck.
48. Diese Zeile gibt den berechneten Wert an den Aufrufer zur?ck.
49. Diese Zeile ist bewusst leer f?r bessere Lesbarkeit.
50. Diese Zeile ist bewusst leer f?r bessere Lesbarkeit.
51. Diese Zeile definiert eine Funktion des Seed-Workflows.
52. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
53. Diese Zeile pr?ft eine Bedingung im Ablauf.
54. Diese Zeile gibt den berechneten Wert an den Aufrufer zur?ck.
55. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
56. Diese Zeile gibt den berechneten Wert an den Aufrufer zur?ck.
57. Diese Zeile ist bewusst leer f?r bessere Lesbarkeit.
58. Diese Zeile ist bewusst leer f?r bessere Lesbarkeit.
59. Diese Zeile definiert eine Funktion des Seed-Workflows.
60. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
61. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
62. Diese Zeile startet einen Try-Block zur Fehlerbehandlung.
63. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
64. Diese Zeile behandelt einen erwarteten Fehlerfall.
65. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
66. Diese Zeile gibt den berechneten Wert an den Aufrufer zur?ck.
67. Diese Zeile ist bewusst leer f?r bessere Lesbarkeit.
68. Diese Zeile nutzt einen Kontextmanager f?r sauberes Ressourcenhandling.
69. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
70. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
71. Diese Zeile ist bewusst leer f?r bessere Lesbarkeit.
72. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
73. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
74. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
75. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
76. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
77. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
78. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
79. Diese Zeile startet eine Schleife ?ber mehrere Elemente.
80. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
81. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
82. Diese Zeile gibt den berechneten Wert an den Aufrufer zur?ck.
83. Diese Zeile ist bewusst leer f?r bessere Lesbarkeit.
84. Diese Zeile ist bewusst leer f?r bessere Lesbarkeit.
85. Diese Zeile pr?ft eine Bedingung im Ablauf.
86. Diese Zeile l?st bewusst eine Exception aus.

### tests/test_seed_accounts.py
```python
from sqlalchemy import func, select

from app.dev_seed_accounts import seed_test_accounts
from app.models import User


def test_seed_accounts_idempotent(db_session_factory):
    db = db_session_factory()
    try:
        first_report = seed_test_accounts(db)
        db.commit()

        total_after_first = db.scalar(select(func.count()).select_from(User))
        admin_after_first = db.scalar(select(func.count()).select_from(User).where(User.role == "admin"))
        user_after_first = db.scalar(select(func.count()).select_from(User).where(User.role == "user"))

        assert first_report.created == 6
        assert total_after_first == 6
        assert admin_after_first == 3
        assert user_after_first == 3

        second_report = seed_test_accounts(db)
        db.commit()

        total_after_second = db.scalar(select(func.count()).select_from(User))
        admin_after_second = db.scalar(select(func.count()).select_from(User).where(User.role == "admin"))
        user_after_second = db.scalar(select(func.count()).select_from(User).where(User.role == "user"))

        assert second_report.created == 0
        assert second_report.updated + second_report.unchanged == 6
        assert total_after_second == 6
        assert admin_after_second == 3
        assert user_after_second == 3
    finally:
        db.close()
```
ZEILEN-ERKL?RUNG
1. Diese Zeile importiert ben?tigte Module oder Funktionen.
2. Diese Zeile ist bewusst leer f?r bessere Lesbarkeit.
3. Diese Zeile importiert ben?tigte Module oder Funktionen.
4. Diese Zeile importiert ben?tigte Module oder Funktionen.
5. Diese Zeile ist bewusst leer f?r bessere Lesbarkeit.
6. Diese Zeile ist bewusst leer f?r bessere Lesbarkeit.
7. Diese Zeile definiert eine Funktion des Seed-Workflows.
8. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
9. Diese Zeile startet einen Try-Block zur Fehlerbehandlung.
10. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
11. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
12. Diese Zeile ist bewusst leer f?r bessere Lesbarkeit.
13. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
14. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
15. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
16. Diese Zeile ist bewusst leer f?r bessere Lesbarkeit.
17. Diese Zeile pr?ft im Test eine erwartete Eigenschaft.
18. Diese Zeile pr?ft im Test eine erwartete Eigenschaft.
19. Diese Zeile pr?ft im Test eine erwartete Eigenschaft.
20. Diese Zeile pr?ft im Test eine erwartete Eigenschaft.
21. Diese Zeile ist bewusst leer f?r bessere Lesbarkeit.
22. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
23. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
24. Diese Zeile ist bewusst leer f?r bessere Lesbarkeit.
25. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
26. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
27. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
28. Diese Zeile ist bewusst leer f?r bessere Lesbarkeit.
29. Diese Zeile pr?ft im Test eine erwartete Eigenschaft.
30. Diese Zeile pr?ft im Test eine erwartete Eigenschaft.
31. Diese Zeile pr?ft im Test eine erwartete Eigenschaft.
32. Diese Zeile pr?ft im Test eine erwartete Eigenschaft.
33. Diese Zeile pr?ft im Test eine erwartete Eigenschaft.
34. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
35. Diese Zeile enth?lt konkrete Programmlogik f?r den Seed-Prozess.
