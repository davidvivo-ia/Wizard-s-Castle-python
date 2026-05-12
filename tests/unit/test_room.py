from __future__ import annotations

from wizards_castle.domain.catalog import Glyph
from wizards_castle.domain.room import Room


class TestRoom:
    def test_default_is_empty_undiscovered(self) -> None:
        r = Room()
        assert r.glyph == Glyph.EMPTY
        assert not r.discovered
        assert not r.cleared

    def test_reveal_sets_discovered(self) -> None:
        r = Room().reveal()
        assert r.discovered

    def test_clear_resets_glyph(self) -> None:
        r = Room(glyph=Glyph.MONSTER, payload=3).clear()
        assert r.glyph == Glyph.EMPTY
        assert r.payload is None
        assert r.cleared

    def test_short_glyph_hidden_unless_discovered(self) -> None:
        r = Room(glyph=Glyph.GOLD)
        assert r.to_short() == Glyph.UNKNOWN.value
        assert r.reveal().to_short() == Glyph.GOLD.value
