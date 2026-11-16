import sqlite3
from collections import Counter

from .db import DB_PATH

c = sqlite3.connect(DB_PATH)

print("Partidas por modo (modo, total, victorias de A):")
for row in c.execute("SELECT mode, COUNT(*), SUM(a_won) FROM games GROUP BY mode"):
    print("  ", row)

raras = c.execute(
    "SELECT COUNT(*) FROM games WHERE deck_a LIKE '%x%' OR deck_b LIKE '%x%'"
).fetchone()[0]
print("Partidas con variantes raras:", raras)

mazos = c.execute(
    "SELECT COUNT(*) FROM (SELECT deck_a d FROM games UNION SELECT deck_b FROM games)"
).fetchone()[0]
total = c.execute("SELECT COUNT(*) FROM games").fetchone()[0]
print(f"Mazos distintos: {mazos} (en {total} partidas)")

nombres = {r[0]: r[1] for r in c.execute("SELECT id, name FROM cards")}
if not nombres:
    print("\nLa tabla cards esta vacia: corre  python -m app.sync_cards")

cont = Counter()
for (d,) in c.execute("SELECT deck_a FROM games"):
    for item in d.split(","):
        cont[int(item.rstrip("eh"))] += 1
print("\nTop 25 cartas en mazos A:")
for cid, n in cont.most_common(25):
    print(f"  {nombres.get(cid, cid)}: {n}")