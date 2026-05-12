from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from tests.conftest import FakeRandom
from wizards_castle.application.character_creation import (
    CharacterChoices,
    create_new_game,
)
from wizards_castle.domain.catalog import Curse, Race, Sex, Treasure, Weapon
from wizards_castle.domain.errors import SaveCorruptedError
from wizards_castle.infrastructure.save import load_from_path, save_to_path


def _state_with_inventory():
    state = create_new_game(
        CharacterChoices(name="Eli", race=Race.ELF, sex=Sex.FEMALE, weapon=Weapon.MACE, flares=5),
        FakeRandom(2026),
        seed=2026,
    )
    enriched = replace(
        state.player,
        treasures=frozenset({Treasure.RUBY_RED, Treasure.PALANTIR}),
        curses=frozenset({Curse.LETHARGY}),
        has_runestaff=True,
    )
    return state.with_player(enriched)


class TestRoundTrip:
    def test_save_and_load_preserves_state(self, tmp_path: Path) -> None:
        s = _state_with_inventory()
        path = tmp_path / "slot.json"
        save_to_path(path, s)
        loaded = load_from_path(path)
        assert loaded.player.name == "Eli"
        assert loaded.player.race == Race.ELF
        assert loaded.player.sex == Sex.FEMALE
        assert loaded.player.weapon == Weapon.MACE
        assert loaded.player.flares == 5
        assert loaded.player.has_runestaff
        assert Treasure.RUBY_RED in loaded.player.treasures
        assert Curse.LETHARGY in loaded.player.curses
        assert loaded.seed == 2026
        assert loaded.castle.entrance == s.castle.entrance
        for c in s.castle.all_coords():
            assert loaded.castle.at(c).glyph == s.castle.at(c).glyph

    def test_load_corrupted_raises(self, tmp_path: Path) -> None:
        path = tmp_path / "bad.json"
        path.write_text("{not json")
        with pytest.raises(SaveCorruptedError):
            load_from_path(path)

    def test_load_wrong_version_raises(self, tmp_path: Path) -> None:
        s = _state_with_inventory()
        path = tmp_path / "v2.json"
        save_to_path(path, s)
        # Modificamos la versión.
        text = path.read_text().replace('"version": 1', '"version": 99')
        path.write_text(text)
        with pytest.raises(SaveCorruptedError):
            load_from_path(path)
