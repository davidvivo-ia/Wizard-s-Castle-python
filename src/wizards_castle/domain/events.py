"""Eventos emitidos por el dominio.

Cada caso de uso devuelve `(estado', list[GameEvent])`. La presentación
traduce eventos a líneas de log/UI. Los eventos son inmutables y
serializables.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum

from wizards_castle.domain.catalog import Curse, Treasure
from wizards_castle.domain.coordinates import Coord


class Severity(StrEnum):
    """Categoría visual del evento."""

    INFO = "info"
    GOOD = "good"
    WARN = "warn"
    BAD = "bad"
    MAGIC = "magic"


@dataclass(frozen=True, slots=True)
class GameEvent:
    """Evento atómico emitido por el dominio."""

    message: str
    severity: Severity = Severity.INFO


@dataclass(frozen=True, slots=True)
class RoomEntered(GameEvent):
    """Marca-evento al entrar en una habitación nueva."""

    coord: Coord = field(default_factory=lambda: Coord(1, 4, 1))


@dataclass(frozen=True, slots=True)
class TreasureFound(GameEvent):
    """El jugador acaba de recoger un tesoro."""

    treasure: Treasure = field(default=Treasure.RUBY_RED)


@dataclass(frozen=True, slots=True)
class CurseAcquired(GameEvent):
    """El jugador acaba de adquirir una maldición."""

    curse: Curse = field(default=Curse.LETHARGY)


@dataclass(frozen=True, slots=True)
class CombatRound(GameEvent):
    """Resultado de una ronda de combate."""

    monster_hp: int = 0
    player_str: int = 0


@dataclass(frozen=True, slots=True)
class GameOver(GameEvent):
    """Fin de partida: muerte, escape sin orbe o victoria."""

    victory: bool = False
