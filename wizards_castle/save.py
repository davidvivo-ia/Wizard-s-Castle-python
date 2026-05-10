"""JSON save/load for the game state.

We serialise the castle as a flat list of glyph/payload tuples so the file
stays human-readable and small (~1-2 KB).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .castle import Castle, Room
from .data import (
    Armor,
    CASTLE_LEVELS,
    CASTLE_SIZE,
    Curse,
    Glyph,
    Race,
    Sex,
    Treasure,
    Weapon,
)
from .player import Player


SAVE_VERSION = 1


def _room_to_obj(r: Room) -> dict[str, Any]:
    return {
        "g": r.glyph.value,
        "p": r.payload,
        "d": r.discovered,
        "c": r.cleared,
    }


def _obj_to_room(obj: dict[str, Any]) -> Room:
    return Room(
        glyph=Glyph(obj["g"]),
        payload=obj.get("p"),
        discovered=bool(obj.get("d", False)),
        cleared=bool(obj.get("c", False)),
    )


def to_dict(player: Player, castle: Castle, seed: int | None) -> dict[str, Any]:
    grid = [
        [
            [_room_to_obj(castle.at((x, y, z))) for x in range(1, CASTLE_SIZE + 1)]
            for y in range(1, CASTLE_SIZE + 1)
        ]
        for z in range(1, CASTLE_LEVELS + 1)
    ]
    return {
        "version": SAVE_VERSION,
        "seed": seed,
        "player": {
            "name": player.name,
            "race": player.race.value,
            "sex": player.sex.value,
            "stats": [player.strength, player.intelligence, player.dexterity],
            "max_stats": [player.max_strength, player.max_intelligence,
                          player.max_dexterity],
            "gold": player.gold,
            "flares": player.flares,
            "lamp": player.has_lamp,
            "runestaff": player.has_runestaff,
            "orb": player.has_orb_of_zot,
            "blind": player.has_blindness,
            "book_stuck": player.book_stuck,
            "weapon": int(player.weapon),
            "armor": int(player.armor),
            "armor_damage": player.armor_damage,
            "treasures": sorted(int(t) for t in player.treasures),
            "curses": sorted(c.name for c in player.curses),
            "position": list(player.position),
            "turn": player.turn,
        },
        "castle": {
            "grid": grid,
            "entrance": list(castle.entrance),
            "orb_of_zot_at": list(castle.orb_of_zot_at),
            "runestaff_monster_at": list(castle.runestaff_monster_at),
        },
    }


def from_dict(data: dict[str, Any]) -> tuple[Player, Castle, int | None]:
    if data.get("version") != SAVE_VERSION:
        raise ValueError(f"Unsupported save version: {data.get('version')}")
    p = data["player"]
    player = Player(
        name=p["name"],
        race=Race(p["race"]),
        sex=Sex(p["sex"]),
        strength=p["stats"][0],
        intelligence=p["stats"][1],
        dexterity=p["stats"][2],
        max_strength=p["max_stats"][0],
        max_intelligence=p["max_stats"][1],
        max_dexterity=p["max_stats"][2],
        gold=p["gold"],
        flares=p["flares"],
        has_lamp=p["lamp"],
        has_runestaff=p["runestaff"],
        has_orb_of_zot=p["orb"],
        has_blindness=p["blind"],
        book_stuck=p["book_stuck"],
        weapon=Weapon(p["weapon"]),
        armor=Armor(p["armor"]),
        armor_damage=p["armor_damage"],
        treasures={Treasure(t) for t in p["treasures"]},
        curses={Curse[c] for c in p["curses"]},
        position=tuple(p["position"]),  # type: ignore[arg-type]
        turn=p["turn"],
    )
    c = data["castle"]
    grid = [
        [
            [_obj_to_room(c["grid"][z][y][x]) for x in range(CASTLE_SIZE)]
            for y in range(CASTLE_SIZE)
        ]
        for z in range(CASTLE_LEVELS)
    ]
    castle = Castle(
        grid=grid,
        entrance=tuple(c["entrance"]),  # type: ignore[arg-type]
        orb_of_zot_at=tuple(c["orb_of_zot_at"]),  # type: ignore[arg-type]
        runestaff_monster_at=tuple(c["runestaff_monster_at"]),  # type: ignore[arg-type]
    )
    return player, castle, data.get("seed")


def save_to_path(path: Path, player: Player, castle: Castle, seed: int | None) -> None:
    path.write_text(json.dumps(to_dict(player, castle, seed), indent=2))


def load_from_path(path: Path) -> tuple[Player, Castle, int | None]:
    return from_dict(json.loads(path.read_text()))
