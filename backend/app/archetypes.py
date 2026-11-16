import sqlite3
from collections import Counter, defaultdict

from .db import DB_PATH
from .stats import wilson_interval

# El orden es la prioridad. Los nombres deben coincidir con los de la tabla cards.
WIN_CONDITIONS = [
    "Golem", "Lava Hound", "Balloon", "Giant", "Royal Giant", "Graveyard",
    "X-Bow", "Mortar", "Hog Rider", "Ram Rider", "Battle Ram", "Miner",
    "Goblin Barrel", "Skeleton Barrel", "Wall Breakers", "P.E.K.K.A",
    "Mega Knight", "Royal Hogs", "Elixir Golem", "Three Musketeers",
    "Goblin Drill", "Sparky",
]


def classify(names: set[str]) -> str:
    found = [w for w in WIN_CONDITIONS if w in names]
    return " + ".join(found[:2]) if found else "Sin clasificar"


def main() -> None:
    c = sqlite3.connect(DB_PATH)
    id_name = {r[0]: r[1] for r in c.execute("SELECT id, name FROM cards")}
    cache: dict[str, str] = {}

    def arch(deck: str) -> str:
        if deck not in cache:
            names = {id_name.get(int(i.rstrip("eh")), "?") for i in deck.split(",")}
            cache[deck] = classify(names)
        return cache[deck]

    games = c.execute("SELECT deck_a, deck_b, a_won FROM games").fetchall()

    freq = Counter()
    for a, b, _ in games:
        freq[arch(a)] += 1
        freq[arch(b)] += 1
    print("Arquetipos (apariciones, ambos lados):")
    for name, n in freq.most_common(20):
        print(f"  {n:4d}  {name}")

    wins = defaultdict(int)
    losses = defaultdict(int)
    for da, db, a_won in games:
        x, y = arch(da), arch(db)
        if x == y or "Sin clasificar" in (x, y):
            continue
        wins[(x, y)] += a_won
        losses[(x, y)] += 1 - a_won
        wins[(y, x)] += 1 - a_won  # la misma partida vista desde el otro lado
        losses[(y, x)] += a_won

    print("\nCruces con mas partidas (A vs B: victorias-derrotas, intervalo Wilson):")
    pares = sorted(wins.keys() | losses.keys(),
                   key=lambda k: -(wins[k] + losses[k]))
    for x, y in [p for p in pares if p[0] < p[1]][:20]:
        w, l = wins[(x, y)], losses[(x, y)]
        lo, hi = wilson_interval(w, l)
        print(f"  {x} vs {y}: {w}-{l}  [{lo:.0%} - {hi:.0%}]")


if __name__ == "__main__":
    main()