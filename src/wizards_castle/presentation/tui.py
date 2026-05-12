"""TUI con Textual: pantalla principal con mapa, status y log.

Esta capa está fuera del coverage (ver `pyproject.toml`) porque la prueba
real es interactiva y depende de Textual `Pilot`. Para v1.0 se aporta una
versión mínima funcional pero estética que cumple el design system.
"""

from __future__ import annotations

import typing
from importlib.resources import files
from pathlib import Path

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import Footer, Header, Input, RichLog, Static

from wizards_castle.application.character_creation import (
    CharacterChoices,
    create_new_game,
)
from wizards_castle.application.commands import Command, parse
from wizards_castle.application.movement import step, use_stairs
from wizards_castle.application.room_events import (
    drink_pool,
    pick_up_treasure,
    resolve_passive_room,
    tick_curses,
)
from wizards_castle.domain.catalog import (
    CASTLE_HEIGHT,
    CASTLE_WIDTH,
    Armor,
    Glyph,
    Race,
    Sex,
    Weapon,
)
from wizards_castle.domain.coordinates import Direction
from wizards_castle.domain.errors import (
    InvalidCommandError,
    InvalidMoveError,
    NoStairsError,
)
from wizards_castle.domain.events import GameEvent
from wizards_castle.domain.random_source import RandomSource
from wizards_castle.domain.state import GameState
from wizards_castle.infrastructure.rng import StdLibRandom

