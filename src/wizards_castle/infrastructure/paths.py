"""Resolución XDG de las rutas de datos."""

from __future__ import annotations

from pathlib import Path

from platformdirs import user_data_dir

APP_NAME = "wizards_castle"


def data_dir() -> Path:
    """Devuelve el directorio XDG de datos del usuario, creándolo si hace falta."""
    p = Path(user_data_dir(APP_NAME))
    p.mkdir(parents=True, exist_ok=True)
    return p


def save_path(slot: str = "auto") -> Path:
    """Construye la ruta del fichero de save para `slot`."""
    safe = "".join(c for c in slot if c.isalnum() or c in "-_") or "auto"
    return data_dir() / f"slot-{safe}.json"
