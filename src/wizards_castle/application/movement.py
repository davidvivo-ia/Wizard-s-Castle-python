"""Casos de uso de movimiento: pasos cardinales, escaleras, teletransporte."""

from __future__ import annotations

from wizards_castle.domain.castle import Castle
from wizards_castle.domain.catalog import Glyph
from wizards_castle.domain.coordinates import Coord, Direction
from wizards_castle.domain.errors import InvalidMoveError, NoStairsError
from wizards_castle.domain.events import GameEvent, Severity
from wizards_castle.domain.state import GameState


def _reveal(state: GameState, position: Coord) -> GameState:
    castle = state.castle.with_room(position, state.castle.at(position).reveal())
    return state.with_castle(castle).with_player(state.player.at(position))


def step(state: GameState, direction: Direction) -> tuple[GameState, tuple[GameEvent, ...]]:
    """Mueve al jugador en una dirección cardinal con wrap toroidal."""
    if direction in (Direction.UP, Direction.DOWN):
        return use_stairs(state, going_up=direction == Direction.UP)
    new_pos = state.player.position.step(direction)
    return _reveal(state, new_pos), ()


def use_stairs(state: GameState, *, going_up: bool) -> tuple[GameState, tuple[GameEvent, ...]]:
    """Sube o baja por las escaleras de la habitación actual."""
    here: Castle = state.castle
    room = here.at(state.player.position)
    want = Glyph.STAIRS_UP if going_up else Glyph.STAIRS_DOWN
    if room.glyph != want:
        msg = f"no hay escaleras hacia {'arriba' if going_up else 'abajo'} aquí"
        raise NoStairsError(msg)
    direction = Direction.UP if going_up else Direction.DOWN
    new_pos = state.player.position.step(direction)
    verb = "Subes" if going_up else "Bajas"
    event = GameEvent(f"{verb} por las escaleras.", Severity.INFO)
    return _reveal(state, new_pos), (event,)


def teleport(state: GameState, target: Coord) -> tuple[GameState, tuple[GameEvent, ...]]:
    """Teletransporte controlado por el jugador con el Runestaff."""
    if not state.player.has_runestaff:
        msg = "necesitas el Runestaff para teletransportarte"
        raise InvalidMoveError(msg)
    return _reveal(state, target), (
        GameEvent("El Runestaff zumba y el mundo parpadea a tu alrededor.", Severity.MAGIC),
    )
