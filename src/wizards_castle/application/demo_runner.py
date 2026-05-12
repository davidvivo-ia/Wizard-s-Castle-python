"""Demo runner determinista.

Genera un castillo con seed fijo, crea un personaje "óptimo" sin elección
humana, y ejecuta una secuencia de comandos pre-decidida hasta morir o ganar.
Sirve como prueba de humo end-to-end y para grabar GIFs.
"""

from __future__ import annotations

from collections import deque
from collections.abc import Iterator

from wizards_castle.application.character_creation import (
    CharacterChoices,
    create_new_game,
)
from wizards_castle.application.movement import step, use_stairs
from wizards_castle.application.room_events import (
    pick_up_treasure,
    resolve_passive_room,
    tick_curses,
)
from wizards_castle.domain.catalog import (
    CASTLE_HEIGHT,
    CASTLE_LEVELS,
    CASTLE_WIDTH,
    Armor,
    Glyph,
    Race,
    Sex,
    Weapon,
)
from wizards_castle.domain.coordinates import Coord, Direction
from wizards_castle.domain.events import GameEvent
from wizards_castle.domain.random_source import RandomSource
from wizards_castle.domain.state import GameState

MAX_TURNS = 1500


def run_demo(rng: RandomSource, *, seed: int | None = None) -> tuple[GameState, list[GameEvent]]:
    """Ejecuta una partida demo completa. Devuelve estado final + log de eventos."""
    choices = CharacterChoices(
        name="Demo",
        race=Race.HUMAN,
        sex=Sex.MALE,
        bonus_strength=2,
        bonus_intelligence=2,
        bonus_dexterity=4,
        armor=Armor.LEATHER,
        weapon=Weapon.MACE,
        flares=10,
    )
    state = create_new_game(choices, rng, seed=seed)
    log: list[GameEvent] = []
    state, evts = resolve_passive_room(state, rng)
    log.extend(evts)
    state, evts = pick_up_treasure(state, rng)
    log.extend(evts)

    # Estrategia simple: BFS al objetivo más prioritario en orden.
    for _ in range(MAX_TURNS):
        if state.is_finished:
            break
        target = _next_target(state)
        if target is None:
            break
        path = _bfs_path(state, target)
        if not path:
            break
        for direction in path:
            state, evts = _execute_step(state, direction, rng)
            log.extend(evts)
            if state.is_finished:
                break
    return state, log


def _execute_step(
    state: GameState, direction: Direction, rng: RandomSource
) -> tuple[GameState, tuple[GameEvent, ...]]:
    if direction in (Direction.UP, Direction.DOWN):
        state, evts1 = use_stairs(state, going_up=direction == Direction.UP)
    else:
        state, evts1 = step(state, direction)
    state, evts2 = resolve_passive_room(state, rng)
    state, evts3 = pick_up_treasure(state, rng)
    state, evts4 = tick_curses(state, rng)
    return state, (*evts1, *evts2, *evts3, *evts4)


def _next_target(state: GameState) -> Coord | None:
    """Decide adónde ir: orbe → entrada (si tienes orbe) → tesoro más próximo → escaleras."""
    if state.player.has_orb_of_zot:
        return state.castle.entrance
    pos = state.player.position
    castle = state.castle

    # 1. Tesoros descubiertos en este nivel.
    for c in castle.all_coords():
        if c.z == pos.z and castle.at(c).glyph == Glyph.TREASURE:
            return c

    # 2. Escaleras hacia abajo en este nivel (vamos profundizando).
    for c in castle.all_coords():
        if c.z == pos.z and castle.at(c).glyph == Glyph.STAIRS_DOWN:
            return c

    # 3. Orbe de Zot (lo conocemos por el state).
    return castle.orb_of_zot_at


def _bfs_path(state: GameState, target: Coord) -> list[Direction]:
    """BFS toroidal al `target` con vecinos N/S/E/W (sin atravesar paredes; aquí no hay)."""
    start = state.player.position
    if start == target:
        # Si target requiere cambiar nivel, devolvemos UP/DOWN.
        return _stairs_dir(state, target)

    if start.z != target.z:
        # Hay que ir a unas escaleras del nivel actual primero.
        # Buscar escaleras hacia el lado correcto.
        glyph_target = Glyph.STAIRS_DOWN if target.z > start.z else Glyph.STAIRS_UP
        for c in state.castle.all_coords():
            if c.z == start.z and state.castle.at(c).glyph == glyph_target:
                target = c
                break

    visited: set[Coord] = {start}
    queue: deque[tuple[Coord, list[Direction]]] = deque([(start, [])])
    while queue:
        cur, path = queue.popleft()
        if cur == target:
            return path
        for direction in (Direction.NORTH, Direction.SOUTH, Direction.EAST, Direction.WEST):
            nxt = cur.step(direction)
            if nxt in visited:
                continue
            visited.add(nxt)
            queue.append((nxt, [*path, direction]))
            # Heurística: al alcanzar un vecino-objetivo paramos antes.
            if nxt == target:
                return [*path, direction]
    return []


def _stairs_dir(state: GameState, target: Coord) -> list[Direction]:
    """Si estamos sobre unas escaleras y el target está en otro nivel, devuelve UP/DOWN."""
    here = state.castle.at(state.player.position)
    if target.z < state.player.position.z and here.glyph == Glyph.STAIRS_UP:
        return [Direction.UP]
    if target.z > state.player.position.z and here.glyph == Glyph.STAIRS_DOWN:
        return [Direction.DOWN]
    return []


def iter_events(rng: RandomSource, *, seed: int | None = None) -> Iterator[GameEvent]:
    """Generador perezoso de eventos (útil para grabar GIFs en streaming)."""
    state, log = run_demo(rng, seed=seed)
    yield from log
    _ = state  # se descarta; quien itere puede lanzar de nuevo si quiere el final


# Sanity helpers para tests
def _grid_dimensions() -> tuple[int, int, int]:
    return CASTLE_WIDTH, CASTLE_HEIGHT, CASTLE_LEVELS
