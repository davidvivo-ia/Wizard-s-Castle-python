"""Combat smoke tests using a scripted input function."""

from __future__ import annotations

from wizards_castle.combat import Combat
from wizards_castle.data import Armor, Race, Sex, Weapon
from wizards_castle.player import Player
from wizards_castle.rng import GameRNG


def scripted(answers: list[str]):
    it = iter(answers)
    return lambda _prompt: next(it)


def test_player_with_sword_can_kill_kobold_quickly():
    rng = GameRNG(0)
    p = Player.from_race("Slayer", Race.HUMAN, Sex.MALE)
    p.weapon = Weapon.SWORD
    p.armor = Armor.PLATE
    p.dexterity = 18
    # Always pick attack; never bribe / cast.
    answers = ["A"] * 50
    fight = Combat(p, rng, monster_index=0, monster_has_runestaff=False,
                   input_fn=scripted(answers))
    outcome = fight.run()
    assert outcome.monster_defeated
    assert p.is_alive


def test_runestaff_drops_when_marked_monster_dies():
    rng = GameRNG(1)
    p = Player.from_race("Hero", Race.HUMAN, Sex.MALE)
    p.weapon = Weapon.SWORD
    p.dexterity = 18
    answers = ["A"] * 50
    fight = Combat(p, rng, monster_index=0, monster_has_runestaff=True,
                   input_fn=scripted(answers))
    fight.run()
    assert p.has_runestaff


def test_retreat_succeeds_with_high_dex():
    rng = GameRNG(2)
    p = Player.from_race("Runner", Race.HOBBIT, Sex.MALE)
    p.weapon = Weapon.DAGGER
    p.dexterity = 18
    fight = Combat(p, rng, monster_index=12, monster_has_runestaff=False,
                   input_fn=scripted(["R"]))
    outcome = fight.run()
    assert outcome.fled or outcome.monster_defeated  # tolerant: sometimes catches
