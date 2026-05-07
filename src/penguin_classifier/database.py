"""SQLite database access helpers."""

import logging
import os
import sqlite3
from pathlib import Path

from alembic import command
from alembic.config import Config


def _get_data_dir() -> Path:
    env_dir = os.getenv("PENGUIN_APP_DATA_DIR")
    if env_dir:
        return Path(env_dir)
    return Path(__file__).resolve().parent.parent / "data"


DEFAULT_DATABASE_PATH = _get_data_dir() / "penguins.db"


def get_connection(database_path: Path | None = None) -> sqlite3.Connection:
    """Create a SQLite connection with row access by column name."""

    db_path = database_path or DEFAULT_DATABASE_PATH
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database(database_path: Path | None = None) -> None:
    """Run Alembic migrations to create required tables if they do not exist yet."""
    db_path = database_path or DEFAULT_DATABASE_PATH
    db_path.parent.mkdir(parents=True, exist_ok=True)

    project_root = Path(__file__).resolve().parent.parent
    alembic_ini_path = project_root / "alembic.ini"
    alembic_script_location = project_root / "alembic"

    alembic_cfg = Config(str(alembic_ini_path))
    alembic_cfg.set_main_option("script_location", str(alembic_script_location))
    alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")

    try:
        command.upgrade(alembic_cfg, "head")
    except Exception as e:  # pylint: disable=broad-exception-caught
        logging.error("Failed to run database migrations: %s", e)
        raise
