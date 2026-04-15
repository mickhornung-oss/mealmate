import sys
from pathlib import Path

from sqlalchemy import select

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.database import SessionLocal
from app.models import User
from app.security import hash_password

ADMIN_EMAIL = "admin@mealmate.local"
ADMIN_PASSWORD = "AdminPass123!"


def seed_admin() -> None:
    db = SessionLocal()
    try:
        admin = db.scalar(select(User).where(User.email == ADMIN_EMAIL))
        if admin:
            admin.role = "admin"
            admin.hashed_password = hash_password(ADMIN_PASSWORD)
            db.commit()
            print("Updated existing admin user.")
            return
        db.add(
            User(
                email=ADMIN_EMAIL,
                hashed_password=hash_password(ADMIN_PASSWORD),
                role="admin",
            )
        )
        db.commit()
        print("Created admin user.")
    finally:
        db.close()


if __name__ == "__main__":
    seed_admin()
