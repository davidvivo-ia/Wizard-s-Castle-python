"""CLI con Typer: comandos `play`, `demo`, `load`, `analyze`."""

from __future__ import annotations

import secrets
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from wizards_castle.application.demo_runner import run_demo
from wizards_castle.domain.castle import generate_castle
from wizards_castle.infrastructure.logging import configure as configure_logging
from wizards_castle.infrastructure.rng import LCGRandom, StdLibRandom
from wizards_castle.infrastructure.save import load_from_path
from wizards_castle.presentation.tui import run_tui, run_tui_state

app = typer.Typer(
    name="wizards-castle",
    help="Wizard's Castle (Power, 1980) — port 2026.",
    no_args_is_help=False,
)

console = Console()


def _make_rng(seed: int | None, *, classic: bool) -> tuple[StdLibRandom | LCGRandom, int]:
    """Construye el RNG resolviendo seed; devuelve (rng, seed_efectivo)."""
    effective_seed = seed if seed is not None else secrets.randbits(32)
    if classic:
        return LCGRandom(effective_seed), effective_seed
    return StdLibRandom(effective_seed), effective_seed


# ─── Comandos ──────────────────────────────────────────────────────────────


@app.command()
def play(
    seed: Annotated[int | None, typer.Option(help="Seed del RNG.")] = None,
    classic: Annotated[bool, typer.Option(help="RNG sesgado tipo Apple II.")] = False,
    load: Annotated[Path | None, typer.Option(help="Carga una partida guardada.")] = None,
) -> None:
    """Lanza la TUI de Textual."""
    configure_logging()
    if load is not None:
        state = load_from_path(load)
        console.print(f"[green]Cargada partida: {load}[/green]")
    else:
        rng, effective_seed = _make_rng(seed, classic=classic)
        console.print(f"[dim]seed={effective_seed}{' (classic)' if classic else ''}[/dim]")
        run_tui(rng, seed=effective_seed, classic=classic)
        return
    run_tui_state(state)


@app.command()
def demo(
    seed: Annotated[int, typer.Option(help="Seed del RNG.")] = 42,
    classic: Annotated[bool, typer.Option(help="RNG sesgado tipo Apple II.")] = False,
    quiet: Annotated[bool, typer.Option(help="Sólo muestra el resultado final.")] = False,
) -> None:
    """Ejecuta una partida demo determinista (no requiere TUI)."""
    configure_logging()
    rng, effective_seed = _make_rng(seed, classic=classic)
    mode = " · classic" if classic else ""
    console.print(f"[bold cyan]Demo[/bold cyan] (seed={effective_seed}{mode})")
    state, log = run_demo(rng, seed=effective_seed)
    if not quiet:
        for evt in log[-25:]:  # últimos 25 eventos para no saturar
            color = {
                "good": "green",
                "warn": "yellow",
                "bad": "red",
                "magic": "magenta",
                "info": "white",
            }.get(evt.severity.value, "white")
            console.print(f"[{color}]▸ {evt.message}[/{color}]")
    if state.is_won:
        console.print("[bold green]✦ Demo COMPLETADA: el orbe ha vuelto.[/bold green]")
    elif state.is_lost:
        console.print("[bold red]✕ Demo: el demo-héroe ha caído.[/bold red]")
    else:
        console.print("[bold yellow]· Demo: límite de turnos alcanzado.[/bold yellow]")
    console.print(
        f"[dim]Stats finales: STR={state.player.strength} INT={state.player.intelligence} "
        f"DEX={state.player.dexterity} GP={state.player.gold} "
        f"Tesoros={len(state.player.treasures)} Turno={state.player.turn}[/dim]"
    )


@app.command()
def analyze(
    seed: Annotated[int, typer.Option(help="Seed del RNG.")] = 42,
) -> None:
    """Imprime un resumen del castillo generado con `seed`."""
    rng = StdLibRandom(seed)
    castle = generate_castle(rng)
    console.print(f"[bold]Castillo seed={seed}[/bold]")
    console.print(f"  Entrada: {castle.entrance}")
    console.print(f"  Orbe de Zot: {castle.orb_of_zot_at}")
    console.print(f"  Runestaff dentro de monstruo en: {castle.runestaff_monster_at}")


# Hook para `wizards-castle` sin subcomando: lanza play.
@app.callback(invoke_without_command=True)
def _main(
    ctx: typer.Context,
    demo_flag: Annotated[bool, typer.Option("--demo", help="Atajo para `demo`.")] = False,
    seed: Annotated[int | None, typer.Option(help="Seed del RNG global.")] = None,
    classic: Annotated[bool, typer.Option(help="RNG sesgado tipo Apple II.")] = False,
) -> None:
    """Sin subcomando, ejecuta `play` (o `demo` con --demo)."""
    if ctx.invoked_subcommand is not None:
        return
    if demo_flag:
        demo(seed if seed is not None else 42, classic=classic, quiet=False)
        raise typer.Exit
    play(seed=seed, classic=classic, load=None)


if __name__ == "__main__":
    app()
