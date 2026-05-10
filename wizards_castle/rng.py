"""Seedable RNG wrapper.

The 1980 Apple II BASIC `RND` is famously biased: as documented on
MyAbandonware, the random pool is small enough that long runs reuse the
same monsters and treasures. This module wraps `random.Random` so the
whole game becomes deterministic when seeded — handy for tests and for
shareable runs — without inheriting the original bias.
"""

from __future__ import annotations

import random
from typing import Sequence, TypeVar

T = TypeVar("T")


class GameRNG:
    """Thin wrapper around `random.Random` exposing only what the game uses."""

    def __init__(self, seed: int | None = None) -> None:
        self._random = random.Random(seed)
        self.seed = seed

    # ---- Dice ---------------------------------------------------------
    def d(self, sides: int) -> int:
        """Roll a single n-sided die (returns 1..sides)."""
        if sides < 1:
            raise ValueError("sides must be >= 1")
        return self._random.randint(1, sides)

    def roll(self, n: int, sides: int) -> int:
        """Roll `n` dice with `sides` sides and return the sum."""
        return sum(self.d(sides) for _ in range(n))

    # ---- Convenience --------------------------------------------------
    def chance(self, numerator: int, denominator: int) -> bool:
        """True with probability numerator/denominator."""
        return self._random.randint(1, denominator) <= numerator

    def coin(self) -> bool:
        return self._random.random() < 0.5

    def choice(self, seq: Sequence[T]) -> T:
        return self._random.choice(seq)

    def randint(self, a: int, b: int) -> int:
        return self._random.randint(a, b)

    def shuffle(self, seq: list[T]) -> None:
        self._random.shuffle(seq)
