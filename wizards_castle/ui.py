"""Tiny terminal UI helpers — colour, prompts, map rendering.

Stdlib-only: writes ANSI escape codes directly. If the output stream is
not a TTY (pipe, CI, tests) the colours collapse to plain text so log
captures stay readable.
"""

from __future__ import annotations

import os
import sys
from typing import Callable, Iterable

from .castle import Castle
from .data import CASTLE_SIZE, Glyph
from .player import Player


_ANSI = {
    "reset": "\033[0m",
    "bold": "\033[1m",
    "dim": "\033[2m",
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
    "white": "\033[37m",
}

_GLYPH_COLOR = {
    Glyph.ENTRANCE: "cyan",
    Glyph.STAIRS_UP: "cyan",
    Glyph.STAIRS_DOWN: "cyan",
    Glyph.POOL: "blue",
    Glyph.CHEST: "yellow",
    Glyph.GOLD: "yellow",
    Glyph.FLARES: "yellow",
    Glyph.WARP: "magenta",
    Glyph.SINKHOLE: "magenta",
    Glyph.CRYSTAL_ORB: "magenta",
    Glyph.BOOK: "green",
    Glyph.MONSTER: "red",
    Glyph.VENDOR: "green",
    Glyph.TREASURE: "yellow",
    Glyph.EMPTY: "dim",
    Glyph.UNKNOWN: "dim",
}


def _ansi_enabled() -> bool:
    if os.environ.get("NO_COLOR"):
        return False
    return sys.stdout.isatty()


def colour(text: str, name: str) -> str:
    if not _ansi_enabled():
        return text
    code = _ANSI.get(name)
    if not code:
        return text
    return f"{code}{text}{_ANSI['reset']}"


def banner(text: str) -> None:
    print(colour(text, "cyan"))


def info(text: str) -> None:
    print(text)


def warn(text: str) -> None:
    print(colour(text, "yellow"))


def good(text: str) -> None:
    print(colour(text, "green"))


def bad(text: str) -> None:
    print(colour(text, "red"))


def magic(text: str) -> None:
    print(colour(text, "magenta"))


# ---------------------------------------------------------------------------
# Prompts
# ---------------------------------------------------------------------------

def ask(prompt: str, *, default: str | None = None,
        validate: Callable[[str], bool] | None = None,
        input_fn: Callable[[str], str] = input) -> str:
    """Prompt until the user's reply passes `validate`."""
    suffix = f" [{default}]" if default else ""
    while True:
        try:
            raw = input_fn(f"{prompt}{suffix}: ").strip()
        except EOFError:
            raw = ""
        if not raw and default is not None:
            raw = default
        if validate is None or validate(raw):
            return raw
        warn("That doesn't look right — try again.")


def ask_choice(prompt: str, choices: Iterable[str], *,
               input_fn: Callable[[str], str] = input) -> str:
    """Prompt for a single-character choice. Returns the matched choice (upper)."""
    options = [c.upper() for c in choices]
    options_str = "/".join(options)
    while True:
        raw = ask(f"{prompt} ({options_str})", input_fn=input_fn).upper()
        if raw and raw[0] in options:
            return raw[0]


# ---------------------------------------------------------------------------
# Map rendering
# ---------------------------------------------------------------------------

def render_level(castle: Castle, player: Player, level: int,
                 reveal_all: bool = False) -> str:
    """ASCII grid of one level. Player marked with `*`."""
    px, py, pz = player.position
    rows = []
    for y in range(1, CASTLE_SIZE + 1):
        cells = []
        for x in range(1, CASTLE_SIZE + 1):
            room = castle.at((x, y, level))
            visible = reveal_all or room.discovered
            if (x, y, level) == player.position:
                cells.append(colour("*", "bold"))
            elif visible:
                ch = room.glyph.value
                cells.append(colour(ch, _GLYPH_COLOR.get(room.glyph, "white")))
            else:
                cells.append(colour("?", "dim"))
        rows.append(" ".join(cells))
    header = colour(f"  Level {level}    ", "bold") + (
        f"(you are at {px},{py})" if pz == level else "(another floor)"
    )
    return header + "\n" + "\n".join(rows)


def show_status(player: Player) -> None:
    print()
    for line in player.status_lines():
        print(line)
    print()
