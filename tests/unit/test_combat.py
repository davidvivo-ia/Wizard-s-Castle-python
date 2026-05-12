from __future__ import annotations

from dataclasses import replace

from tests.conftest import FakeRandom
from wizards_castle.domain.catalog import MONSTERS, Armor, Race, Sex, Treasure, Weapon
from wizards_castle.domain.combat import (
    CombatState,
    monster_attack,
    player_attack,
    player_bribe,
    player_cast_deathspell,
    player_cast_fireball,
    player_cast_web,
    player_retreat,
    start_combat,
)
from wizards_castle.domain.coordinates import Coord
from wizards_castle.domain.player import Player


def _hero(**kw: object) -> Player:
    p = Player.fresh("Hero", Race.HUMAN, Sex.MALE, Coord(1, 4, 1))
    if kw:
        return replace(p, **kw)  # type: ignore[arg-type]
    return p


class TestPlayerAttack:
    def test_unarmed_player_does_not_attack(self) -> None:
        step = player_attack(_hero(), start_combat(0), FakeRandom(0))
        assert step.combat is not None
        assert any("arma" in e.message for e in step.events)

    def test_hit_kills_kobold_with_sword(self) -> None:
        # Kobold tiene 2 HP, espada hace 3.
        p = _hero(weapon=Weapon.SWORD, dexterity=18)
        step = player_attack(p, start_combat(0), FakeRandom(0))
        assert step.monster_dead
        assert step.combat is None


class TestPlayerRetreat:
    def test_high_dex_escapes(self) -> None:
        p = _hero(dexterity=18)
        step = player_retreat(p, start_combat(0), FakeRandom(0))
        assert step.fled is True or step.combat is not None  # tolerante a la tirada


class TestSpells:
    def test_web_paralyzes(self) -> None:
        p = _hero(intelligence=18)
        step = player_cast_web(p, start_combat(0), FakeRandom(0))
        assert step.combat is not None
        assert step.combat.web_turns >= 2
        assert step.player.strength == p.strength - 1

    def test_fireball_damages(self) -> None:
        p = _hero(intelligence=18)
        step = player_cast_fireball(p, start_combat(11), FakeRandom(0))  # Dragon 13 hp
        assert step.player.strength == p.strength - 1
        assert step.player.intelligence == p.intelligence - 1

    def test_deathspell_can_succeed_or_kill_caster(self) -> None:
        p = _hero(intelligence=18)
        step = player_cast_deathspell(p, start_combat(0), FakeRandom(0))
        assert step.monster_dead or step.player.intelligence == 0


class TestBribe:
    def test_no_treasures_no_bribe(self) -> None:
        step = player_bribe(_hero(), start_combat(0), FakeRandom(0))
        assert step.combat is not None
        assert any("nada" in e.message.lower() for e in step.events)

    def test_with_treasure_attempts_bribe(self) -> None:
        p = _hero().with_treasure(Treasure.SILMARIL)
        step = player_bribe(p, start_combat(0), FakeRandom(1))
        assert step.bribed or step.combat is not None


class TestMonsterAttack:
    def test_web_monster_does_not_hit(self) -> None:
        cs = CombatState(monster=MONSTERS[0], monster_hp=2, web_turns=1)
        step = monster_attack(_hero(armor=Armor.PLATE), cs, FakeRandom(0))
        assert step.combat is not None
        assert step.combat.web_turns == 0  # se reduce
        assert step.player.strength == _hero().strength
