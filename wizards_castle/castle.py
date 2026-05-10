"""Castle map generation.

Coordinates are 1-indexed `(x, y, z)` to match the original BASIC, where
`x` is east-west, `y` is north-south, and `z` is the level (1 = top).
Each level is a torus: walking off the edge wraps to the opposite side,
exactly as in the 1980 game.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterator

from .data import (
    CASTLE_LEVELS,
    CASTLE_SIZE,
    Glyph,
    MONSTERS,
    Treasure,
)
from .rng import GameRNG


@dataclass
class Room:
    """One room in the castle.

    `glyph` is what the player sees. `payload` is type-dependent:
    monster index, treasure index, gold/flare quantity, etc. `discovered`
    is set once the room has been entered or revealed (lamp/flare/orb).
    """

    glyph: Glyph = Glyph.EMPTY
    payload: int | None = None
    discovered: bool = False
    cleared: bool = False  # treasure picked up, monster killed, etc.

    def short(self) -> str:
        return self.glyph.value if self.discovered else "?"


Coord = tuple[int, int, int]


@dataclass
class Castle:
    """The full 8x8x8 dungeon."""

    grid: list[list[list[Room]]]
    entrance: Coord
    orb_of_zot_at: Coord  # warp room hiding the Orb of Zot
    runestaff_monster_at: Coord  # monster carrying the Runestaff

    # ---- Helpers ------------------------------------------------------
    def in_bounds(self, c: Coord) -> bool:
        x, y, z = c
        return 1 <= x <= CASTLE_SIZE and 1 <= y <= CASTLE_SIZE and 1 <= z <= CASTLE_LEVELS

    def at(self, c: Coord) -> Room:
        x, y, z = c
        return self.grid[z - 1][y - 1][x - 1]

    def all_coords(self) -> Iterator[Coord]:
        for z in range(1, CASTLE_LEVELS + 1):
            for y in range(1, CASTLE_SIZE + 1):
                for x in range(1, CASTLE_SIZE + 1):
                    yield (x, y, z)

    def level_coords(self, z: int) -> Iterator[Coord]:
        for y in range(1, CASTLE_SIZE + 1):
            for x in range(1, CASTLE_SIZE + 1):
                yield (x, y, z)


# ---------------------------------------------------------------------------
# Generation
# ---------------------------------------------------------------------------

def _empty_grid() -> list[list[list[Room]]]:
    return [
        [[Room() for _ in range(CASTLE_SIZE)] for _ in range(CASTLE_SIZE)]
        for _ in range(CASTLE_LEVELS)
    ]


def _level_distribution() -> list[tuple[Glyph, int]]:
    """How many of each special room every level should contain.

    Matches the original distribution: each level has exactly one of every
    type below; the rest is filled with empty rooms, monsters, then a few
    extras in unused space, and finally treasures are sprinkled.
    """

    return [
        (Glyph.STAIRS_DOWN, 1),
        (Glyph.POOL, 1),
        (Glyph.CHEST, 1),
        (Glyph.GOLD, 1),
        (Glyph.FLARES, 1),
        (Glyph.WARP, 1),
        (Glyph.SINKHOLE, 1),
        (Glyph.CRYSTAL_ORB, 1),
        (Glyph.BOOK, 1),
    ]


def generate_castle(rng: GameRNG) -> Castle:
    grid = _empty_grid()

    # Build a list of (x, y) slots per level, shuffled, used as a placement queue.
    def slots(z: int) -> list[tuple[int, int]]:
        cells = [(x, y) for y in range(1, CASTLE_SIZE + 1) for x in range(1, CASTLE_SIZE + 1)]
        rng.shuffle(cells)
        return cells

    # Place entrance on level 1, top row (y=1), random x — must be reachable
    # from outside in the original.
    entrance_x = rng.randint(1, CASTLE_SIZE)
    entrance: Coord = (entrance_x, 1, 1)

    # Pre-shuffle slots per level and ensure the entrance is consumed.
    level_slots: dict[int, list[tuple[int, int]]] = {z: slots(z) for z in range(1, CASTLE_LEVELS + 1)}
    level_slots[1].remove((entrance_x, 1))
    grid[0][0][entrance_x - 1] = Room(glyph=Glyph.ENTRANCE, discovered=True)

    # Place stairs up on every level except the top, mirroring the matching
    # stairs-down on the level above. This guarantees connectivity.
    stairs_up_at: dict[int, tuple[int, int]] = {}
    for z in range(1, CASTLE_LEVELS):
        # Pick a slot on level z for the stairs DOWN.
        sx, sy = level_slots[z].pop()
        grid[z - 1][sy - 1][sx - 1] = Room(glyph=Glyph.STAIRS_DOWN)
        # Mirror as stairs UP on level z+1, removing matching slot if free.
        if (sx, sy) in level_slots[z + 1]:
            level_slots[z + 1].remove((sx, sy))
        else:
            # If by chance that cell isn't free, just pick another.
            sx2, sy2 = level_slots[z + 1].pop()
            sx, sy = sx2, sy2
        grid[z][sy - 1][sx - 1] = Room(glyph=Glyph.STAIRS_UP)
        stairs_up_at[z + 1] = (sx, sy)

    # Place one of each level-local feature on every level.
    for z in range(1, CASTLE_LEVELS + 1):
        for glyph, count in _level_distribution():
            if glyph == Glyph.STAIRS_DOWN:
                # Already placed except top level wouldn't have it; but we
                # placed STAIRS_DOWN on z=1..7 above. Skip here.
                continue
            for _ in range(count):
                if not level_slots[z]:
                    break
                x, y = level_slots[z].pop()
                grid[z - 1][y - 1][x - 1] = Room(glyph=glyph)

    # Place a vendor on every level.
    for z in range(1, CASTLE_LEVELS + 1):
        if level_slots[z]:
            x, y = level_slots[z].pop()
            grid[z - 1][y - 1][x - 1] = Room(glyph=Glyph.VENDOR)

    # Sprinkle monsters: ~3 per level on shallow floors, more on deeper ones.
    monster_count_per_level = [3, 3, 4, 4, 5, 5, 6, 6]
    for z in range(1, CASTLE_LEVELS + 1):
        for _ in range(monster_count_per_level[z - 1]):
            if not level_slots[z]:
                break
            x, y = level_slots[z].pop()
            mon_idx = rng.randint(0, len(MONSTERS) - 1)
            grid[z - 1][y - 1][x - 1] = Room(glyph=Glyph.MONSTER, payload=mon_idx)

    # Place the 8 treasures somewhere in the castle (one per level fits well,
    # but the original allows multiple on the same level).
    treasures = list(Treasure)
    rng.shuffle(treasures)
    for t in treasures:
        # Pick a random level that still has a free slot.
        candidates = [z for z in range(1, CASTLE_LEVELS + 1) if level_slots[z]]
        if not candidates:
            break
        z = rng.choice(candidates)
        x, y = level_slots[z].pop()
        grid[z - 1][y - 1][x - 1] = Room(glyph=Glyph.TREASURE, payload=int(t))

    # Fill remaining slots with empty rooms (already empty, but mark explicitly
    # so we keep glyph EMPTY).
    for z in range(1, CASTLE_LEVELS + 1):
        for x, y in level_slots[z]:
            grid[z - 1][y - 1][x - 1] = Room(glyph=Glyph.EMPTY)

    castle = Castle(
        grid=grid,
        entrance=entrance,
        orb_of_zot_at=(0, 0, 0),  # placeholder; set below
        runestaff_monster_at=(0, 0, 0),
    )

    # Hide the Orb of Zot inside one of the warp rooms, level >= 2 to avoid
    # giving it away in the entry foyer.
    warps = [c for c in castle.all_coords() if castle.at(c).glyph == Glyph.WARP and c[2] >= 2]
    castle.orb_of_zot_at = rng.choice(warps) if warps else castle.entrance

    # Hide the Runestaff inside one of the monsters.
    monsters = [c for c in castle.all_coords() if castle.at(c).glyph == Glyph.MONSTER]
    castle.runestaff_monster_at = rng.choice(monsters) if monsters else castle.entrance

    return castle


# ---------------------------------------------------------------------------
# Movement helpers (toroidal)
# ---------------------------------------------------------------------------

def wrap(c: Coord) -> Coord:
    x, y, z = c
    x = ((x - 1) % CASTLE_SIZE) + 1
    y = ((y - 1) % CASTLE_SIZE) + 1
    z = max(1, min(CASTLE_LEVELS, z))
    return x, y, z


def step(c: Coord, direction: str) -> Coord:
    x, y, z = c
    d = direction.upper()
    if d == "N":
        y -= 1
    elif d == "S":
        y += 1
    elif d == "E":
        x += 1
    elif d == "W":
        x -= 1
    elif d == "U":
        z -= 1
    elif d == "D":
        z += 1
    else:
        raise ValueError(f"unknown direction {direction!r}")
    return wrap((x, y, z))
