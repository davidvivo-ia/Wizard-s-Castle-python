"""Resolución de combate como funciones puras.

Cada acción del jugador o del monstruo devuelve un `CombatStep` con la nueva
versión del jugador, los HP del monstruo, y la lista de eventos generados.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from wizards_castle.domain.catalog import MONSTERS, MonsterStats, Treasure, Weapon
from wizards_castle.domain.events import GameEvent, Severity
from wizards_castle.domain.player import Player
from wizards_castle.domain.random_source import RandomSource, chance, d


class CombatAction(StrEnum):
    """Acciones disponibles para el jugador en combate."""

    ATTACK = "A"
    RETREAT = "R"
    CAST_WEB = "W"
    CAST_FIREBALL = "F"
    CAST_DEATHSPELL = "D"
    BRIBE = "B"


@dataclass(frozen=True, slots=True)
class CombatState:
    """Snapshot de un combate en curso."""

    monster: MonsterStats
    monster_hp: int
    web_turns: int = 0
    monster_carries_runestaff: bool = False


@dataclass(frozen=True, slots=True)
class CombatStep:
    """Resultado de un paso de combate (jugador + monstruo)."""

    player: Player
    combat: CombatState | None  # None significa que el combate ha terminado
    events: tuple[GameEvent, ...]
    fled: bool = False
    bribed: bool = False
    monster_dead: bool = False


def start_combat(monster_index: int, *, carries_runestaff: bool = False) -> CombatState:
    """Inicializa el estado de combate con un monstruo dado por su índice."""
    monster = MONSTERS[monster_index]
    return CombatState(
        monster=monster,
        monster_hp=monster.hit_points,
        monster_carries_runestaff=carries_runestaff,
    )


def player_attack(player: Player, combat: CombatState, rng: RandomSource) -> CombatStep:
    """Ataque del jugador. Acierta si DX >= d20."""
    if player.weapon == Weapon.NONE:
        return CombatStep(
            player=player,
            combat=combat,
            events=(GameEvent("¡No tienes arma con la que atacar!", Severity.WARN),),
        )
    if player.book_stuck:
        return CombatStep(
            player=player,
            combat=combat,
            events=(GameEvent("¡El libro pegado a tus manos te lo impide!", Severity.WARN),),
        )
    if d(rng, 20) > player.dexterity:
        return CombatStep(
            player=player,
            combat=combat,
            events=(GameEvent(f"Fallas el golpe contra el {combat.monster.name}.", Severity.WARN),),
        )
    new_hp = combat.monster_hp - player.weapon_damage
    events: list[GameEvent] = [
        GameEvent(
            f"Aciertas al {combat.monster.name} causando {player.weapon_damage} de daño.",
            Severity.GOOD,
        )
    ]
    new_player = player
    if combat.monster.can_break_weapon and chance(rng, 1, 8):
        events.append(GameEvent("¡Tu arma se hace pedazos contra su piel!", Severity.BAD))
        new_player = player.with_weapon(Weapon.NONE)
    if new_hp <= 0:
        events.append(GameEvent(f"El {combat.monster.name} cae muerto a tus pies.", Severity.GOOD))
        return CombatStep(player=new_player, combat=None, events=tuple(events), monster_dead=True)
    return CombatStep(
        player=new_player,
        combat=CombatState(
            monster=combat.monster,
            monster_hp=new_hp,
            web_turns=combat.web_turns,
            monster_carries_runestaff=combat.monster_carries_runestaff,
        ),
        events=tuple(events),
    )


def monster_attack(player: Player, combat: CombatState, rng: RandomSource) -> CombatStep:
    """Ataque del monstruo. Si está web, no actúa."""
    if combat.web_turns > 0:
        return CombatStep(
            player=player,
            combat=CombatState(
                monster=combat.monster,
                monster_hp=combat.monster_hp,
                web_turns=combat.web_turns - 1,
                monster_carries_runestaff=combat.monster_carries_runestaff,
            ),
            events=(
                GameEvent(
                    f"El {combat.monster.name} sigue atrapado en la telaraña.", Severity.INFO
                ),
            ),
        )
    if d(rng, 20) > player.dexterity:
        return CombatStep(
            player=player,
            combat=combat,
            events=(GameEvent(f"El {combat.monster.name} ataca y falla.", Severity.INFO),),
        )
    new_player, st_dmg = player.take_damage(combat.monster.damage)
    msg = (
        f"El {combat.monster.name} te golpea ({combat.monster.damage} dmg, "
        f"{st_dmg} traspasa la armadura)."
    )
    return CombatStep(player=new_player, combat=combat, events=(GameEvent(msg, Severity.BAD),))


def player_retreat(player: Player, combat: CombatState, rng: RandomSource) -> CombatStep:
    """Intento de retirada. Si DX <= d20, el monstruo te alcanza."""
    if d(rng, 20) <= player.dexterity:
        return CombatStep(
            player=player,
            combat=None,
            events=(GameEvent("¡Consigues escabullirte!", Severity.GOOD),),
            fled=True,
        )
    counter = monster_attack(player, combat, rng)
    return CombatStep(
        player=counter.player,
        combat=counter.combat if counter.combat else combat,
        events=(GameEvent("Intentas huir pero te alcanza.", Severity.WARN), *counter.events),
    )


def player_bribe(player: Player, combat: CombatState, rng: RandomSource) -> CombatStep:
    """Soborno con un tesoro aleatorio. 50/50 de aceptación."""
    if not player.treasures:
        return CombatStep(
            player=player,
            combat=combat,
            events=(GameEvent("¡No tienes nada que ofrecer!", Severity.WARN),),
        )
    offering: Treasure = rng.choice(sorted(player.treasures, key=int))
    if chance(rng, 1, 2):
        return CombatStep(
            player=player.without_treasure(offering),
            combat=None,
            events=(
                GameEvent(
                    f"El {combat.monster.name} acepta el soborno y se marcha.", Severity.GOOD
                ),
            ),
            bribed=True,
        )
    return CombatStep(
        player=player,
        combat=combat,
        events=(GameEvent(f"El {combat.monster.name} rechaza tu ofrecimiento.", Severity.BAD),),
    )


def player_cast_web(player: Player, combat: CombatState, rng: RandomSource) -> CombatStep:
    """Web: paraliza al monstruo 2-9 turnos. Cuesta 1 ST."""
    new_player = player.with_stats(strength=-1)
    web_for = d(rng, 8) + 1
    return CombatStep(
        player=new_player,
        combat=CombatState(
            monster=combat.monster,
            monster_hp=combat.monster_hp,
            web_turns=web_for,
            monster_carries_runestaff=combat.monster_carries_runestaff,
        ),
        events=(
            GameEvent(
                f"Una telaraña inmoviliza al {combat.monster.name} ({web_for} turnos).",
                Severity.MAGIC,
            ),
        ),
    )


def player_cast_fireball(player: Player, combat: CombatState, rng: RandomSource) -> CombatStep:
    """Fireball: 2d7 daño. Cuesta 1 ST + 1 IQ."""
    new_player = player.with_stats(strength=-1, intelligence=-1)
    dmg = d(rng, 7) + d(rng, 7)
    new_hp = combat.monster_hp - dmg
    events: list[GameEvent] = [GameEvent(f"¡Bola de fuego! {dmg} de daño.", Severity.MAGIC)]
    if new_hp <= 0:
        events.append(
            GameEvent(f"El {combat.monster.name} arde hasta convertirse en cenizas.", Severity.GOOD)
        )
        return CombatStep(player=new_player, combat=None, events=tuple(events), monster_dead=True)
    return CombatStep(
        player=new_player,
        combat=CombatState(
            monster=combat.monster,
            monster_hp=new_hp,
            web_turns=combat.web_turns,
            monster_carries_runestaff=combat.monster_carries_runestaff,
        ),
        events=tuple(events),
    )


def player_cast_deathspell(player: Player, combat: CombatState, rng: RandomSource) -> CombatStep:
    """Deathspell: o mata al monstruo, o te mata a ti."""
    if player.intelligence < d(rng, 4) + 15:
        new_player = player.with_stats(intelligence=-player.intelligence)
        return CombatStep(
            player=new_player,
            combat=combat,
            events=(GameEvent("¡El conjuro de muerte rebota — caes fulminado!", Severity.BAD),),
        )
    return CombatStep(
        player=player,
        combat=None,
        events=(
            GameEvent(
                f"¡El {combat.monster.name} se desploma envuelto en sombras!", Severity.MAGIC
            ),
        ),
        monster_dead=True,
    )
