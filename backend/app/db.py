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
CREATE TABLE IF NOT EXISTS archetypes (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS decks (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    archetype_id INTEGER REFERENCES archetypes(id)
);

CREATE TABLE IF NOT EXISTS deck_cards (
    deck_id INTEGER NOT NULL REFERENCES decks(id),
    card_id INTEGER NOT NULL REFERENCES cards(id),
    variant TEXT NOT NULL DEFAULT 'normal'
            CHECK (variant IN ('normal', 'evo', 'hero')),
    PRIMARY KEY (deck_id, card_id)
);

CREATE TABLE IF NOT EXISTS matchups (
    archetype_a INTEGER NOT NULL REFERENCES archetypes(id),
    archetype_b INTEGER NOT NULL REFERENCES archetypes(id),
    wins        INTEGER NOT NULL DEFAULT 0,
    losses      INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (archetype_a, archetype_b),
    CHECK (archetype_a <> archetype_b)
);
"""


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    with get_conn() as conn:
        conn.executescript(SCHEMA)