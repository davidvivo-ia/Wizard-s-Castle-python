"""Punto de entrada `python -m wizards_castle`."""

from wizards_castle.presentation.cli import app


def main() -> None:
    """Lanza la CLI con Typer."""
    app()


if __name__ == "__main__":
    main()
