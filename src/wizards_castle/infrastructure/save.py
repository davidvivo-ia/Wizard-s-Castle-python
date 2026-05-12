"""Persistencia JSON de partidas con Pydantic v2 (versión 1)."""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field, ValidationError

from wizards_castle.domain.castle import Castle
from wizards_castle.domain.catalog import (
    Armor,
    Curse,
    Glyph,
    Race,
    Sex,
    Treasure,
    Weapon,
)
from wizards_castle.domain.coordinates import Coord
from wizards_castle.domain.errors import SaveCorruptedError
from wizards_castle.domain.player import Player
from wizards_castle.domain.room import Room
from wizards_castle.domain.state import GameState

SAVE_VERSION = 1


class _RoomModel(BaseModel):
    g: str
    p: int | None = None
    d: bool = False
    c: bool = False


class _CoordModel(BaseModel):
    x: int
    y: int
    z: int


class _PlayerModel(BaseModel):
    name: str
    race: str
    sex: str
    strength: int
    intelligence: int
    dexterity: int
    max_strength: int
    max_intelligence: int
    max_dexterity: int
    gold: int
    flares: int
    has_lamp: bool
    has_runestaff: bool
    has_orb_of_zot: bool
    is_blind: bool
    book_stuck: bool
    weapon: int
    armor: int
    armor_damage: int
    treasures: list[int] = Field(default_factory=list)
    curses: list[str] = Field(default_factory=list)
    position: _CoordModel
    turn: int


class _CastleModel(BaseModel):
    grid: list[list[list[_RoomModel]]]
    entrance: _CoordModel
    orb_of_zot_at: _CoordModel
    runestaff_monster_at: _CoordModel


class _SaveModel(BaseModel):
    version: int
    seed: int | None = None
    classic_mode: bool = False
    vendor_hostile: bool = False
    player: _PlayerModel
    castle: _CastleModel


def _coord(c: Coord) -> _CoordModel:
    return _CoordModel(x=c.x, y=c.y, z=c.z)


def _to_coord(m: _CoordModel) -> Coord:
    return Coord(m.x, m.y, m.z)


def _to_save_model(state: GameState) -> _SaveModel:
    p = state.player
    grid = [
        [
            [
                _RoomModel(g=room.glyph.value, p=room.payload, d=room.discovered, c=room.cleared)
                for room in row
            ]
            for row in level
        ]
        for level in state.castle.grid
    ]
    return _SaveModel(
        version=SAVE_VERSION,
        seed=state.seed,
        classic_mode=state.classic_mode,
        vendor_hostile=state.vendor_hostile,
        player=_PlayerModel(
            name=p.name,
            race=p.race.value,
            sex=p.sex.value,
            strength=p.strength,
            intelligence=p.intelligence,
            dexterity=p.dexterity,
            max_strength=p.max_strength,
            max_intelligence=p.max_intelligence,
            max_dexterity=p.max_dexterity,
            gold=p.gold,
            flares=p.flares,
            has_lamp=p.has_lamp,
            has_runestaff=p.has_runestaff,
            has_orb_of_zot=p.has_orb_of_zot,
            is_blind=p.is_blind,
            book_stuck=p.book_stuck,
            weapon=int(p.weapon),
            armor=int(p.armor),
            armor_damage=p.armor_damage,
            treasures=sorted(int(t) for t in p.treasures),
            curses=sorted(c.name for c in p.curses),
            position=_coord(p.position),
            turn=p.turn,
        ),
        castle=_CastleModel(
            grid=grid,
            entrance=_coord(state.castle.entrance),
            orb_of_zot_at=_coord(state.castle.orb_of_zot_at),
            runestaff_monster_at=_coord(state.castle.runestaff_monster_at),
        ),
    )


def _from_save_model(model: _SaveModel) -> GameState:
    pm = model.player
    cm = model.castle
    grid = tuple(
        tuple(
            tuple(
                Room(
                    glyph=Glyph(room.g),
                    payload=room.p,
                    discovered=room.d,
                    cleared=room.c,
                )
                for room in row
            )
            for row in level
        )
        for level in cm.grid
    )
    castle = Castle(
        grid=grid,
        entrance=_to_coord(cm.entrance),
        orb_of_zot_at=_to_coord(cm.orb_of_zot_at),
        runestaff_monster_at=_to_coord(cm.runestaff_monster_at),
    )
    player = Player(
        name=pm.name,
        race=Race(pm.race),
        sex=Sex(pm.sex),
        strength=pm.strength,
        intelligence=pm.intelligence,
        dexterity=pm.dexterity,
        max_strength=pm.max_strength,
        max_intelligence=pm.max_intelligence,
        max_dexterity=pm.max_dexterity,
        gold=pm.gold,
        flares=pm.flares,
        has_lamp=pm.has_lamp,
        has_runestaff=pm.has_runestaff,
        has_orb_of_zot=pm.has_orb_of_zot,
        is_blind=pm.is_blind,
        book_stuck=pm.book_stuck,
        weapon=Weapon(pm.weapon),
        armor=Armor(pm.armor),
        armor_damage=pm.armor_damage,
        treasures=frozenset(Treasure(t) for t in pm.treasures),
        curses=frozenset(Curse[c] for c in pm.curses),
        position=_to_coord(pm.position),
        turn=pm.turn,
    )
    return GameState(
        player=player,
        castle=castle,
        seed=model.seed,
        classic_mode=model.classic_mode,
        vendor_hostile=model.vendor_hostile,
    )


def save_to_path(path: Path, state: GameState) -> None:
    """Serializa `state` a JSON en `path`."""
    model = _to_save_model(state)
    path.write_text(model.model_dump_json(indent=2), encoding="utf-8")


def load_from_path(path: Path) -> GameState:
    """Carga un `GameState` desde `path`."""
    raw = path.read_text(encoding="utf-8")
    try:
        model = _SaveModel.model_validate_json(raw)
    except ValidationError as exc:
        msg = f"save corrupto en {path}: {exc}"
        raise SaveCorruptedError(msg) from exc
    if model.version != SAVE_VERSION:
        msg = f"versión de save no soportada: {model.version}"
        raise SaveCorruptedError(msg)
    return _from_save_model(model)
