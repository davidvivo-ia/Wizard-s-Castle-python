"""Modelo inmutable del jugador."""

from __future__ import annotations

from dataclasses import dataclass, field, replace

from wizards_castle.domain.catalog import (
    ARMOR_CAPACITY,
    RACE_STATS,
    STAT_CAP,
    WEAPON_DAMAGE,
    Armor,
    Curse,
    Race,
    Sex,
    Treasure,
    Weapon,
)
from wizards_castle.domain.coordinates import Coord


@dataclass(frozen=True, slots=True)
class Player:
    """Estado completo del jugador. Inmutable: cualquier cambio devuelve uno nuevo."""

    name: str
    race: Race
    sex: Sex

    strength: int
    intelligence: int
    dexterity: int
    max_strength: int
    max_intelligence: int
    max_dexterity: int

    gold: int = 0
    flares: int = 0
    has_lamp: bool = False
    has_runestaff: bool = False
    has_orb_of_zot: bool = False
    is_blind: bool = False
    book_stuck: bool = False

    weapon: Weapon = Weapon.NONE
    armor: Armor = Armor.NONE
    armor_damage: int = 0

    treasures: frozenset[Treasure] = field(default_factory=frozenset)
    curses: frozenset[Curse] = field(default_factory=frozenset)

    position: Coord = field(default_factory=lambda: Coord(1, 4, 1))
    turn: int = 0

    @classmethod
    def fresh(cls, name: str, race: Race, sex: Sex, position: Coord) -> Player:
        """Crea un jugador con los stats base de su raza y oro inicial."""
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
            position=position,
        )

    @property
    def is_alive(self) -> bool:
        """`True` si todos los stats vitales son > 0."""
        return self.strength > 0 and self.intelligence > 0 and self.dexterity > 0

    @property
    def can_cast_spell(self) -> bool:
        """Requisito del original (línea 4220): `IQ > 14`."""
        return self.intelligence >= 15

    @property
    def weapon_damage(self) -> int:
        """Daño base del arma equipada."""
        return WEAPON_DAMAGE[self.weapon]

    def has_treasure(self, t: Treasure) -> bool:
        """Comprueba pertenencia al inventario de tesoros."""
        return t in self.treasures

    # ─── Mutadores funcionales ─────────────────────────────────────────────

    def at(self, position: Coord) -> Player:
        """Devuelve el jugador en una nueva posición."""
        return replace(self, position=position)

    def with_stats(self, *, strength: int = 0, intelligence: int = 0, dexterity: int = 0) -> Player:
        """Suma deltas a los stats, clampando en `[0, STAT_CAP]` y subiendo el tope si procede."""
        new_st = _clamp(self.strength + strength)
        new_iq = _clamp(self.intelligence + intelligence)
        new_dx = _clamp(self.dexterity + dexterity)
        return replace(
            self,
            strength=new_st,
            intelligence=new_iq,
            dexterity=new_dx,
            max_strength=max(self.max_strength, new_st),
            max_intelligence=max(self.max_intelligence, new_iq),
            max_dexterity=max(self.max_dexterity, new_dx),
        )

    def take_damage(self, amount: int) -> tuple[Player, int]:
        """Aplica `amount` puntos absorbiendo con armadura. Devuelve (jugador, daño_a_st)."""
        capacity = ARMOR_CAPACITY.get(self.armor, 0)
        soak = min(amount, max(0, capacity - self.armor_damage))
        new_armor_damage = self.armor_damage + soak
        broken = new_armor_damage >= capacity > 0
        st_dmg = amount - soak
        new = replace(
            self,
            armor=Armor.NONE if broken else self.armor,
            armor_damage=0 if broken else new_armor_damage,
            strength=max(0, self.strength - st_dmg),
        )
        return new, st_dmg

    def with_gold(self, delta: int) -> Player:
        """Suma oro (positivo o negativo), nunca por debajo de 0."""
        return replace(self, gold=max(0, self.gold + delta))

    def with_flares(self, delta: int) -> Player:
        """Suma bengalas, nunca por debajo de 0."""
        return replace(self, flares=max(0, self.flares + delta))

    def with_treasure(self, t: Treasure) -> Player:
        """Añade un tesoro al inventario."""
        return replace(self, treasures=self.treasures | {t})

    def without_treasure(self, t: Treasure) -> Player:
        """Quita un tesoro del inventario."""
        return replace(self, treasures=self.treasures - {t})

    def with_curse(self, c: Curse) -> Player:
        """Marca al jugador como afectado por una maldición."""
        return replace(self, curses=self.curses | {c})

    def with_weapon(self, w: Weapon) -> Player:
        """Cambia el arma equipada."""
        return replace(self, weapon=w)

    def with_armor(self, a: Armor) -> Player:
        """Cambia armadura, reseteando el daño absorbido."""
        return replace(self, armor=a, armor_damage=0)

    def with_lamp(self, value: bool = True) -> Player:
        """Activa o desactiva la lámpara."""
        return replace(self, has_lamp=value)

    def tick_turn(self) -> Player:
        """Avanza el contador de turnos en uno."""
        return replace(self, turn=self.turn + 1)


def _clamp(value: int) -> int:
    """Clampa un stat a `[0, STAT_CAP]`."""
    return max(0, min(STAT_CAP, value))
