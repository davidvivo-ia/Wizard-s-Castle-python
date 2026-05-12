"""Catálogo de constantes del juego: razas, monstruos, tesoros, glifos, precios.

Los valores siguen el listado canónico `legacy/exidy-sorcerer/origwiz.bas`
(*Recreational Computing*, jul/ago 1980). Cuando dos versiones discrepan,
ganamos esa.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, IntEnum, StrEnum, auto

# ─── Constantes globales del castillo ──────────────────────────────────────

CASTLE_WIDTH = 8
CASTLE_HEIGHT = 8
CASTLE_LEVELS = 8
START_GOLD = 60
LAMP_COST = 20
FLARE_COST = 1
STAT_CAP = 18  # FNC del original clampa a 18


# ─── Razas ─────────────────────────────────────────────────────────────────


class Race(StrEnum):
    """Las cuatro razas jugables del original."""

    HOBBIT = "Hobbit"
    ELF = "Elf"
    HUMAN = "Human"
    DWARF = "Dwarf"

    @property
    def code(self) -> int:
        """Código RC del listado original (1..4). [DATO] línea 1545."""
        return {Race.HOBBIT: 1, Race.ELF: 2, Race.HUMAN: 3, Race.DWARF: 4}[self]


class Sex(StrEnum):
    """Dos sexos del original."""

    MALE = "Male"
    FEMALE = "Female"


@dataclass(frozen=True, slots=True)
class RaceProfile:
    """Stats iniciales y puntos extra de una raza.

    Fórmulas del listado (líneas 1425-1565):
        ST = 2 + 2 * RC
        DX = 14 - 2 * RC
        IQ = 8 (igual para todos)
        OT = 8 + 4 * (RC == 1)   # los hobbits reciben 12 puntos extra
    """

    strength: int
    intelligence: int
    dexterity: int
    bonus_points: int


RACE_STATS: dict[Race, RaceProfile] = {
    Race.HOBBIT: RaceProfile(strength=4, intelligence=8, dexterity=12, bonus_points=12),
    Race.ELF: RaceProfile(strength=6, intelligence=8, dexterity=10, bonus_points=8),
    Race.HUMAN: RaceProfile(strength=8, intelligence=8, dexterity=8, bonus_points=8),
    Race.DWARF: RaceProfile(strength=10, intelligence=8, dexterity=6, bonus_points=8),
}


# ─── Equipamiento ──────────────────────────────────────────────────────────


class Armor(IntEnum):
    """AV del original (líneas 1730, 4860)."""

    NONE = 0
    LEATHER = 1
    CHAINMAIL = 2
    PLATE = 3


ARMOR_NAME: dict[Armor, str] = {
    Armor.NONE: "sin armadura",
    Armor.LEATHER: "cuero",
    Armor.CHAINMAIL: "cota de malla",
    Armor.PLATE: "armadura de placas",
}
ARMOR_COST: dict[Armor, int] = {Armor.LEATHER: 10, Armor.CHAINMAIL: 20, Armor.PLATE: 30}
ARMOR_CAPACITY: dict[Armor, int] = {
    Armor.NONE: 0,
    Armor.LEATHER: 7,
    Armor.CHAINMAIL: 14,
    Armor.PLATE: 21,
}


class Weapon(IntEnum):
    """WV del original."""

    NONE = 0
    DAGGER = 1
    MACE = 2
    SWORD = 3


WEAPON_NAME: dict[Weapon, str] = {
    Weapon.NONE: "sin arma",
    Weapon.DAGGER: "una daga",
    Weapon.MACE: "una maza",
    Weapon.SWORD: "una espada",
}
WEAPON_COST: dict[Weapon, int] = {Weapon.DAGGER: 10, Weapon.MACE: 20, Weapon.SWORD: 30}
WEAPON_DAMAGE: dict[Weapon, int] = {
    Weapon.NONE: 0,
    Weapon.DAGGER: 1,
    Weapon.MACE: 2,
    Weapon.SWORD: 3,
}


# ─── Monstruos ─────────────────────────────────────────────────────────────


@dataclass(frozen=True, slots=True)
class MonsterStats:
    """Stats de un monstruo. HP = `hit_points`, daño = `damage`."""

    name: str
    hit_points: int
    damage: int
    can_break_weapon: bool = False  # Gargoyle (21) y Dragon (24) en el original.


# Orden = código de habitación 13..24. [DATO] línea 5240-5250.
# HP = código + 2, daño = ceil(código_local / 2). Reproducido fielmente.
MONSTERS: tuple[MonsterStats, ...] = (
    MonsterStats("Kobold", 2, 1),
    MonsterStats("Orco", 3, 1),
    MonsterStats("Lobo", 4, 1),
    MonsterStats("Goblin", 5, 1),
    MonsterStats("Ogro", 6, 2),
    MonsterStats("Trol", 7, 2),
    MonsterStats("Oso", 8, 2),
    MonsterStats("Minotauro", 9, 3),
    MonsterStats("Gárgola", 10, 3, can_break_weapon=True),
    MonsterStats("Quimera", 11, 3),
    MonsterStats("Balrog", 12, 4),
    MonsterStats("Dragón", 13, 4, can_break_weapon=True),
)


# ─── Tesoros ───────────────────────────────────────────────────────────────


class Treasure(IntEnum):
    """Códigos 26..33 del original (líneas 5250-5260)."""

    RUBY_RED = 0
    NORN_STONE = 1
    PALE_PEARL = 2
    OPAL_EYE = 3
    GREEN_GEM = 4
    BLUE_FLAME = 5
    PALANTIR = 6
    SILMARIL = 7


TREASURE_NAME: dict[Treasure, str] = {
    Treasure.RUBY_RED: "el Rubí Rojo",
    Treasure.NORN_STONE: "la Piedra Norn",
    Treasure.PALE_PEARL: "la Perla Pálida",
    Treasure.OPAL_EYE: "el Ojo de Ópalo",
    Treasure.GREEN_GEM: "la Gema Verde",
    Treasure.BLUE_FLAME: "la Llama Azul",
    Treasure.PALANTIR: "el Palantir",
    Treasure.SILMARIL: "el Silmaril",
}


# ─── Tipos de habitación ───────────────────────────────────────────────────


class Glyph(StrEnum):
    """Glifo de un único carácter ASCII para cada tipo de habitación."""

    EMPTY = "."
    ENTRANCE = "E"
    STAIRS_UP = "<"
    STAIRS_DOWN = ">"
    POOL = "P"
    CHEST = "C"
    GOLD = "G"
    FLARES = "F"
    WARP = "W"
    SINKHOLE = "S"
    CRYSTAL_ORB = "O"
    BOOK = "B"
    MONSTER = "M"
    VENDOR = "V"
    TREASURE = "T"
    UNKNOWN = "?"


GLYPH_NAME: dict[Glyph, str] = {
    Glyph.EMPTY: "una habitación vacía",
    Glyph.ENTRANCE: "la entrada",
    Glyph.STAIRS_UP: "unas escaleras hacia arriba",
    Glyph.STAIRS_DOWN: "unas escaleras hacia abajo",
    Glyph.POOL: "un charco mágico",
    Glyph.CHEST: "un cofre",
    Glyph.GOLD: "monedas de oro",
    Glyph.FLARES: "bengalas",
    Glyph.WARP: "un warp",
    Glyph.SINKHOLE: "un sumidero",
    Glyph.CRYSTAL_ORB: "una bola de cristal",
    Glyph.BOOK: "un libro",
    Glyph.MONSTER: "un monstruo",
    Glyph.VENDOR: "un comerciante",
    Glyph.TREASURE: "un tesoro",
    Glyph.UNKNOWN: "una zona inexplorada",
}


# ─── Maldiciones ───────────────────────────────────────────────────────────


class Curse(Enum):
    """Las tres maldiciones latentes del castillo."""

    LETHARGY = auto()  # +1 turno extra; bloqueada por Rubí Rojo
    LEECH = auto()  # -1d5 oro/turno; bloqueada por Perla Pálida
    FORGETFULNESS = auto()  # re-oculta una sala aleatoria; bloqueada por Gema Verde


CURSE_WARD: dict[Curse, Treasure] = {
    Curse.LETHARGY: Treasure.RUBY_RED,
    Curse.LEECH: Treasure.PALE_PEARL,
    Curse.FORGETFULNESS: Treasure.GREEN_GEM,
}
