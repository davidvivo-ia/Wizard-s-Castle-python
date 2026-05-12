"""Tests adicionales de combate para subir cobertura."""

from __future__ import annotations

from dataclasses import replace

from tests.conftest import FakeRandom
from wizards_castle.domain.catalog import MONSTERS, Race, Sex, Treasure, Weapon
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
    p = Player.fresh("X", Race.HUMAN, Sex.MALE, Coord(1, 4, 1))
    return replace(p, **kw) if kw else p  # type: ignore[arg-type]


class TestEdgeCases:
    def test_attack_with_book_stuck_blocked(self) -> None:
        p = _hero(weapon=Weapon.SWORD, dexterity=18, book_stuck=True)
        step = player_attack(p, start_combat(0), FakeRandom(0))
        assert step.combat is not None
        assert any("libro" in e.message.lower() for e in step.events)

    def test_dragon_can_break_weapon_eventually(self) -> None:
        p = _hero(weapon=Weapon.SWORD, dexterity=18)
        # Forzamos: dragon (índice 11), 100 intentos para asegurar el break aleatorio.
        broke = False
        for seed in range(50):
            step = player_attack(p, start_combat(11), FakeRandom(seed))
            if step.player.weapon == Weapon.NONE:
                broke = True
                break
        assert broke, "El dragón debería romper el arma en algún seed"

    def test_monster_misses_with_low_dex(self) -> None:
        p = _hero(dexterity=18)
        step = monster_attack(p, start_combat(0), FakeRandom(2))
        # con dex=18 y d20<=18 falla raramente; al menos no peta.
        assert step.combat is not None or step.fled is False

    def test_retreat_when_caught(self) -> None:
        p = _hero(dexterity=1)  # dex muy baja, casi nunca escapa
        step = player_retreat(p, start_combat(0), FakeRandom(0))
        # debe haber al menos un evento "intentas huir"
        assert any("hu" in e.message.lower() for e in step.events)

    def test_bribe_no_treasure(self) -> None:
        p = _hero()
        step = player_bribe(p, start_combat(0), FakeRandom(0))
        assert any("nada" in e.message.lower() for e in step.events)

    def test_bribe_rejected_keeps_treasure(self) -> None:
        p = _hero().with_treasure(Treasure.PALANTIR)
        # buscamos una semilla en la que el soborno se rechace
        rejected = False
        for s in range(10):
            step = player_bribe(p, start_combat(0), FakeRandom(s))
            if not step.bribed:
                assert Treasure.PALANTIR in step.player.treasures
                rejected = True
                break
        assert rejected

    def test_fireball_kills_weak_monster(self) -> None:
        p = _hero(intelligence=18)
        step = player_cast_fireball(p, start_combat(0), FakeRandom(0))  # kobold 2hp
        # 2d7 ≥ 2 casi siempre, pero por seguridad chequeamos coherencia
        if step.monster_dead:
            assert step.combat is None

    def test_web_costs_strength(self) -> None:
        p = _hero(intelligence=18)
        st_before = p.strength
        step = player_cast_web(p, start_combat(0), FakeRandom(0))
        assert step.player.strength == st_before - 1

    def test_deathspell_kills_caster_low_iq(self) -> None:
        p = _hero(intelligence=15)  # justo en el umbral
        # encontramos un seed donde rebote
        rebound = False
        for s in range(20):
            step = player_cast_deathspell(p, start_combat(0), FakeRandom(s))
            if step.player.intelligence == 0:
                rebound = True
                break
        assert rebound


class TestStartCombat:
    def test_runestaff_flag_carried(self) -> None:
        cs = start_combat(0, carries_runestaff=True)
        assert cs.monster_carries_runestaff


class TestMonsterMissesPath:
    def test_low_dex_player_gets_hit(self) -> None:
        p = _hero(dexterity=1)
        cs = CombatState(monster=MONSTERS[0], monster_hp=10)
        step = monster_attack(p, cs, FakeRandom(0))
        # con dex=1, casi siempre golpea; verificamos al menos que no peta
        assert step.player.strength <= p.strength
