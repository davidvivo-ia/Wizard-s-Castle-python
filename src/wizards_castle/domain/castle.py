"""Castle: mapa inmutable 8x8x8 + generador determinista."""

from __future__ import annotations

from dataclasses import dataclass, replace

from wizards_castle.domain.catalog import (
    CASTLE_HEIGHT,
    CASTLE_LEVELS,
    CASTLE_WIDTH,
    MONSTERS,
    Glyph,
    Treasure,
)
from wizards_castle.domain.coordinates import Coord
from wizards_castle.domain.random_source import RandomSource
from wizards_castle.domain.room import Room


@dataclass(frozen=True, slots=True)
class Castle:
    """Mapa del castillo. Almacenado como tupla 3D anidada (z, y, x), 1-indexada externamente."""

    grid: tuple[tuple[tuple[Room, ...], ...], ...]
    entrance: Coord
    orb_of_zot_at: Coord
    runestaff_monster_at: Coord

    def at(self, c: Coord) -> Room:
        """Devuelve la habitación en `c`. La grid es 0-indexada por dentro."""
        return self.grid[c.z - 1][c.y - 1][c.x - 1]

    def with_room(self, c: Coord, room: Room) -> Castle:
        """Devuelve un Castle nuevo con `room` colocada en `c` (resto compartido)."""
        new_grid: list[tuple[tuple[Room, ...], ...]] = []
        for z, level in enumerate(self.grid, start=1):
            if z != c.z:
                new_grid.append(level)
                continue
            new_level: list[tuple[Room, ...]] = []
            for y, row in enumerate(level, start=1):
                if y != c.y:
                    new_level.append(row)
                    continue
                new_row = tuple(room if (x == c.x) else cell for x, cell in enumerate(row, start=1))
                new_level.append(new_row)
            new_grid.append(tuple(new_level))
        return replace(self, grid=tuple(new_grid))

    def all_coords(self) -> tuple[Coord, ...]:
        """Itera todas las coordenadas en orden (z, y, x)."""
        return tuple(
            Coord(x, y, z)
            for z in range(1, CASTLE_LEVELS + 1)
            for y in range(1, CASTLE_HEIGHT + 1)
            for x in range(1, CASTLE_WIDTH + 1)
        )


# ─── Generación ────────────────────────────────────────────────────────────


def _level_features() -> tuple[Glyph, ...]:
    """Una de cada característica por nivel (excepto stairs, que se enlazan aparte).

    [DATO] Líneas 1295-1345 del original colocan 1 de cada item por nivel y 3
    vendors. Aquí simplificamos a 1 vendor (más jugable, menos repetitivo);
    [LICENCIA CREATIVA] documentada en CHANGELOG.
    """
    return (
        Glyph.POOL,
        Glyph.CHEST,
        Glyph.GOLD,
        Glyph.FLARES,
        Glyph.WARP,
        Glyph.SINKHOLE,
        Glyph.CRYSTAL_ORB,
        Glyph.BOOK,
        Glyph.VENDOR,
    )


def _monsters_per_level() -> tuple[int, ...]:
    """Cuántos monstruos por nivel.

    El original coloca 12 (uno de cada tipo) por nivel. Mantenemos esa cantidad
    pero el tipo concreto se escoge aleatoriamente (no 1-de-cada-tipo) para
    aumentar variedad al jugar varias veces.
    """
    return (12,) * CASTLE_LEVELS


def generate_castle(rng: RandomSource) -> Castle:
    """Genera un castillo nuevo con `rng`. Determinista para un seed dado."""
    grid: list[list[list[Room]]] = [
        [[Room() for _ in range(CASTLE_WIDTH)] for _ in range(CASTLE_HEIGHT)]
        for _ in range(CASTLE_LEVELS)
    ]

    free_slots: dict[int, list[tuple[int, int]]] = {}
    for z in range(1, CASTLE_LEVELS + 1):
        cells = [(x, y) for y in range(1, CASTLE_HEIGHT + 1) for x in range(1, CASTLE_WIDTH + 1)]
        rng.shuffle(cells)
        free_slots[z] = cells

    # Entrada en (1, 4, 1) — [DATO] línea 1255 (FND(1) con X=1, Y=4 → 4).
    entrance = Coord(1, 4, 1)
    free_slots[1].remove((entrance.x, entrance.y))
    grid[0][entrance.y - 1][entrance.x - 1] = Room(glyph=Glyph.ENTRANCE, discovered=True)

    # Escaleras: una pareja down/up por cada par de niveles consecutivos.
    for z in range(1, CASTLE_LEVELS):
        sx, sy = free_slots[z].pop()
        grid[z - 1][sy - 1][sx - 1] = Room(glyph=Glyph.STAIRS_DOWN)
        if (sx, sy) in free_slots[z + 1]:
            free_slots[z + 1].remove((sx, sy))
            ux, uy = sx, sy
        else:  # pragma: no cover — extremadamente improbable con shuffle previo
            ux, uy = free_slots[z + 1].pop()
        grid[z][uy - 1][ux - 1] = Room(glyph=Glyph.STAIRS_UP)

    # Características de nivel.
    for z in range(1, CASTLE_LEVELS + 1):
        for glyph in _level_features():
            if not free_slots[z]:
                break
            x, y = free_slots[z].pop()
            grid[z - 1][y - 1][x - 1] = Room(glyph=glyph)

    # Monstruos.
    for z, count in enumerate(_monsters_per_level(), start=1):
        for _ in range(count):
            if not free_slots[z]:
                break
            x, y = free_slots[z].pop()
            mon_idx = rng.randint(0, len(MONSTERS) - 1)
            grid[z - 1][y - 1][x - 1] = Room(glyph=Glyph.MONSTER, payload=mon_idx)

    # Tesoros: uno de cada, esparcidos por niveles aleatorios.
    treasures = list(Treasure)
    rng.shuffle(treasures)
    for t in treasures:
        candidates = [z for z in range(1, CASTLE_LEVELS + 1) if free_slots[z]]
        if not candidates:
            break  # pragma: no cover
        z = rng.choice(candidates)
        x, y = free_slots[z].pop()
        grid[z - 1][y - 1][x - 1] = Room(glyph=Glyph.TREASURE, payload=int(t))

    # Sellar grid en tuplas inmutables.
    sealed = tuple(tuple(tuple(row) for row in level) for level in grid)
    castle = Castle(
        grid=sealed,
        entrance=entrance,
        orb_of_zot_at=entrance,  # placeholder, fijado abajo
        runestaff_monster_at=entrance,
    )

    warps = [c for c in castle.all_coords() if castle.at(c).glyph == Glyph.WARP and c.z >= 2]
    monsters = [c for c in castle.all_coords() if castle.at(c).glyph == Glyph.MONSTER]
    return replace(
        castle,
        orb_of_zot_at=rng.choice(warps) if warps else entrance,
        runestaff_monster_at=rng.choice(monsters) if monsters else entrance,
    )
