from wizards_castle.data import (
    ARMOR_CAPACITY,
    Armor,
    RACE_STATS,
    Race,
    Sex,
    Treasure,
    Weapon,
)
from wizards_castle.player import Player


def test_from_race_uses_profile():
    p = Player.from_race("Bilbo", Race.HOBBIT, Sex.MALE)
    profile = RACE_STATS[Race.HOBBIT]
    assert (p.strength, p.intelligence, p.dexterity) == (
        profile.strength, profile.intelligence, profile.dexterity)
    assert p.is_alive


def test_armor_soaks_damage_then_breaks():
    p = Player.from_race("Tank", Race.HUMAN, Sex.MALE)
    p.armor = Armor.LEATHER
    capacity = ARMOR_CAPACITY[Armor.LEATHER]
    # Pour 100 damage: armour soaks `capacity`, rest hits STR.
    str_dmg = p.take_damage(100)
    assert str_dmg == 100 - capacity
    assert p.armor == Armor.NONE
    assert p.armor_damage == 0


def test_weapon_damage_lookup():
    p = Player.from_race("Sworder", Race.HUMAN, Sex.MALE)
    p.weapon = Weapon.SWORD
    assert p.weapon_damage == 3
    p.break_weapon()
    assert p.weapon == Weapon.NONE


def test_treasure_membership():
    p = Player.from_race("Hoarder", Race.ELF, Sex.FEMALE)
    p.treasures.add(Treasure.RUBY_RED)
    assert p.has_treasure(Treasure.RUBY_RED)
    assert not p.has_treasure(Treasure.SILMARIL)


def test_dies_when_strength_zero():
    p = Player.from_race("Doomed", Race.HUMAN, Sex.MALE)
    p.strength = 0
    assert not p.is_alive
