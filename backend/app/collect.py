import sys
import time
from datetime import datetime, timezone
from urllib.parse import quote

import httpx

from .config import settings
from .db import get_conn, init_db
from .parse_battles import parse_battle, parse_duel

BASE = "https://api.clashroyale.com/v1"


def games_from(b: dict):
    """Devuelve filas (game_key, time, mode, deck_a, deck_b, a_won) y el tag rival."""
    if b.get("type") == "pathOfLegend":
        g = parse_battle(b)
        if g:
            yield (g["battle_key"], g["battle_time"], "pol_1v1",
                   g["player_deck"], g["opponent_deck"], g["player_won"]), g["opponent_tag"]
    elif b.get("gameMode", {}).get("name") == "Competitive_Multideck":
        d = parse_duel(b)
        if d:
            for r in d["rounds"]:
                yield (f'{d["battle_key"]}|r{r["round_no"]}', d["battle_time"],
                       "pol_multideck", r["player_deck"], r["opponent_deck"],
                       r["player_won"]), d["opponent_tag"]


def fetch_log(client: httpx.Client, tag: str):
    for _ in range(2):
        r = client.get(f"/players/{quote(tag, safe='')}/battlelog")
        if r.status_code == 429:  # demasiadas peticiones
            time.sleep(5)
            continue
        if r.status_code == 404:
            return []
        r.raise_for_status()
        return r.json()
    return []


def main() -> None:
    season, n_seeds, max_players = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    init_db()
    headers = {"Authorization": f"Bearer {settings.cr_api_key}"}

    with httpx.Client(base_url=BASE, headers=headers, timeout=15) as client, get_conn() as conn:
        resp = client.get(
            f"/locations/global/pathoflegend/{season}/rankings/players",
            params={"limit": n_seeds},
        )
        if resp.status_code != 200:
            sys.exit(f"Error {resp.status_code} al pedir el ranking: {resp.text}")
        for p in resp.json()["items"]:
            conn.execute("INSERT OR IGNORE INTO pending_players VALUES (?)", (p["tag"],))
        conn.commit()

        fetched = new_games = 0
        while fetched < max_players:
            row = conn.execute(
                "SELECT tag FROM pending_players "
                "WHERE tag NOT IN (SELECT tag FROM players) "
                "ORDER BY rowid LIMIT 1"
            ).fetchone()
            if row is None:
                print("No quedan jugadores pendientes.")
                break
            tag = row["tag"]

            for b in fetch_log(client, tag):
                for game_row, opp_tag in games_from(b):
                    cur = conn.execute(
                        "INSERT OR IGNORE INTO games VALUES (?,?,?,?,?,?)", game_row)
                    new_games += cur.rowcount
                    conn.execute(
                        "INSERT OR IGNORE INTO pending_players VALUES (?)", (opp_tag,))

            conn.execute(
                "INSERT OR REPLACE INTO players VALUES (?, ?)",
                (tag, datetime.now(timezone.utc).isoformat()),
            )
            conn.commit()
            fetched += 1
            print(f"[{fetched}/{max_players}] {tag}: {new_games} partidas nuevas en esta corrida")
            time.sleep(0.15)

if __name__ == "__main__":
    main()