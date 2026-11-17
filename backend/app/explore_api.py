import json
import sys
from urllib.parse import quote

import httpx

from .config import settings

BASE = "https://api.clashroyale.com/v1"
HEADERS = {"Authorization": f"Bearer {settings.cr_api_key}"}


def get(path: str, **params):
    r = httpx.get(f"{BASE}{path}", headers=HEADERS, params=params, timeout=15)
    r.raise_for_status()
    return r.json()


def main() -> None:
    mode = sys.argv[1] if len(sys.argv) > 1 else ""

    if mode == "locations":
        for loc in get("/locations", limit=1000)["items"]:
            if not loc.get("isCountry"):
                print(loc["id"], loc["name"])

    elif mode == "players":
        loc_id, limit = sys.argv[2], int(sys.argv[3])
        for p in get(f"/locations/{loc_id}/rankings/players", limit=limit)["items"]:
            print(p["tag"], p["name"])

    elif mode == "battlelog":
        tag = quote("#" + sys.argv[2].lstrip("#"), safe="")
        battles = get(f"/players/{tag}/battlelog")
        print(f"{len(battles)} batallas")
        por_modo = {}
        for b in battles:
            por_modo.setdefault(b.get("gameMode", {}).get("name"), b)
        with open("multimodo.json", "w", encoding="utf-8") as f:
            json.dump(list(por_modo.values()), f, indent=2, ensure_ascii=False)
        print("Una batalla por modo:", list(por_modo))
            
    elif mode == "seasons":
        data = get("/locations/global/seasons")
        for s in data.get("items", [])[-5:]:
            print(s)

    elif mode == "pol":
        season, limit = sys.argv[2], int(sys.argv[3])
        data = get(
            f"/locations/global/pathoflegend/{season}/rankings/players",
            limit=limit,
        )
        for p in data.get("items", []):
            print(p["tag"], p["name"])
    else:
        print("Uso: locations | players <id> <n> | battlelog <tag>")


if __name__ == "__main__":
    main()