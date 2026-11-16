import json
from pathlib import Path

VARIANT_BY_LEVEL = {1: "evo", 2: "hero"}
SUFFIX = {"normal": "", "evo": "e", "hero": "h"}


def card_variant(card: dict) -> str:
    lvl = card.get("evolutionLevel")
    if lvl is None:
        return "normal"
    return VARIANT_BY_LEVEL.get(lvl, f"x{lvl}")


def deck_key(cards: list[dict]) -> str:
    """Mazo canónico: ids ordenados con sufijo e (evo) o h (héroe)."""
    parts = sorted((c["id"], card_variant(c)) for c in cards)
    return ",".join(f"{cid}{SUFFIX.get(v, v)}" for cid, v in parts)


def tower_id(player: dict):
    support = player.get("supportCards") or [{}]
    return support[0].get("id")


def parse_battle(b: dict) -> dict | None:
    if len(b["team"]) != 1 or len(b["opponent"]) != 1:
        return None  # no es 1v1
    me, opp = b["team"][0], b["opponent"][0]
    if len(me["cards"]) != 8 or len(opp["cards"]) != 8:
        return None
    if me["crowns"] == opp["crowns"]:
        return None  # sin ganador claro
    tags = sorted([me["tag"], opp["tag"]])
    return {
        "battle_key": f'{b["battleTime"]}|{tags[0]}|{tags[1]}',
        "battle_time": b["battleTime"],
        "type": b["type"],
        "player_tag": me["tag"],
        "opponent_tag": opp["tag"],
        "player_deck": deck_key(me["cards"]),
        "opponent_deck": deck_key(opp["cards"]),
        "player_tower": tower_id(me),
        "opponent_tower": tower_id(opp),
        "player_won": int(me["crowns"] > opp["crowns"]),
    }

def parse_duel(b: dict) -> dict | None:
    if b.get("gameMode", {}).get("name") != "Competitive_Multideck":
        return None
    if len(b["team"]) != 1 or len(b["opponent"]) != 1:
        return None
    me, opp = b["team"][0], b["opponent"][0]
    my_rounds, opp_rounds = me.get("rounds"), opp.get("rounds")
    if not my_rounds or not opp_rounds or len(my_rounds) != len(opp_rounds):
        return None

    rounds, ids_me, ids_opp = [], [], []
    for i, (mr, orr) in enumerate(zip(my_rounds, opp_rounds), start=1):
        if len(mr["cards"]) != 8 or len(orr["cards"]) != 8:
            return None
        if mr["crowns"] == orr["crowns"]:
            return None
        ids_me += [c["id"] for c in mr["cards"]]
        ids_opp += [c["id"] for c in orr["cards"]]
        rounds.append({
            "round_no": i,
            "player_deck": deck_key(mr["cards"]),
            "opponent_deck": deck_key(orr["cards"]),
            "player_crowns": mr["crowns"],
            "opponent_crowns": orr["crowns"],
            "player_won": int(mr["crowns"] > orr["crowns"]),
        })

    won = sum(r["player_won"] for r in rounds)
    tags = sorted([me["tag"], opp["tag"]])
    return {
        "battle_key": f'{b["battleTime"]}|{tags[0]}|{tags[1]}',
        "battle_time": b["battleTime"],
        "player_tag": me["tag"],
        "opponent_tag": opp["tag"],
        "player_won_duel": int(won > len(rounds) / 2),
        "no_repeats": len(set(ids_me)) == len(ids_me)
                      and len(set(ids_opp)) == len(ids_opp),
        "rounds": rounds,
    }

if __name__ == "__main__":
    from pprint import pprint

    data = json.loads(Path("multimodo.json").read_text(encoding="utf-8"))
    for b in data:
        pprint(parse_battle(b) or parse_duel(b))