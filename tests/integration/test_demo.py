"""Tests del demo runner: end-to-end determinista."""

from __future__ import annotations

import pytest

from wizards_castle.application.demo_runner import run_demo
from wizards_castle.infrastructure.rng import StdLibRandom


@pytest.mark.slow
def test_demo_completes_with_seed_42() -> None:
    rng = StdLibRandom(42)
    state, log = run_demo(rng, seed=42)
    assert state.player.turn > 0
    # No verificamos victoria — la heurística es greedy y puede morir.
    # Sí verificamos que el log no está vacío y el state es coherente.
    assert log
    assert state.player.position is not None


def test_demo_is_deterministic_for_same_seed() -> None:
    s1, l1 = run_demo(StdLibRandom(7), seed=7)
    s2, l2 = run_demo(StdLibRandom(7), seed=7)
    assert s1.player.turn == s2.player.turn
    assert s1.player.gold == s2.player.gold
    assert len(l1) == len(l2)
