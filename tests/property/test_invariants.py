"""Property-based tests con Hypothesis."""

from __future__ import annotations

from collections import Counter

from hypothesis import given, settings
from hypothesis import strategies as st

from tests.conftest import FakeRandom
from wizards_castle.domain.castle import generate_castle
from wizards_castle.domain.catalog import (
    CASTLE_HEIGHT,
    CASTLE_LEVELS,
    CASTLE_WIDTH,
    Glyph,
    Race,
    Sex,
    Treasure,
)
from wizards_castle.domain.coordinates import Coord
from wizards_castle.domain.player import Player


@given(seed=st.integers(min_value=0, max_value=10_000))
@settings(max_examples=30, deadline=None)
def test_castle_always_has_eight_treasures(seed: int) -> None:
    c = generate_castle(FakeRandom(seed))
    treasures = sorted(
        c.at(co).payload for co in c.all_coords() if c.at(co).glyph == Glyph.TREASURE
    )
    assert treasures == sorted(int(t) for t in Treasure)


@given(seed=st.integers(min_value=0, max_value=10_000))
@settings(max_examples=30, deadline=None)
def test_castle_total_room_count(seed: int) -> None:
    c = generate_castle(FakeRandom(seed))
    total = sum(1 for _ in c.all_coords())
    assert total == CASTLE_WIDTH * CASTLE_HEIGHT * CASTLE_LEVELS


@given(
    delta=st.integers(min_value=-100, max_value=100),
    seed=st.integers(min_value=0, max_value=1000),
)
@settings(max_examples=50, deadline=None)
def test_gold_never_negative(delta: int, seed: int) -> None:
    p = Player.fresh("X", Race.HUMAN, Sex.MALE, Coord(1, 4, 1))
    p2 = p.with_gold(delta)
    assert p2.gold >= 0


@given(seed=st.integers(min_value=0, max_value=10_000))
@settings(max_examples=20, deadline=None)
def test_castle_orb_in_warp(seed: int) -> None:
    c = generate_castle(FakeRandom(seed))
    assert c.at(c.orb_of_zot_at).glyph == Glyph.WARP


@given(seed=st.integers(min_value=0, max_value=10_000))
@settings(max_examples=20, deadline=None)
def test_glyph_distribution_includes_minimums(seed: int) -> None:
    """Cada nivel tiene al menos un pool, chest, orb, book, vendor."""
    c = generate_castle(FakeRandom(seed))
    for z in range(1, CASTLE_LEVELS + 1):
        glyphs = Counter(c.at(co).glyph for co in c.all_coords() if co.z == z)
        for g in (Glyph.POOL, Glyph.CHEST, Glyph.CRYSTAL_ORB, Glyph.BOOK, Glyph.VENDOR):
            assert glyphs[g] >= 1, f"Level {z} missing {g}"
