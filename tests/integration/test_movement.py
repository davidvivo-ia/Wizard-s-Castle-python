from __future__ import annotations

from dataclasses import replace

import pytest

from tests.conftest import FakeRandom
from wizards_castle.application.character_creation import (
    CharacterChoices,
    create_new_game,
)
from wizards_castle.application.movement import step, teleport, use_stairs
from wizards_castle.domain.catalog import CASTLE_WIDTH, Race, Sex
from wizards_castle.domain.coordinates import Coord, Direction
from wizards_castle.domain.errors import InvalidMoveError, NoStairsError


def _state():
    return create_new_game(CharacterChoices(name="X", race=Race.HUMAN, sex=Sex.MALE), FakeRandom(0))


class TestStep:
    def test_north_wraps(self) -> None:
        s = _state()
        # Player at (1, 4, 1). North goes to (1, 3, 1).
        s2, _ = step(s, Direction.NORTH)
        assert s2.player.position == Coord(1, 3, 1)

    def test_west_wraps_to_max(self) -> None:
        s = _state()
        s2, _ = step(s, Direction.WEST)
        assert s2.player.position == Coord(CASTLE_WIDTH, 4, 1)

    def test_step_marks_room_discovered(self) -> None:
        s = _state()
        s2, _ = step(s, Direction.SOUTH)
        assert s2.castle.at(s2.player.position).discovered


class TestStairs:
    def test_no_stairs_raises(self) -> None:
        s = _state()
        with pytest.raises(NoStairsError):
            use_stairs(s, going_up=True)


class TestTeleport:
    def test_without_runestaff_raises(self) -> None:
        s = _state()
        with pytest.raises(InvalidMoveError):
            teleport(s, Coord(2, 2, 2))

    def test_with_runestaff_ok(self) -> None:
        s = _state()
        s = s.with_player(replace(s.player, has_runestaff=True))
        target = Coord(5, 5, 5)
        s2, events = teleport(s, target)
        assert s2.player.position == target
        assert any("Runestaff" in e.message for e in events)
