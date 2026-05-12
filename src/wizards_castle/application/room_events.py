"""Resolución de eventos de habitación: oro, bengalas, sumideros, warps, etc.

Cada función devuelve `(GameState', tuple[GameEvent, ...])`. Si el evento
inicia un combate o requiere decisión del jugador, devolvemos un evento
informativo y la presentación se encarga de invocar el caso de uso siguiente.
"""

from __future__ import annotations

from dataclasses import replace

from wizards_castle.domain.castle import Castle
from wizards_castle.domain.catalog import (
    CASTLE_LEVELS,
    CURSE_WARD,
    GLYPH_NAME,
    TREASURE_NAME,
    Curse,
    Glyph,
    Race,
    Sex,
    Treasure,
)
from wizards_castle.domain.coordinates import Coord
from wizards_castle.domain.events import (
    CurseAcquired,
    GameEvent,
    Severity,
    TreasureFound,
)
from wizards_castle.domain.player import Player
from wizards_castle.domain.random_source import RandomSource, chance, d
from wizards_castle.domain.room import Room
from wizards_castle.domain.state import GameState


def resolve_passive_room(
    state: GameState, rng: RandomSource
) -> tuple[GameState, tuple[GameEvent, ...]]:
    """Resuelve eventos automáticos al entrar (oro, bengalas, sumidero, warp).

    Para eventos interactivos (charco, cofre, libro, orbe, vendedor, monstruo)
    devolvemos un mensaje "aquí encuentras X" y la capa de presentación invoca
    luego el caso de uso correspondiente cuando el jugador decida.
    """
    room = state.castle.at(state.player.position)
    if room.cleared:
        return state, ()

    if room.glyph == Glyph.GOLD:
        return _pickup_gold(state, room, rng)
    if room.glyph == Glyph.FLARES:
        return _pickup_flares(state, room, rng)
    if room.glyph == Glyph.SINKHOLE:
        return _resolve_sinkhole(state)
    if room.glyph == Glyph.WARP:
        return _resolve_warp(state, rng)
    return state, (
        GameEvent(f"Aquí encuentras {GLYPH_NAME.get(room.glyph, 'algo')}.", Severity.INFO),
    )


def _pickup_gold(
    state: GameState, room: Room, rng: RandomSource
) -> tuple[GameState, tuple[GameEvent, ...]]:
    amount = d(rng, 10) + d(rng, 10)
    return _consume(state, state.player.with_gold(amount), room), (
        GameEvent(f"Recoges {amount} monedas de oro.", Severity.GOOD),
    )


def _pickup_flares(
    state: GameState, room: Room, rng: RandomSource
) -> tuple[GameState, tuple[GameEvent, ...]]:
    amount = d(rng, 5) + 1
    return _consume(state, state.player.with_flares(amount), room), (
        GameEvent(f"Te haces con {amount} bengalas.", Severity.GOOD),
    )


def _resolve_sinkhole(state: GameState) -> tuple[GameState, tuple[GameEvent, ...]]:
    pos = state.player.position
    if pos.z >= CASTLE_LEVELS:
        return state, (
            GameEvent("El sumidero ruge bajo tus pies, pero no hay más abajo.", Severity.WARN),
        )
    new_pos = Coord(pos.x, pos.y, pos.z + 1)
    state2 = _move_to(state, new_pos)
    return state2, (GameEvent("¡El suelo cede y caes al nivel inferior!", Severity.MAGIC),)


def _resolve_warp(state: GameState, rng: RandomSource) -> tuple[GameState, tuple[GameEvent, ...]]:
    if state.player.position == state.castle.orb_of_zot_at and not state.player.has_orb_of_zot:
        new_player = replace(state.player, has_orb_of_zot=True)
        room = state.castle.at(state.player.position)
        return _consume(state, new_player, room), (
            GameEvent("¡Dentro del warp encuentras el ORBE DE ZOT!", Severity.MAGIC),
        )
    new_pos = Coord(d(rng, 8), d(rng, 8), d(rng, 8))
    return _move_to(state, new_pos), (
        GameEvent("El warp retuerce la realidad — apareces en otro lugar.", Severity.MAGIC),
    )


def pick_up_treasure(
    state: GameState, rng: RandomSource
) -> tuple[GameState, tuple[GameEvent, ...]]:
    """Recoge el tesoro de la habitación actual."""
    del rng  # firma uniforme; no se usa
    room = state.castle.at(state.player.position)
    if room.glyph != Glyph.TREASURE or room.payload is None:
        return state, ()
    t = Treasure(int(room.payload))
    new_player = state.player.with_treasure(t)
    return _consume(state, new_player, room), (
        TreasureFound(f"Recoges {TREASURE_NAME[t]}.", Severity.GOOD, treasure=t),
    )


def drink_pool(state: GameState, rng: RandomSource) -> tuple[GameState, tuple[GameEvent, ...]]:
    """Bebe del charco mágico (8 resultados aleatorios). [DATO] línea 2890."""
    room = state.castle.at(state.player.position)
    if room.glyph != Glyph.POOL:
        return state, (GameEvent("Aquí no hay ningún charco.", Severity.WARN),)
    roll = d(rng, 8)
    if roll <= 6:
        return _drink_stat(state, roll, rng)
    if roll == 7:
        return _drink_change_race(state, rng)
    return _drink_change_sex(state)


