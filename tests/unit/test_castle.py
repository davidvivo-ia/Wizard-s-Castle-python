from __future__ import annotations

from collections import Counter

from tests.conftest import FakeRandom
from wizards_castle.domain.castle import generate_castle
from wizards_castle.domain.catalog import (
    CASTLE_HEIGHT,
    CASTLE_LEVELS,
    CASTLE_WIDTH,
    MONSTERS,
    Glyph,
    Treasure,
)


class TestDimensions:
    def test_three_dimensional_grid(self) -> None:
        c = generate_castle(FakeRandom(0))
        assert len(c.grid) == CASTLE_LEVELS
        for level in c.grid:
            assert len(level) == CASTLE_HEIGHT
            for row in level:
                assert len(row) == CASTLE_WIDTH


class TestUniqueRooms:
    def test_one_entrance(self) -> None:
        c = generate_castle(FakeRandom(7))
        glyphs = Counter(c.at(co).glyph for co in c.all_coords())
        assert glyphs[Glyph.ENTRANCE] == 1

    def test_eight_treasures(self) -> None:
        c = generate_castle(FakeRandom(7))
        treasures = sorted(
            c.at(co).payload for co in c.all_coords() if c.at(co).glyph == Glyph.TREASURE
        )
        assert treasures == sorted(int(t) for t in Treasure)

    def test_orb_inside_a_warp(self) -> None:
        c = generate_castle(FakeRandom(11))
        assert c.at(c.orb_of_zot_at).glyph == Glyph.WARP

    def test_runestaff_inside_a_monster(self) -> None:
        c = generate_castle(FakeRandom(13))
        room = c.at(c.runestaff_monster_at)
        assert room.glyph == Glyph.MONSTER
        assert room.payload is not None
        assert 0 <= room.payload < len(MONSTERS)


class TestEachLevelHas:
    def test_pool_chest_orb_book(self) -> None:
        c = generate_castle(FakeRandom(99))
        for z in range(1, CASTLE_LEVELS + 1):
            glyphs = {c.at(co).glyph for co in c.all_coords() if co.z == z}
            assert Glyph.POOL in glyphs
            assert Glyph.CHEST in glyphs
            assert Glyph.CRYSTAL_ORB in glyphs
            assert Glyph.BOOK in glyphs

    def test_vendor_per_level(self) -> None:
        c = generate_castle(FakeRandom(99))
        for z in range(1, CASTLE_LEVELS + 1):
            vendors = [co for co in c.all_coords() if co.z == z and c.at(co).glyph == Glyph.VENDOR]
            assert len(vendors) >= 1


class TestStairsConnectivity:
    def test_stairs_pairs_match(self) -> None:
        c = generate_castle(FakeRandom(123))
        for z in range(1, CASTLE_LEVELS):
            downs = [
                co for co in c.all_coords() if co.z == z and c.at(co).glyph == Glyph.STAIRS_DOWN
            ]
            ups_below = [
                co for co in c.all_coords() if co.z == z + 1 and c.at(co).glyph == Glyph.STAIRS_UP
            ]
            assert len(downs) >= 1
            assert len(ups_below) >= 1


class TestDeterminism:
    def test_same_seed_same_castle(self) -> None:
        a = generate_castle(FakeRandom(2026))
        b = generate_castle(FakeRandom(2026))
        ga = [a.at(co).glyph for co in a.all_coords()]
        gb = [b.at(co).glyph for co in b.all_coords()]
        assert ga == gb
        assert a.entrance == b.entrance
        assert a.orb_of_zot_at == b.orb_of_zot_at


class TestImmutability:
    def test_with_room_does_not_mutate_original(self) -> None:
        c = generate_castle(FakeRandom(0))
        original = c.at(c.entrance)
        modified = c.with_room(c.entrance, original.clear())
        assert c.at(c.entrance) == original
        assert modified.at(c.entrance).glyph == Glyph.EMPTY
