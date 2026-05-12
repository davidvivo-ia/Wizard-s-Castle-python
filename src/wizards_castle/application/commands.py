"""Comandos del jugador: enum + parser desde una letra/palabra clave."""

from __future__ import annotations

from enum import StrEnum

from wizards_castle.domain.errors import InvalidCommandError


class Command(StrEnum):
    """Conjunto canónico de comandos del juego.

    El listado original (líneas 2225-2280) usa una sola letra. Mantenemos esa
    convención para fidelidad y la enriquecemos con un help moderno.
    """

    NORTH = "N"
    SOUTH = "S"
    EAST = "E"
    WEST = "W"
    UP = "U"
    DOWN = "D"
    MAP = "M"
    FLARE = "F"
    LAMP = "L"
    GAZE = "G"
    OPEN = "O"
    DRINK = "T"
    READ_RUNESTAFF = "R"
    INVENTORY = "I"
    HELP = "H"
    SAVE = "V"
    QUIT = "Q"


def parse(raw: str) -> Command:
    """Convierte la entrada cruda del usuario en un Command.

    Acepta el primer carácter (case-insensitive). Reconoce alias `?` -> HELP
    y `DR` -> DRINK (compatibilidad con `LINE INPUT` del original).
    """
    if not raw:
        msg = "comando vacío"
        raise InvalidCommandError(msg)
    cleaned = raw.strip().upper()
    if cleaned in ("?",):
        return Command.HELP
    if cleaned.startswith("DR"):
        return Command.DRINK
    first = cleaned[0]
    try:
        return Command(first)
    except ValueError as exc:
        msg = f"comando desconocido: {raw!r}"
        raise InvalidCommandError(msg) from exc
