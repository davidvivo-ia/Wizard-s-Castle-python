"""Coordenadas y dirección de movimiento en el castillo toroidal."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from wizards_castle.domain.catalog import CASTLE_HEIGHT, CASTLE_LEVELS, CASTLE_WIDTH
from wizards_castle.domain.errors import InvalidMoveError


class Direction(StrEnum):
    """Direcciones cardinales más subir/bajar."""

    NORTH = "N"
    SOUTH = "S"
    EAST = "E"
    WEST = "W"
    UP = "U"
    DOWN = "D"


@dataclass(frozen=True, slots=True, order=True)
class Coord:
    """Coordenada 1-indexada `(x, y, z)` que casa con `FND` del original.

    El castillo es un toro 8x8 en cada nivel: salir por un borde te lleva al
    opuesto. Subir/bajar respeta los límites verticales (1..8).
    """

    x: int
    y: int
    z: int

    def __post_init__(self) -> None:
        if not (1 <= self.x <= CASTLE_WIDTH):
            msg = f"x fuera de rango: {self.x}"
            raise InvalidMoveError(msg)
        if not (1 <= self.y <= CASTLE_HEIGHT):
            msg = f"y fuera de rango: {self.y}"
            raise InvalidMoveError(msg)
        if not (1 <= self.z <= CASTLE_LEVELS):
            msg = f"z fuera de rango: {self.z}"
            raise InvalidMoveError(msg)

    def step(self, direction: Direction) -> Coord:
        """Devuelve la coordenada vecina aplicando wrap toroidal en X/Y."""
        x, y, z = self.x, self.y, self.z
        match direction:
            case Direction.NORTH:
                y = _wrap(y - 1, CASTLE_HEIGHT)
            case Direction.SOUTH:
                y = _wrap(y + 1, CASTLE_HEIGHT)
            case Direction.EAST:
                x = _wrap(x + 1, CASTLE_WIDTH)
            case Direction.WEST:
                x = _wrap(x - 1, CASTLE_WIDTH)
            case Direction.UP:
                if z <= 1:
                    msg = "no puedes subir desde el primer nivel"
                    raise InvalidMoveError(msg)
                z -= 1
            case Direction.DOWN:
                if z >= CASTLE_LEVELS:
                    msg = "no puedes bajar desde el último nivel"
                    raise InvalidMoveError(msg)
                z += 1
        return Coord(x, y, z)


def _wrap(value: int, modulus: int) -> int:
    """Wrap 1-indexed: 0 → modulus, modulus+1 → 1."""
    return ((value - 1) % modulus) + 1
