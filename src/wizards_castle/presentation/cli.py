"""Stub CLI — implementación real en Fase 7."""

from __future__ import annotations

import typer

app = typer.Typer(help="Wizard's Castle — port 2026.")


@app.command()
def play() -> None:
    """Lanza el juego (placeholder)."""
    typer.echo("Coming soon.")


if __name__ == "__main__":
    app()
