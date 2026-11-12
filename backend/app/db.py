import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "oraculo.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS cards (
    id            INTEGER PRIMARY KEY,
    name          TEXT NOT NULL,
    elixir        INTEGER,
    rarity        TEXT,
    max_level     INTEGER,
    icon_url      TEXT,
    evo_icon_url  TEXT,
    hero_icon_url TEXT,
    has_evo       INTEGER NOT NULL DEFAULT 0,
    has_hero      INTEGER NOT NULL DEFAULT 0
);
"""


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_conn() as conn:
        conn.executescript(SCHEMA)