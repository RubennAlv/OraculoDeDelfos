import httpx

from .config import settings
from .db import get_conn, init_db

URL = "https://api.clashroyale.com/v1/cards"


def main() -> None:
    headers = {"Authorization": f"Bearer {settings.cr_api_key}"}
    r = httpx.get(URL, headers=headers, timeout=15)
    r.raise_for_status()
    items = r.json()["items"]

    init_db()
    with get_conn() as conn:
        for c in items:
            icons = c.get("iconUrls", {})
            conn.execute(
                """
                INSERT INTO cards (id, name, elixir, rarity, max_level,
                                   icon_url, evo_icon_url, hero_icon_url,
                                   has_evo, has_hero)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    name=excluded.name, elixir=excluded.elixir,
                    rarity=excluded.rarity, max_level=excluded.max_level,
                    icon_url=excluded.icon_url,
                    evo_icon_url=excluded.evo_icon_url,
                    hero_icon_url=excluded.hero_icon_url,
                    has_evo=excluded.has_evo, has_hero=excluded.has_hero
                """,
                (
                    c["id"], c["name"], c.get("elixirCost"), c.get("rarity"),
                    c.get("maxLevel"), icons.get("medium"),
                    icons.get("evolutionMedium"), icons.get("heroMedium"),
                    int("evolutionMedium" in icons),
                    int("heroMedium" in icons),
                ),
            )
    print(f"{len(items)} cartas sincronizadas")


if __name__ == "__main__":
    main()