def _drink_stat(
    state: GameState, roll: int, rng: RandomSource
) -> tuple[GameState, tuple[GameEvent, ...]]:
    p = state.player
    delta_table: dict[int, tuple[int, int, int, str]] = {
        1: (-d(rng, 3), 0, 0, "te sientes más débil."),
        2: (+d(rng, 3), 0, 0, "te sientes más fuerte."),
        3: (0, -d(rng, 3), 0, "te sientes más torpe."),
        4: (0, +d(rng, 3), 0, "te sientes más despierto."),
        5: (0, 0, -d(rng, 3), "te sientes más patoso."),
        6: (0, 0, +d(rng, 3), "te sientes más ágil."),
    }
    st, iq, dx, msg = delta_table[roll]
    new_player = p.with_stats(strength=st, intelligence=iq, dexterity=dx)
    sev = Severity.GOOD if max(st, iq, dx) > 0 else Severity.BAD
    return state.with_player(new_player), (GameEvent(f"Bebes y {msg}", sev),)


def _drink_change_race(
    state: GameState, rng: RandomSource
) -> tuple[GameState, tuple[GameEvent, ...]]:
    p = state.player
    new_race = rng.choice([r for r in Race if r != p.race])
    return state.with_player(replace(p, race=new_race)), (
        GameEvent(f"El charco te transforma en un {new_race.value}.", Severity.MAGIC),
    )


def _drink_change_sex(state: GameState) -> tuple[GameState, tuple[GameEvent, ...]]:
    p = state.player
    new_sex = Sex.FEMALE if p.sex == Sex.MALE else Sex.MALE
    return state.with_player(replace(p, sex=new_sex)), (
        GameEvent(
            f"El charco te cambia el sexo — ahora eres {new_sex.value.lower()}.", Severity.MAGIC
        ),
    )


def tick_curses(state: GameState, rng: RandomSource) -> tuple[GameState, tuple[GameEvent, ...]]:
    """Aplica al final del turno: contraer / sufrir / curar maldiciones."""
    p = state.player
    events: list[GameEvent] = []

    for curse in Curse:
        ward = CURSE_WARD[curse]
        if curse in p.curses or p.has_treasure(ward):
            continue
        if chance(rng, 1, 250):
            p = p.with_curse(curse)
            events.append(
                CurseAcquired(
                    f"Una bocanada de aire helado: la maldición de {_curse_label(curse)} te toca.",
                    Severity.WARN,
                    curse=curse,
                )
            )

    if Curse.LEECH in p.curses and not p.has_treasure(CURSE_WARD[Curse.LEECH]):
        stolen = d(rng, 5)
        taken = min(p.gold, stolen)
        if taken > 0:
            p = p.with_gold(-taken)
            events.append(GameEvent(f"La Sanguijuela te roba {taken} gp.", Severity.WARN))

    state, p = _maybe_forget_room(state, p, rng)

    if p.is_blind and p.has_treasure(Treasure.OPAL_EYE):
        p = replace(p, is_blind=False)
        events.append(GameEvent("¡El Ojo de Ópalo te devuelve la vista!", Severity.GOOD))
    if p.book_stuck and p.has_treasure(Treasure.BLUE_FLAME):
        p = replace(p, book_stuck=False)
        events.append(
            GameEvent("La Llama Azul incinera el libro pegado a tus manos.", Severity.GOOD)
        )

    p = p.tick_turn()
    return state.with_player(p), tuple(events)


def _maybe_forget_room(
    state: GameState, player: Player, rng: RandomSource
) -> tuple[GameState, Player]:
    if not (
        Curse.FORGETFULNESS in player.curses
        and not player.has_treasure(CURSE_WARD[Curse.FORGETFULNESS])
        and chance(rng, 1, 4)
    ):
        return state, player
    z = player.position.z
    coord = Coord(d(rng, 8), d(rng, 8), z)
    room = state.castle.at(coord)
    new_castle: Castle = state.castle.with_room(coord, replace(room, discovered=False))
    return state.with_castle(new_castle), player


# ─── Helpers ───────────────────────────────────────────────────────────────


def _consume(state: GameState, new_player: Player, room: Room) -> GameState:
    """Marca la habitación como vaciada y aplica el nuevo jugador."""
    castle = state.castle.with_room(new_player.position, room.clear())
    return state.with_player(new_player).with_castle(castle)


def _move_to(state: GameState, target: Coord) -> GameState:
    """Mueve al jugador a `target` revelando la habitación destino."""
    castle = state.castle.with_room(target, state.castle.at(target).reveal())
    return state.with_player(state.player.at(target)).with_castle(castle)


def _curse_label(curse: Curse) -> str:
    return {
        Curse.LETHARGY: "la Letargia",
        Curse.LEECH: "la Sanguijuela",
        Curse.FORGETFULNESS: "el Olvido",
    }[curse]
