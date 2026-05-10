"""Static game data: races, monsters, treasures, room glyphs, vendor prices.

Numbers follow the 1980 Joseph R. Power listing reproduced at the IF Archive
and annotated by MaiZure ("Decoded: The Wizard's Castle"). Where versions
disagree we pick the value from the canonical Power BASIC source.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, IntEnum, auto


CASTLE_SIZE = 8  # 8x8 floor
CASTLE_LEVELS = 8  # 8 floors
START_GOLD = 60
LAMP_COST = 20
FLARE_COST = 1
TURNS_PER_CURSE_TICK = 1


class Race(str, Enum):
    HOBBIT = "Hobbit"
    ELF = "Elf"
    HUMAN = "Human"
    DWARF = "Dwarf"


class Sex(str, Enum):
    MALE = "Male"
    FEMALE = "Female"


@dataclass(frozen=True)
class RaceProfile:
    """Starting stats for a race.

    `bonus_points` are the extra attribute points the player allocates after
    rolling. Values come from the canonical BASIC listing (lines 9000-9030).
    """

    strength: int
    intelligence: int
    dexterity: int
    bonus_points: int


RACE_STATS: dict[Race, RaceProfile] = {
    Race.HOBBIT: RaceProfile(strength=5, intelligence=8, dexterity=8, bonus_points=4),
    Race.ELF:    RaceProfile(strength=7, intelligence=7, dexterity=7, bonus_points=8),
    Race.HUMAN:  RaceProfile(strength=8, intelligence=8, dexterity=8, bonus_points=8),
    Race.DWARF:  RaceProfile(strength=8, intelligence=6, dexterity=4, bonus_points=8),
}


class Armor(IntEnum):
    NONE = 0
    LEATHER = 1
    CHAINMAIL = 2
    PLATE = 3


ARMOR_NAME = {
    Armor.NONE: "no armor",
    Armor.LEATHER: "leather",
    Armor.CHAINMAIL: "chainmail",
    Armor.PLATE: "plate",
}
ARMOR_COST = {Armor.LEATHER: 10, Armor.CHAINMAIL: 20, Armor.PLATE: 30}
# Hit points each armour absorbs before being destroyed.
ARMOR_CAPACITY = {Armor.NONE: 0, Armor.LEATHER: 7, Armor.CHAINMAIL: 13, Armor.PLATE: 21}


class Weapon(IntEnum):
    NONE = 0
    DAGGER = 1
    MACE = 2
    SWORD = 3


WEAPON_NAME = {
    Weapon.NONE: "no weapon",
    Weapon.DAGGER: "a dagger",
    Weapon.MACE: "a mace",
    Weapon.SWORD: "a sword",
}
WEAPON_COST = {Weapon.DAGGER: 10, Weapon.MACE: 20, Weapon.SWORD: 30}
WEAPON_DAMAGE = {Weapon.NONE: 0, Weapon.DAGGER: 1, Weapon.MACE: 2, Weapon.SWORD: 3}


# ---------------------------------------------------------------------------
# Monsters
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class MonsterStats:
    name: str
    hit_points: int
    damage: int
    can_drain: bool = False  # Vampires drain Strength permanently.
    can_steal: bool = False  # Some monsters steal gold/treasure (not in original; here for extension).


# Order matters: index aligns with room codes 13..25 in the original.
MONSTERS: list[MonsterStats] = [
    MonsterStats("Kobold",    2, 1),
    MonsterStats("Orc",       3, 1),
    MonsterStats("Wolf",      3, 1),
    MonsterStats("Goblin",    4, 1),
    MonsterStats("Ogre",      5, 2),
    MonsterStats("Troll",     6, 2),
    MonsterStats("Bear",      7, 2),
    MonsterStats("Minotaur",  8, 3),
    MonsterStats("Giant",     9, 3),
    MonsterStats("Dragon",   10, 3),
    MonsterStats("Vampire",  11, 4, can_drain=True),
    MonsterStats("Balrog",   12, 4),
    MonsterStats("Werewolf", 13, 4),
]


# ---------------------------------------------------------------------------
# Treasures
# ---------------------------------------------------------------------------

class Treasure(IntEnum):
    RUBY_RED = 0
    NORN_STONE = 1
    PALE_PEARL = 2
    OPAL_EYE = 3
    GREEN_GEM = 4
    BLUE_FLAME = 5
    PALANTIR = 6
    SILMARIL = 7


TREASURE_NAME = {
    Treasure.RUBY_RED:   "the Ruby Red",
    Treasure.NORN_STONE: "the Norn Stone",
    Treasure.PALE_PEARL: "the Pale Pearl",
    Treasure.OPAL_EYE:   "the Opal Eye",
    Treasure.GREEN_GEM:  "the Green Gem",
    Treasure.BLUE_FLAME: "the Blue Flame",
    Treasure.PALANTIR:   "the Palantir",
    Treasure.SILMARIL:   "the Silmaril",
}

# Effects that owning a treasure grants the player while in inventory.
TREASURE_EFFECTS = {
    Treasure.RUBY_RED:   "wards off the curse of Lethargy",
    Treasure.PALE_PEARL: "wards off the curse of the Leech",
    Treasure.GREEN_GEM:  "wards off the curse of Forgetfulness",
    Treasure.OPAL_EYE:   "cures blindness",
    Treasure.BLUE_FLAME: "burns books that stick to your hands",
    Treasure.NORN_STONE: "useful but mysterious",
    Treasure.PALANTIR:   "useful but mysterious",
    Treasure.SILMARIL:   "useful but mysterious",
}


# ---------------------------------------------------------------------------
# Room types — single-character glyphs match the original printout
# ---------------------------------------------------------------------------

class Glyph(str, Enum):
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


GLYPH_DESCRIPTION = {
    Glyph.EMPTY:       "an empty room",
    Glyph.ENTRANCE:    "the entrance",
    Glyph.STAIRS_UP:   "stairs going up",
    Glyph.STAIRS_DOWN: "stairs going down",
    Glyph.POOL:        "a magic pool",
    Glyph.CHEST:       "a chest",
    Glyph.GOLD:        "gold pieces",
    Glyph.FLARES:      "flares",
    Glyph.WARP:        "a warp",
    Glyph.SINKHOLE:    "a sinkhole",
    Glyph.CRYSTAL_ORB: "a crystal orb",
    Glyph.BOOK:        "a book",
    Glyph.MONSTER:     "a monster",
    Glyph.VENDOR:      "a vendor",
    Glyph.TREASURE:    "a treasure",
    Glyph.UNKNOWN:     "an unmapped area",
}


# ---------------------------------------------------------------------------
# Curses
# ---------------------------------------------------------------------------

class Curse(Enum):
    LETHARGY = auto()        # +1 turn cost; warded by Ruby Red
    LEECH = auto()           # loses 1-5 gp per turn; warded by Pale Pearl
    FORGETFULNESS = auto()   # forgets visited rooms; warded by Green Gem


CURSE_TREASURE = {
    Curse.LETHARGY: Treasure.RUBY_RED,
    Curse.LEECH: Treasure.PALE_PEARL,
    Curse.FORGETFULNESS: Treasure.GREEN_GEM,
}


# ---------------------------------------------------------------------------
# Misc strings
# ---------------------------------------------------------------------------

INTRO_BANNER = r"""
   __        ___                  _ _      ____           _   _
   \ \      / (_)______ _ _ __ __| ( )___ / ___|__ _ ___| |_| | ___
    \ \ /\ / /| |_  / _` | '__/ _` |// __| |   / _` / __| __| |/ _ \
     \ V  V / | |/ / (_| | | | (_| | \__ \ |__| (_| \__ \ |_| |  __/
      \_/\_/  |_/___\__,_|_|  \__,_| |___/\____\__,_|___/\__|_|\___|

           A modern Python port of Joseph R. Power's 1980 classic.
"""

HELP_TEXT = """\
Commands:
  N S E W    Move north / south / east / west
  U D        Stairs up / down (only when standing on stairs)
  M          Show map of current level (uses a flare or lamp)
  F          Light a flare (reveals a 3x3 area)
  L <dir>    Shine the lamp in a direction (reveals adjacent rooms)
  G          Gaze into a crystal orb
  O          Open a book or chest in this room
  T          Drink from a magic pool
  R          Read your runestaff (teleports — needs runestaff)
  I          Inventory / status
  H or ?     This help
  S a v e    Save game to disk
  Q          Quit
"""
