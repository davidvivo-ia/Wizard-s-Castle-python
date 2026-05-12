from __future__ import annotations

from dataclasses import replace

import pytest

from tests.conftest import FakeRandom
from wizards_castle.application.character_creation import (
    CharacterChoices,
    create_new_game,
)
from wizards_castle.application.commands import Command, parse
from wizards_castle.application.room_events import (
    drink_pool,
    pick_up_treasure,
    resolve_passive_room,
    tick_curses,
)
from wizards_castle.domain.catalog import Curse, Glyph, Race, Sex, Treasure
from wizards_castle.domain.coordinates import Coord
from wizards_castle.domain.errors import InvalidCommandError
from wizards_castle.domain.room import Room


def _state():
    return create_new_game(CharacterChoices(name="X", race=Race.HUMAN, sex=Sex.MALE), FakeRandom(0))


class TestPassiveRoom:
    def test_gold_pickup(self) -> None:
        s = _state()
        # Plantamos una sala de oro en la posición del jugador.
        gold_room = Room(glyph=Glyph.GOLD, discovered=True)
        new_castle = s.castle.with_room(s.player.position, gold_room)
        s2 = s.with_castle(new_castle)
        s3, events = resolve_passive_room(s2, FakeRandom(1))
        assert s3.player.gold > s2.player.gold
        assert s3.castle.at(s2.player.position).glyph == Glyph.EMPTY
        assert any("oro" in e.message.lower() for e in events)

    def test_flares_pickup(self) -> None:
        s = _state()
        flare_room = Room(glyph=Glyph.FLARES, discovered=True)
        new_castle = s.castle.with_room(s.player.position, flare_room)
        s2 = s.with_castle(new_castle)
        s3, _ = resolve_passive_room(s2, FakeRandom(1))
        assert s3.player.flares > s2.player.flares

    def test_sinkhole_drops_one_level(self) -> None:
        s = _state()
        sink = Room(glyph=Glyph.SINKHOLE, discovered=True)
        new_castle = s.castle.with_room(s.player.position, sink)
        s2 = s.with_castle(new_castle)
        s3, events = resolve_passive_room(s2, FakeRandom(1))
        assert s3.player.position.z == s2.player.position.z + 1
        assert any("cede" in e.message for e in events)

    def test_warp_with_orb_grants_it(self) -> None:
        s = _state()
        # Construimos una sala warp en la coord del orbe.
        target = s.castle.orb_of_zot_at
        s2 = s.with_player(s.player.at(target))
        s3, events = resolve_passive_room(s2, FakeRandom(1))
        assert s3.player.has_orb_of_zot
        assert any("ORBE DE ZOT" in e.message for e in events)


class TestPickUpTreasure:
    def test_picks_up_when_treasure_room(self) -> None:
        s = _state()
        room = Room(glyph=Glyph.TREASURE, payload=int(Treasure.SILMARIL), discovered=True)
        s2 = s.with_castle(s.castle.with_room(s.player.position, room))
        s3, events = pick_up_treasure(s2, FakeRandom(0))
        assert Treasure.SILMARIL in s3.player.treasures
        assert any("Silmaril" in e.message for e in events)

    def test_no_op_on_empty(self) -> None:
        s = _state()
        s.with_castle(s.castle.with_room(s.player.position, Room(glyph=Glyph.EMPTY)))
        _, events = pick_up_treasure(s, FakeRandom(0))
        assert events == ()


class TestDrinkPool:
    def test_no_pool_warns(self) -> None:
        s = _state()
        _, events = drink_pool(s, FakeRandom(0))
        assert any("charco" in e.message.lower() for e in events)

    def test_pool_changes_player(self) -> None:
        s = _state()
        pool = Room(glyph=Glyph.POOL, discovered=True)
        s2 = s.with_castle(s.castle.with_room(s.player.position, pool))
        s3, events = drink_pool(s2, FakeRandom(0))
        # No verificamos qué cambia (es aleatorio), sólo que algo pasó.
        assert events != ()
        assert s3 != s2


class TestTickCurses:
    def test_tick_advances_turn(self) -> None:
        s = _state()
        s2, _ = tick_curses(s, FakeRandom(0))
        assert s2.player.turn == s.player.turn + 1

    def test_leech_drains_gold(self) -> None:
        s = _state()
        cursed = replace(s.player, curses=frozenset({Curse.LEECH}), gold=100)
        s2 = s.with_player(cursed)
        # En 50 ticks debería al menos perder algo de oro
        for seed in range(50):
            s3, _ = tick_curses(s2, FakeRandom(seed))
            if s3.player.gold < 100:
                return
        raise AssertionError("la sanguijuela debería robar oro en algún seed")


class TestCommandParse:
    def test_single_letter(self) -> None:
        assert parse("n") == Command.NORTH
        assert parse("Q") == Command.QUIT

    def test_dr_alias(self) -> None:
        assert parse("DR") == Command.DRINK
        assert parse("drink") == Command.DRINK

    def test_help_aliases(self) -> None:
        assert parse("?") == Command.HELP
        assert parse("h") == Command.HELP

    def test_unknown_raises(self) -> None:
        with pytest.raises(InvalidCommandError):
            parse("Z")
        with pytest.raises(InvalidCommandError):
            parse("")


def _unused() -> None:
    """Mantener importación de Coord para evitar warning en runtime."""
    _ = Coord(1, 1, 1)
