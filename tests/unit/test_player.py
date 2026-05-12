from __future__ import annotations

from dataclasses import replace

from wizards_castle.domain.catalog import (
    ARMOR_CAPACITY,
    RACE_STATS,
    Armor,
    Curse,
    Race,
    Sex,
    Treasure,
    Weapon,
)
from wizards_castle.domain.coordinates import Coord
from wizards_castle.domain.player import Player


def _hero(**kw: object) -> Player:
    base = Player.fresh("Test", Race.HUMAN, Sex.MALE, Coord(1, 4, 1))
    if kw:
        return replace(base, **kw)  # type: ignore[arg-type]
    return base


class TestFresh:
    def test_uses_race_profile(self) -> None:
        p = Player.fresh("Bilbo", Race.HOBBIT, Sex.MALE, Coord(1, 4, 1))
        prof = RACE_STATS[Race.HOBBIT]
        assert p.strength == prof.strength
        assert p.intelligence == prof.intelligence
        assert p.dexterity == prof.dexterity

    def test_alive_at_start(self) -> None:
        assert _hero().is_alive


class TestImmutability:
    def test_with_gold_returns_new_instance(self) -> None:
        p = _hero()
        q = p.with_gold(100)
        assert p.gold == 0
        assert q.gold == 100
        assert p is not q

    def test_at_returns_new(self) -> None:
        p = _hero()
        q = p.at(Coord(2, 2, 2))
        assert p.position == Coord(1, 4, 1)
        assert q.position == Coord(2, 2, 2)


class TestArmorAndDamage:
    def test_armor_soaks_damage_then_breaks(self) -> None:
        p = _hero(armor=Armor.LEATHER)
        cap = ARMOR_CAPACITY[Armor.LEATHER]
        new_p, st_dmg = p.take_damage(100)
        assert st_dmg == 100 - cap
        assert new_p.armor == Armor.NONE
        assert new_p.armor_damage == 0

    def test_armor_persists_when_not_overwhelmed(self) -> None:
        p = _hero(armor=Armor.PLATE)
        new_p, st_dmg = p.take_damage(3)
        assert st_dmg == 0
        assert new_p.armor == Armor.PLATE
        assert new_p.armor_damage == 3


class TestStats:
    def test_with_stats_clamps_to_18(self) -> None:
        p = _hero().with_stats(strength=100)
        assert p.strength == 18
        assert p.max_strength == 18

    def test_with_stats_floors_at_0(self) -> None:
        p = _hero().with_stats(strength=-1000)
        assert p.strength == 0
        assert not p.is_alive

    def test_can_cast_spell_threshold(self) -> None:
        assert not _hero().can_cast_spell  # IQ default 8
        assert _hero().with_stats(intelligence=10).can_cast_spell  # 8+10=18


class TestInventory:
    def test_add_remove_treasure(self) -> None:
        p = _hero().with_treasure(Treasure.OPAL_EYE)
        assert p.has_treasure(Treasure.OPAL_EYE)
        q = p.without_treasure(Treasure.OPAL_EYE)
        assert not q.has_treasure(Treasure.OPAL_EYE)

    def test_curse_added(self) -> None:
        p = _hero().with_curse(Curse.LEECH)
        assert Curse.LEECH in p.curses


class TestWeaponDamage:
    def test_damage_lookup(self) -> None:
        for w in Weapon:
            assert _hero(weapon=w).weapon_damage == int(w)
