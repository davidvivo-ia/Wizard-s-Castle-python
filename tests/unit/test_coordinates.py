from __future__ import annotations

import pytest

from wizards_castle.domain.catalog import CASTLE_HEIGHT, CASTLE_LEVELS, CASTLE_WIDTH
from wizards_castle.domain.coordinates import Coord, Direction
from wizards_castle.domain.errors import InvalidMoveError


class TestCoord:
    def test_construction_within_bounds(self) -> None:
        c = Coord(1, 1, 1)
        assert (c.x, c.y, c.z) == (1, 1, 1)

    @pytest.mark.parametrize(
        "bad",
        [(0, 1, 1), (CASTLE_WIDTH + 1, 1, 1), (1, 0, 1), (1, 1, 0), (1, 1, CASTLE_LEVELS + 1)],
    )
    def test_out_of_range_raises(self, bad: tuple[int, int, int]) -> None:
        with pytest.raises(InvalidMoveError):
            Coord(*bad)

    def test_step_north_wraps(self) -> None:
        assert Coord(1, 1, 1).step(Direction.NORTH) == Coord(1, CASTLE_HEIGHT, 1)

    def test_step_south_wraps(self) -> None:
        assert Coord(1, CASTLE_HEIGHT, 1).step(Direction.SOUTH) == Coord(1, 1, 1)

    def test_step_east_wraps(self) -> None:
        assert Coord(CASTLE_WIDTH, 1, 1).step(Direction.EAST) == Coord(1, 1, 1)

    def test_step_west_wraps(self) -> None:
        assert Coord(1, 1, 1).step(Direction.WEST) == Coord(CASTLE_WIDTH, 1, 1)

    def test_up_from_top_raises(self) -> None:
        with pytest.raises(InvalidMoveError):
            Coord(1, 1, 1).step(Direction.UP)

    def test_down_from_bottom_raises(self) -> None:
        with pytest.raises(InvalidMoveError):
            Coord(1, 1, CASTLE_LEVELS).step(Direction.DOWN)

    def test_step_z_normal(self) -> None:
        assert Coord(3, 3, 4).step(Direction.UP) == Coord(3, 3, 3)
        assert Coord(3, 3, 4).step(Direction.DOWN) == Coord(3, 3, 5)
