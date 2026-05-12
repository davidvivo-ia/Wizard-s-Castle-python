from __future__ import annotations

from wizards_castle.infrastructure.rng import LCGRandom, StdLibRandom


class TestStdLibRandom:
    def test_seeded_is_deterministic(self) -> None:
        a = StdLibRandom(42)
        b = StdLibRandom(42)
        assert [a.randint(1, 100) for _ in range(5)] == [b.randint(1, 100) for _ in range(5)]

    def test_choice_in_seq(self) -> None:
        a = StdLibRandom(0)
        items = [10, 20, 30]
        for _ in range(20):
            assert a.choice(items) in items

    def test_shuffle_in_place(self) -> None:
        a = StdLibRandom(0)
        items = list(range(10))
        a.shuffle(items)
        assert sorted(items) == list(range(10))

    def test_random_in_range(self) -> None:
        a = StdLibRandom(0)
        for _ in range(50):
            v = a.random()
            assert 0.0 <= v < 1.0


class TestLCGRandom:
    def test_seeded_is_deterministic(self) -> None:
        a = LCGRandom(42)
        b = LCGRandom(42)
        assert [a.randint(1, 100) for _ in range(5)] == [b.randint(1, 100) for _ in range(5)]

    def test_randint_bounds(self) -> None:
        a = LCGRandom(7)
        for _ in range(100):
            v = a.randint(1, 8)
            assert 1 <= v <= 8

    def test_choice_in_seq(self) -> None:
        a = LCGRandom(7)
        items = ["x", "y", "z"]
        for _ in range(20):
            assert a.choice(items) in items

    def test_shuffle_preserves_elements(self) -> None:
        a = LCGRandom(7)
        items = list(range(20))
        a.shuffle(items)
        assert sorted(items) == list(range(20))

    def test_random_in_range(self) -> None:
        a = LCGRandom(0)
        for _ in range(50):
            v = a.random()
            assert 0.0 <= v < 1.0
