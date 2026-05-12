"""Puerto del generador aleatorio.

El dominio recibe siempre un `RandomSource` por inyección. La implementación
concreta vive en `infrastructure/rng.py`. Esta separación habilita el modo
`--seed` y los tests deterministas (ver ADR 0003).
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol, TypeVar

T = TypeVar("T")


class RandomSource(Protocol):
    """Interfaz mínima del RNG usada por el dominio."""

    def randint(self, a: int, b: int, /) -> int:
        """Devuelve un entero en el rango cerrado `[a, b]`."""
        ...

    def choice(self, seq: Sequence[T], /) -> T:
        """Devuelve un elemento aleatorio de `seq` (no vacía)."""
        ...

    def shuffle(self, seq: list[T], /) -> None:
        """Mezcla `seq` in-place."""
        ...

    def random(self) -> float:
        """Devuelve un float en `[0.0, 1.0)`."""
        ...


def d(rng: RandomSource, sides: int) -> int:
    """Tira un dado de `sides` caras (1..sides)."""
    if sides < 1:
        msg = f"sides debe ser >= 1, recibido {sides}"
        raise ValueError(msg)
    return rng.randint(1, sides)


def roll(rng: RandomSource, n: int, sides: int) -> int:
    """Suma de `n` tiradas de un dado de `sides` caras."""
    return sum(d(rng, sides) for _ in range(n))


def chance(rng: RandomSource, numerator: int, denominator: int) -> bool:
    """True con probabilidad `numerator / denominator`."""
    return rng.randint(1, denominator) <= numerator