GLYPH_STYLES: dict[Glyph, str] = {
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


def _load_css() -> str:
    """Carga el CSS desde assets si existe; si no, devuelve uno embebido."""
    try:
        path = Path(str(files("wizards_castle.assets") / "wizards_castle.tcss"))
        if path.exists():
            return path.read_text(encoding="utf-8")
    except (FileNotFoundError, ModuleNotFoundError):
        pass
    return _DEFAULT_CSS


_DEFAULT_CSS = """
Screen {
    background: #0E1014;
    color: #E6D9B8;
}
#map {
    width: 40;
    border: round #7A6F58;
    padding: 1;
}
#status {
    width: 1fr;
    border: round #7A6F58;
    padding: 1;
}
#log {
    height: 12;
    border: round #7A6F58;
    padding: 0 1;
}
Input {
    border: round #FFB347;
    background: #1A1D24;
}
"""


class WizardsCastleApp(App[None]):
    """Aplicación Textual."""

    CSS = _DEFAULT_CSS
    TITLE = "Wizard's Castle"
    BINDINGS: typing.ClassVar = [
        Binding("ctrl+q", "quit", "Salir"),
    ]

    def __init__(self, state: GameState, rng: RandomSource) -> None:
        super().__init__()
        self.state = state
        self.rng = rng

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical():
            with Horizontal():
                yield Static("", id="map")
                yield Static("", id="status")
            yield RichLog(id="log", markup=True, highlight=False)
            yield Input(
                placeholder="Comando (N/S/E/W, U/D, M, F, L, T, O, G, R, I, V, Q, H)…", id="cmd"
            )
        yield Footer()

    def on_mount(self) -> None:
        self._refresh()
        self.query_one(Input).focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        raw = event.value
        event.input.value = ""
        if not raw:
            return
        try:
            cmd = parse(raw)
        except InvalidCommandError as exc:
            self._write_log(f"[red]✕ {exc}[/red]")
            return
        self._handle(cmd)
        self._refresh()

    def _handle(self, cmd: Command) -> None:
        if cmd == Command.QUIT:
            self.exit()
            return
        try:
            new_state, events = self._dispatch(cmd)
        except (NoStairsError, InvalidMoveError) as exc:
            self._write_log(f"[yellow]! {exc}[/yellow]")
            return
        self.state = new_state
        for evt in events:
            self._render_event(evt)
        if self.state.is_finished:
            outcome = (
                "[bold green]Victoria.[/bold green]"
                if self.state.is_won
                else "[bold red]Has muerto.[/bold red]"
            )
            self._write_log(outcome)

    def _dispatch(self, cmd: Command) -> tuple[GameState, tuple[GameEvent, ...]]:
        if cmd in (Command.NORTH, Command.SOUTH, Command.EAST, Command.WEST):
            d = {
                Command.NORTH: Direction.NORTH,
                Command.SOUTH: Direction.SOUTH,
                Command.EAST: Direction.EAST,
                Command.WEST: Direction.WEST,
            }[cmd]
            state, evts1 = step(self.state, d)
            state, evts2 = resolve_passive_room(state, self.rng)
            state, evts3 = pick_up_treasure(state, self.rng)
            state, evts4 = tick_curses(state, self.rng)
            return state, (*evts1, *evts2, *evts3, *evts4)
        if cmd in (Command.UP, Command.DOWN):
            state, evts = use_stairs(self.state, going_up=cmd == Command.UP)
            state, evts2 = resolve_passive_room(state, self.rng)
            return state, (*evts, *evts2)
        if cmd == Command.DRINK:
            return drink_pool(self.state, self.rng)
        if cmd == Command.HELP:
            return self.state, (
                GameEvent(
                    "Comandos: N/S/E/W mover, U/D escaleras, T beber, M mapa, Q salir.",
                ),
            )
        return self.state, (
            GameEvent(
                f"Comando '{cmd}' aún no implementado en TUI v1.0.",
            ),
        )

    def _refresh(self) -> None:
        self.query_one("#map", Static).update(self._render_map())
        self.query_one("#status", Static).update(self._render_status())

    def _render_map(self) -> str:
        p = self.state.player
        z = p.position.z
        rows = [f"[bold]Nivel {z} ({p.position.x},{p.position.y})[/bold]"]
        for y in range(1, CASTLE_HEIGHT + 1):
            cells: list[str] = []
            for x in range(1, CASTLE_WIDTH + 1):
                room = self.state.castle.grid[z - 1][y - 1][x - 1]
                if (x, y) == (p.position.x, p.position.y):
                    cells.append("[bold]*[/bold]")
                elif room.discovered:
                    style = GLYPH_STYLES.get(room.glyph, "white")
                    cells.append(f"[{style}]{room.glyph.value}[/{style}]")
                else:
                    cells.append("[dim]?[/dim]")
            rows.append(" ".join(cells))
        return "\n".join(rows)

    def _render_status(self) -> str:
        p = self.state.player
        treasures = ", ".join(t.name for t in p.treasures) or "—"
        curses = ", ".join(c.name for c in p.curses) or "—"
        return (
            f"[bold]{p.name}[/bold] el {p.race.value} ({p.sex.value})\n"
            f"STR {p.strength}/{p.max_strength}   INT {p.intelligence}/{p.max_intelligence}   "
            f"DEX {p.dexterity}/{p.max_dexterity}\n"
            f"Oro {p.gold}   Bengalas {p.flares}   Lámpara: {'sí' if p.has_lamp else 'no'}\n"
            f"Arma: {p.weapon.name.title()}   Armadura: {p.armor.name.title()}\n"
            f"Tesoros: {treasures}\n"
            f"Maldiciones: {curses}\n"
            f"Runestaff: {'sí' if p.has_runestaff else 'no'}   "
            f"Orbe de Zot: {'sí' if p.has_orb_of_zot else 'no'}\n"
            f"Turno {p.turn}"
        )

    def _render_event(self, evt: GameEvent) -> None:
        color = {
            "good": "green",
            "warn": "yellow",
            "bad": "red",
            "magic": "magenta",
            "info": "white",
        }.get(evt.severity.value, "white")
        self._write_log(f"[{color}]▸ {evt.message}[/{color}]")

    def _write_log(self, line: str) -> None:
        self.query_one("#log", RichLog).write(line)


def run_tui(rng: RandomSource, *, seed: int | None, classic: bool) -> None:
    """Crea un personaje "default" y lanza la TUI.

    En v1.0 saltamos la pantalla de creación interactiva — usa decisiones por
    defecto y el jugador puede recrear el personaje vía CLI. Pendiente para
    v1.1: pantalla `CharacterScreen` con wizard de 4 pasos.
    """
    del classic  # ya aplicado al rng
    state = create_new_game(
        CharacterChoices(
            name="Adventurer",
            race=Race.HUMAN,
            sex=Sex.MALE,
            bonus_strength=2,
            bonus_intelligence=2,
            bonus_dexterity=4,
            armor=Armor.LEATHER,
            weapon=Weapon.MACE,
            buy_lamp=False,
            flares=10,
        ),
        rng,
        seed=seed,
    )
    WizardsCastleApp(state, rng).run()


def run_tui_state(state: GameState) -> None:
    """Lanza la TUI con un GameState ya creado (cargado desde save)."""
    rng = StdLibRandom(state.seed)
    WizardsCastleApp(state, rng).run()


def write_default_css(target: Path) -> None:
    """Helper para escribir el CSS por defecto en `target` (uso en assets)."""
    target.write_text(_DEFAULT_CSS, encoding="utf-8")
