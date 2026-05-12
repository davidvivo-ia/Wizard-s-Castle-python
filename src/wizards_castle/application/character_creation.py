"""Caso de uso: creación del personaje + entrada al castillo."""

from __future__ import annotations

from dataclasses import dataclass

from wizards_castle.domain.castle import generate_castle
from wizards_castle.domain.catalog import (
    ARMOR_COST,
    FLARE_COST,
    LAMP_COST,
    RACE_STATS,
    START_GOLD,
    WEAPON_COST,
    Armor,
    Race,
    Sex,
    Weapon,
)
from wizards_castle.domain.player import Player
from wizards_castle.domain.random_source import RandomSource
from wizards_castle.domain.state import GameState


@dataclass(frozen=True, slots=True)
class CharacterChoices:
    """Decisiones del jugador en la pantalla de creación.

    Sin IO: el caller (TUI/CLI) recoge respuestas y construye este objeto
    antes de invocar `create_new_game`.
    """

    name: str
    race: Race
    sex: Sex
    bonus_strength: int = 0
    bonus_intelligence: int = 0
    bonus_dexterity: int = 0
    armor: Armor = Armor.NONE
    weapon: Weapon = Weapon.NONE
    buy_lamp: bool = False
    flares: int = 0


def create_new_game(
    choices: CharacterChoices,
    rng: RandomSource,
    *,
    seed: int | None = None,
    classic_mode: bool = False,
) -> GameState:
    """Construye un GameState fresco a partir de las decisiones del jugador.

    Valida que la suma de bonus no excede el cupo de la raza y que el oro
    inicial cubre las compras.
    """
    profile = RACE_STATS[choices.race]
    bonus_total = choices.bonus_strength + choices.bonus_intelligence + choices.bonus_dexterity
    if bonus_total > profile.bonus_points:
        msg = (
            f"bonus total {bonus_total} excede el cupo de {choices.race.value}: "
            f"{profile.bonus_points}"
        )
        raise ValueError(msg)
    if any(
        b < 0 for b in (choices.bonus_strength, choices.bonus_intelligence, choices.bonus_dexterity)
    ):
        msg = "los bonus no pueden ser negativos"
        raise ValueError(msg)

    castle = generate_castle(rng)
    player = Player.fresh(choices.name, choices.race, choices.sex, castle.entrance)
    player = player.with_stats(
        strength=choices.bonus_strength,
        intelligence=choices.bonus_intelligence,
        dexterity=choices.bonus_dexterity,
    )
    player = player.with_gold(START_GOLD)

    cost = (
        ARMOR_COST.get(choices.armor, 0)
        + WEAPON_COST.get(choices.weapon, 0)
        + (LAMP_COST if choices.buy_lamp else 0)
        + FLARE_COST * choices.flares
    )
    if cost > player.gold:
        msg = f"compras suman {cost} gp, sólo tienes {player.gold}"
        raise ValueError(msg)

    player = (
        player.with_gold(-cost)
        .with_armor(choices.armor)
        .with_weapon(choices.weapon)
        .with_lamp(choices.buy_lamp)
        .with_flares(choices.flares)
    )

    return GameState(player=player, castle=castle, seed=seed, classic_mode=classic_mode)
