from __future__ import annotations

import pytest

from tests.conftest import FakeRandom
from wizards_castle.application.character_creation import (
    CharacterChoices,
    create_new_game,
)
from wizards_castle.domain.catalog import Armor, Race, Sex, Weapon


class TestCreateNewGame:
    def test_basic_creation(self) -> None:
        choices = CharacterChoices(name="Bilbo", race=Race.HOBBIT, sex=Sex.MALE)
        state = create_new_game(choices, FakeRandom(0), seed=0)
        assert state.player.name == "Bilbo"
        assert state.player.race == Race.HOBBIT
        assert state.player.gold == 60
        assert state.player.position == state.castle.entrance

    def test_bonus_distribution_applied(self) -> None:
        choices = CharacterChoices(
            name="X", race=Race.HUMAN, sex=Sex.MALE, bonus_strength=4, bonus_dexterity=4
        )
        state = create_new_game(choices, FakeRandom(0))
        assert state.player.strength == 12
        assert state.player.dexterity == 12

    def test_overspend_raises(self) -> None:
        # 30 plate + 30 sword + 20 lamp = 80 > 60 gp inicial.
        choices = CharacterChoices(
            name="X",
            race=Race.HUMAN,
            sex=Sex.MALE,
            armor=Armor.PLATE,
            weapon=Weapon.SWORD,
            buy_lamp=True,
        )
        with pytest.raises(ValueError, match="compras suman"):
            create_new_game(choices, FakeRandom(0))

    def test_buy_partial_kit(self) -> None:
        choices = CharacterChoices(
            name="X",
            race=Race.HUMAN,
            sex=Sex.MALE,
            armor=Armor.LEATHER,  # 10
            weapon=Weapon.MACE,  # 20
            flares=10,  # 10
        )
        state = create_new_game(choices, FakeRandom(0))
        assert state.player.gold == 60 - 40
        assert state.player.armor == Armor.LEATHER
        assert state.player.weapon == Weapon.MACE
        assert state.player.flares == 10

    def test_excess_bonus_raises(self) -> None:
        choices = CharacterChoices(name="X", race=Race.HUMAN, sex=Sex.MALE, bonus_strength=999)
        with pytest.raises(ValueError, match="bonus total"):
            create_new_game(choices, FakeRandom(0))

    def test_negative_bonus_raises(self) -> None:
        choices = CharacterChoices(name="X", race=Race.HUMAN, sex=Sex.MALE, bonus_strength=-1)
        with pytest.raises(ValueError, match="negativos"):
            create_new_game(choices, FakeRandom(0))
