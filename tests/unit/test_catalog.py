from __future__ import annotations

from wizards_castle.domain.catalog import (
    ARMOR_COST,
    CURSE_WARD,
    MONSTERS,
    RACE_STATS,
    WEAPON_DAMAGE,
    Armor,
    Curse,
    Race,
    Treasure,
    Weapon,
)


class TestRaceProfiles:
    def test_hobbit_has_most_bonus_points(self) -> None:
        # [DATO] OT = 8 + 4*(RC == 1)
        assert RACE_STATS[Race.HOBBIT].bonus_points == 12
        assert all(RACE_STATS[r].bonus_points == 8 for r in (Race.ELF, Race.HUMAN, Race.DWARF))

    def test_strength_increases_with_race_code(self) -> None:
        # ST = 2 + 2*RC, así que la fuerza aumenta con el código de raza.
        codes = [(Race.HOBBIT, 4), (Race.ELF, 6), (Race.HUMAN, 8), (Race.DWARF, 10)]
        for race, expected in codes:
            assert RACE_STATS[race].strength == expected

    def test_dexterity_decreases_with_race_code(self) -> None:
        codes = [(Race.HOBBIT, 12), (Race.ELF, 10), (Race.HUMAN, 8), (Race.DWARF, 6)]
        for race, expected in codes:
            assert RACE_STATS[race].dexterity == expected


class TestMonsters:
    def test_twelve_monsters(self) -> None:
        # [DATO] códigos 13..24 del original.
        assert len(MONSTERS) == 12

    def test_dragon_breaks_weapons(self) -> None:
        dragon = next(m for m in MONSTERS if m.name == "Dragón")
        assert dragon.can_break_weapon
        assert dragon.damage == 4
        assert dragon.hit_points == 13


class TestEquipment:
    def test_armor_costs_match_original(self) -> None:
        # [DATO] línea 1715 del original.
        assert ARMOR_COST[Armor.LEATHER] == 10
        assert ARMOR_COST[Armor.CHAINMAIL] == 20
        assert ARMOR_COST[Armor.PLATE] == 30

    def test_weapon_damage_matches_av_formula(self) -> None:
        for w in Weapon:
            assert WEAPON_DAMAGE[w] == int(w)


class TestTreasures:
    def test_eight_treasures(self) -> None:
        assert len(list(Treasure)) == 8


class TestCurses:
    def test_three_curses_with_wards(self) -> None:
        assert set(CURSE_WARD.keys()) == set(Curse)
        # Cada curse tiene un tesoro de protección distinto.
        assert len(set(CURSE_WARD.values())) == 3
