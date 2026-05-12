"""Implementaciones concretas del puerto `RandomSource`.

- `StdLibRandom`: `random.Random` sembrable. Default moderno.
- `LCGRandom`: aproximación al `RND` Apple II BASIC (LCG corto, periodo bajo).
  Activado por `--classic`.
"""

from __future__ import annotations

import random
from collections.abc import Sequence
from typing import TypeVar

T = TypeVar("T")


class StdLibRandom:
    """Wrapper sobre `random.Random` que cumple `RandomSource`."""

    def __init__(self, seed: int | None = None) -> None:
        self._rand = random.Random(seed)

    def randint(self, a: int, b: int, /) -> int:
        return self._rand.randint(a, b)

    def choice(self, seq: Sequence[T], /) -> T:
        return self._rand.choice(seq)

    def shuffle(self, seq: list[T], /) -> None:
        self._rand.shuffle(seq)

    def random(self) -> float:
        return self._rand.random()


class LCGRandom:
    """Aproximación del RND Apple II BASIC.

    Generador congruencial lineal de 32 bits con multiplicador 1103515245 y
    incremento 12345 (la receta clásica de glibc). El periodo real del RND
    de Applesoft variaba según versión; este LCG no es bit-exact pero
    reproduce el "sabor" repetitivo: secuencias cortas, choices que se
    parecen entre sí.
    """

    _MULT = 1_103_515_245
    _INC = 12_345
    _MOD = 2**31

    def __init__(self, seed: int | None = None) -> None:
        self._state = (seed or 1) & (self._MOD - 1)

    def _next(self) -> int:
        self._state = (self._MULT * self._state + self._INC) % self._MOD
        return self._state

    def random(self) -> float:
        return self._next() / self._MOD

    def randint(self, a: int, b: int, /) -> int:
        if a > b:
            msg = f"a > b: {a} > {b}"
            raise ValueError(msg)
        span = b - a + 1
        return a + self._next() % span

    def choice(self, seq: Sequence[T], /) -> T:
        if not seq:
            msg = "no se puede elegir de una secuencia vacía"
            raise IndexError(msg)
        return seq[self._next() % len(seq)]

    def shuffle(self, seq: list[T], /) -> None:
        # Fisher-Yates con nuestro propio _next para mantener el sesgo del LCG.
        for i in range(len(seq) - 1, 0, -1):
            j = self._next() % (i + 1)
            seq[i], seq[j] = seq[j], seq[i]
