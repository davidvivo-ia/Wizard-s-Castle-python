from __future__ import annotations

from pathlib import Path

from wizards_castle.infrastructure.paths import data_dir, save_path


class TestPaths:
    def test_data_dir_creates_directory(self) -> None:
        p = data_dir()
        assert isinstance(p, Path)
        assert p.exists()

    def test_save_path_sanitises_slot_name(self) -> None:
        p = save_path("../../etc/passwd")
        assert "passwd" in p.name
        assert ".." not in p.parts[-1]

    def test_save_path_default_slot(self) -> None:
        p = save_path()
        assert p.name == "slot-auto.json"
