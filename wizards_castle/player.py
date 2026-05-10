"""Player model: stats, inventory, curses, status helpers."""

from __future__ import annotations

from dataclasses import dataclass, field

from .data import (
    ARMOR_CAPACITY,
    Armor,
    CASTLE_SIZE,
    Curse,
    RACE_STATS,
    Race,
    Sex,
    Treasure,
    WEAPON_DAMAGE,
    Weapon,
)


@dataclass
class Player:
    name: str = "Adventurer"
    race: Race = Race.HUMAN
    sex: Sex = Sex.MALE

    strength: int = 8
    intelligence: int = 8
    dexterity: int = 8

    max_strength: int = 8
    max_intelligence: int = 8
    max_dexterity: int = 8

    gold: int = 0
    flares: int = 0
    has_lamp: bool = False
    has_runestaff: bool = False
    has_orb_of_zot: bool = False
    has_blindness: bool = False
    book_stuck: bool = False

    weapon: Weapon = Weapon.NONE
    armor: Armor = Armor.NONE
    armor_damage: int = 0  # hit points the armour has soaked

    treasures: set[Treasure] = field(default_factory=set)
    curses: set[Curse] = field(default_factory=set)

    position: tuple[int, int, int] = (1, 1, 1)
    turn: int = 0

    # ---- Construction helpers ----------------------------------------
    @classmethod
    def from_race(cls, name: str, race: Race, sex: Sex) -> "Player":
        profile = RACE_STATS[race]
        return cls(
            name=name,
            race=race,
            sex=sex,
            strength=profile.strength,
            intelligence=profile.intelligence,
            dexterity=profile.dexterity,
            max_strength=profile.strength,
            max_intelligence=profile.intelligence,
            max_dexterity=profile.dexterity,
        )

    # ---- Status -------------------------------------------------------
    @property
    def is_alive(self) -> bool:
        return self.strength > 0 and self.intelligence > 0 and self.dexterity > 0

    @property
    def can_cast_fireball(self) -> bool:
        return self.intelligence >= 15 and self.strength >= 1

    @property
    def can_cast_deathspell(self) -> bool:
        return self.intelligence >= 15 and self.strength >= 1

    def has_treasure(self, t: Treasure) -> bool:
        return t in self.treasures

    # ---- Damage / armour ---------------------------------------------
    def take_damage(self, amount: int) -> int:
        """Apply incoming damage, soaking with armour. Returns damage to STR."""
        soak = 0
        capacity = ARMOR_CAPACITY.get(self.armor, 0)
        if capacity > 0:
            remaining = capacity - self.armor_damage
            soak = min(amount, remaining)
            self.armor_damage += soak
            if self.armor_damage >= capacity:
                self.armor = Armor.NONE
                self.armor_damage = 0
        str_damage = amount - soak
        self.strength = max(0, self.strength - str_damage)
        return str_damage

    # ---- Stat clamps --------------------------------------------------
    def adjust(self, *, strength: int = 0, intelligence: int = 0, dexterity: int = 0) -> None:
        self.strength = max(0, min(self.max_strength + 50, self.strength + strength))
        self.intelligence = max(0, min(self.max_intelligence + 50, self.intelligence + intelligence))
        self.dexterity = max(0, min(self.max_dexterity + 50, self.dexterity + dexterity))
        # Track the lifetime maximum so pools can permanently raise the cap.
        self.max_strength = max(self.max_strength, self.strength)
        self.max_intelligence = max(self.max_intelligence, self.intelligence)
        self.max_dexterity = max(self.max_dexterity, self.dexterity)

    # ---- Combat helpers ----------------------------------------------
    @property
    def weapon_damage(self) -> int:
        return WEAPON_DAMAGE[self.weapon]

    def break_weapon(self) -> None:
        self.weapon = Weapon.NONE

    # ---- Display ------------------------------------------------------
    def status_lines(self) -> list[str]:
        x, y, z = self.position
        return [
            f"{self.name} the {self.race.value} ({self.sex.value})",
            f"  STR {self.strength:>2}/{self.max_strength}   "
            f"INT {self.intelligence:>2}/{self.max_intelligence}   "
            f"DEX {self.dexterity:>2}/{self.max_dexterity}",
            f"  Gold {self.gold}   Flares {self.flares}   "
            f"Lamp: {'yes' if self.has_lamp else 'no'}",
            f"  Weapon: {self.weapon.name.title()}   "
            f"Armor: {self.armor.name.title()} "
            f"({ARMOR_CAPACITY[self.armor] - self.armor_damage} left)",
            f"  Treasures: {', '.join(t.name for t in self.treasures) or 'none'}",
            f"  Curses: {', '.join(c.name for c in self.curses) or 'none'}",
            f"  Runestaff: {'yes' if self.has_runestaff else 'no'}   "
            f"Orb of Zot: {'yes' if self.has_orb_of_zot else 'no'}",
            f"  Floor {z}, ({x},{y})   Turn {self.turn}",
        ]
