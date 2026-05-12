from __future__ import annotations

from dataclasses import replace

from tests.conftest import FakeRandom
from wizards_castle.domain.castle import generate_castle
from wizards_castle.domain.catalog import Race, Sex
from wizards_castle.domain.player import Player
from wizards_castle.domain.state import GameState


def _state() -> GameState:
    castle = generate_castle(FakeRandom(0))
    player = Player.fresh("Test", Race.HUMAN, Sex.MALE, castle.entrance)
    return GameState(player=player, castle=castle, seed=0)


class TestGameState:
    def test_with_player_returns_new_state(self) -> None:
        s = _state()
        s2 = s.with_player(s.player.with_gold(100))
        assert s.player.gold == 0
        assert s2.player.gold == 100

    def test_is_won_only_with_orb_at_entrance(self) -> None:
        s = _state()
        assert not s.is_won
        with_orb = s.with_player(replace_with(s.player, has_orb_of_zot=True))
        assert with_orb.is_won

    def test_is_lost_when_dead(self) -> None:
        s = _state()
        dead = s.with_player(s.player.with_stats(strength=-100))
        assert dead.is_lost
        assert dead.is_finished

    def test_vendor_hostility_toggles(self) -> None:
        s = _state().with_vendor_hostile(True)
        assert s.vendor_hostile is True

    def test_with_castle_swaps_castle(self) -> None:
        s = _state()
        new_castle = s.castle.with_room(s.castle.entrance, s.castle.at(s.castle.entrance).clear())
        s2 = s.with_castle(new_castle)
        assert s2.castle is new_castle
        assert s.castle is not new_castle


def replace_with(player: Player, **kw: object) -> Player:
    """Helper para mutar un player en tests."""
    return replace(player, **kw)  # type: ignore[arg-type]
