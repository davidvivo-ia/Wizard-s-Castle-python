"""Map-generation invariants."""

from __future__ import annotations

from collections import Counter

from wizards_castle.castle import generate_castle, step, wrap
from wizards_castle.data import (
    CASTLE_LEVELS,
    CASTLE_SIZE,
    Glyph,
    MONSTERS,
    Treasure,
)
from wizards_castle.rng import GameRNG


def _glyph_counts(castle):
    return Counter(castle.at(c).glyph for c in castle.all_coords())


def test_castle_dimensions():
    castle = generate_castle(GameRNG(42))
    assert len(castle.grid) == CASTLE_LEVELS
    for level in castle.grid:
        assert len(level) == CASTLE_SIZE
        for row in level:
            assert len(row) == CASTLE_SIZE


def test_entrance_unique_and_on_top():
    castle = generate_castle(GameRNG(7))
    counts = _glyph_counts(castle)
    assert counts[Glyph.ENTRANCE] == 1
    assert castle.entrance[2] == 1


def test_eight_treasures_in_castle():
    castle = generate_castle(GameRNG(7))
    treasures = [castle.at(c).payload for c in castle.all_coords()
                 if castle.at(c).glyph == Glyph.TREASURE]
    assert sorted(treasures) == sorted(int(t) for t in Treasure)


def test_runestaff_hidden_in_a_monster():
    castle = generate_castle(GameRNG(11))
    room = castle.at(castle.runestaff_monster_at)
    assert room.glyph == Glyph.MONSTER
    assert 0 <= int(room.payload) < len(MONSTERS)


def test_orb_of_zot_in_warp_room():
    castle = generate_castle(GameRNG(13))
    assert castle.at(castle.orb_of_zot_at).glyph == Glyph.WARP


def test_seed_is_deterministic():
    a = generate_castle(GameRNG(2026))
    b = generate_castle(GameRNG(2026))
    glyphs_a = [a.at(c).glyph for c in a.all_coords()]
    glyphs_b = [b.at(c).glyph for c in b.all_coords()]
    assert glyphs_a == glyphs_b


def test_movement_wraps_torus():
    assert step((1, 1, 1), "W") == (CASTLE_SIZE, 1, 1)
    assert step((CASTLE_SIZE, CASTLE_SIZE, 1), "S") == (CASTLE_SIZE, 1, 1)
    assert wrap((0, 0, 1)) == (CASTLE_SIZE, CASTLE_SIZE, 1)


def test_every_level_has_at_least_one_monster_and_vendor():
    castle = generate_castle(GameRNG(99))
    for z in range(1, CASTLE_LEVELS + 1):
        glyphs = [castle.at(c).glyph for c in castle.level_coords(z)]
        assert Glyph.MONSTER in glyphs
        assert Glyph.VENDOR in glyphs


def test_stairs_match_between_levels():
    castle = generate_castle(GameRNG(123))
    for z in range(1, CASTLE_LEVELS):
        downs = [c for c in castle.level_coords(z)
                 if castle.at(c).glyph == Glyph.STAIRS_DOWN]
        ups_below = [c for c in castle.level_coords(z + 1)
                     if castle.at(c).glyph == Glyph.STAIRS_UP]
        assert len(downs) >= 1
        assert len(ups_below) >= 1
