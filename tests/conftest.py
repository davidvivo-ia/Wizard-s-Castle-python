"""Fixtures compartidas."""

from __future__ import annotations

import random
from collections.abc import Sequence
from typing import TypeVar

import pytest

T = TypeVar("T")


class FakeRandom:
    """RandomSource determinista basada en `random.Random(seed)`."""

    def __init__(self, seed: int = 0) -> None:
        self._r = random.Random(seed)

    def randint(self, a: int, b: int, /) -> int:
        return self._r.randint(a, b)

    def choice(self, seq: Sequence[T], /) -> T:
        return self._r.choice(seq)

    def shuffle(self, seq: list[T], /) -> None:
        self._r.shuffle(seq)

    def random(self) -> float:
        return self._r.random()


@pytest.fixture
def rng() -> FakeRandom:
    """RNG con seed 42 — útil cuando se quiere algo "estable pero no cero"."""
    return FakeRandom(42)


@pytest.fixture
def zero_rng() -> FakeRandom:
    """RNG con seed 0."""
    return FakeRandom(0)
