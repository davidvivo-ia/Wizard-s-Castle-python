from pathlib import Path

from wizards_castle.castle import generate_castle
from wizards_castle.data import Race, Sex, Treasure, Weapon, Armor
from wizards_castle.player import Player
from wizards_castle.rng import GameRNG
from wizards_castle.save import load_from_path, save_to_path


def test_round_trip(tmp_path: Path):
    rng = GameRNG(2026)
    castle = generate_castle(rng)
    player = Player.from_race("Eli", Race.ELF, Sex.FEMALE)
    player.gold = 137
    player.weapon = Weapon.MACE
    player.armor = Armor.CHAINMAIL
    player.armor_damage = 3
    player.treasures.add(Treasure.PALANTIR)
    player.position = castle.entrance

    path = tmp_path / "save.json"
    save_to_path(path, player, castle, seed=2026)
    p2, c2, seed = load_from_path(path)

    assert seed == 2026
    assert p2.name == "Eli"
    assert p2.race == Race.ELF
    assert p2.gold == 137
    assert p2.weapon == Weapon.MACE
    assert p2.armor == Armor.CHAINMAIL
    assert p2.armor_damage == 3
    assert Treasure.PALANTIR in p2.treasures
    assert c2.entrance == castle.entrance
    # Spot-check a few rooms.
    for c in [castle.entrance,
              (1, 1, 1), (4, 4, 4), (8, 8, 8)]:
        assert c2.at(c).glyph == castle.at(c).glyph
