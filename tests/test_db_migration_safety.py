from __future__ import annotations

import os
import sqlite3
from datetime import datetime
from contextlib import contextmanager
from pathlib import Path

from alembic import command
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine

from app.config import get_settings

# Python 3.12 deprecates sqlite's implicit datetime adapter.
# Register explicit adapters for migration tests to keep behavior explicit and warning-free.
sqlite3.register_adapter(datetime, lambda value: value.isoformat(sep=" "))


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ALEMBIC_INI_PATH = PROJECT_ROOT / "alembic.ini"
ALEMBIC_SCRIPT_PATH = PROJECT_ROOT / "alembic"


def _sqlite_url_for(path: Path) -> str:
    return f"sqlite:///{path.resolve().as_posix()}"


@contextmanager
def _alembic_env(database_url: str):
    previous_database_url = os.environ.get("DATABASE_URL")
    os.environ["DATABASE_URL"] = database_url
    get_settings.cache_clear()
    try:
        yield
    finally:
        if previous_database_url is None:
            os.environ.pop("DATABASE_URL", None)
        else:
            os.environ["DATABASE_URL"] = previous_database_url
        get_settings.cache_clear()


def _alembic_config(database_url: str) -> Config:
    config = Config(str(ALEMBIC_INI_PATH))
    config.set_main_option("script_location", str(ALEMBIC_SCRIPT_PATH))
    config.set_main_option("sqlalchemy.url", database_url)
    return config


def _current_revision(database_url: str) -> str | None:
    engine = create_engine(database_url)
    try:
        with engine.connect() as connection:
            context = MigrationContext.configure(connection)
            return context.get_current_revision()
    finally:
        engine.dispose()


def test_alembic_has_single_head():
    config = _alembic_config("sqlite:///./unused.db")
    script = ScriptDirectory.from_config(config)
    heads = script.get_heads()
    assert len(heads) == 1


def test_upgrade_head_on_empty_db_matches_head_revision(tmp_path: Path):
    database_url = _sqlite_url_for(tmp_path / "migration_upgrade_head.db")
    config = _alembic_config(database_url)
    script = ScriptDirectory.from_config(config)
    head_revision = script.get_current_head()

    with _alembic_env(database_url):
        command.upgrade(config, "head")
        current_revision = _current_revision(database_url)

    assert current_revision == head_revision


def test_downgrade_one_step_and_upgrade_back_to_head(tmp_path: Path):
    database_url = _sqlite_url_for(tmp_path / "migration_downgrade_upgrade.db")
    config = _alembic_config(database_url)
    script = ScriptDirectory.from_config(config)
    head_revision = script.get_current_head()

    with _alembic_env(database_url):
        command.upgrade(config, "head")
        revision_after_upgrade = _current_revision(database_url)
        assert revision_after_upgrade == head_revision

        command.downgrade(config, "-1")
        revision_after_downgrade = _current_revision(database_url)
        assert revision_after_downgrade != head_revision

        command.upgrade(config, "head")
        revision_after_reupgrade = _current_revision(database_url)

    assert revision_after_reupgrade == head_revision
