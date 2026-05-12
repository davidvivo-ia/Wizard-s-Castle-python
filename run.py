"""Lanzador "doble-clic" del juego sin dependencias externas.

Uso:
    python run.py              # arranca la TUI con un personaje por defecto
    python run.py --demo       # ejecuta la demo determinista
    python run.py --seed 42    # partida reproducible
    python run.py --classic    # RNG sesgado tipo Apple II

Si no tienes dependencias instaladas, este script intenta instalarlas con
`pip install -e .` antes de lanzar el juego. Si tienes `uv`, usa eso por
ser más rápido.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def _ensure_dependencies() -> None:
    """Comprueba si las dependencias están instaladas; si no, las instala."""
    try:
        import textual  # noqa: F401
        import typer  # noqa: F401

        return
    except ImportError:
        pass

    print("Instalando dependencias por primera vez... (esto tarda ~30 s)")
    if shutil.which("uv"):
        subprocess.check_call(["uv", "sync"], cwd=ROOT)
        # Re-lanzamos con el python de uv.
        venv_python = ROOT / ".venv" / ("Scripts" if sys.platform == "win32" else "bin") / "python"
        if venv_python.exists():
            subprocess.check_call([str(venv_python), __file__, *sys.argv[1:]])
            sys.exit(0)
    else:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-e", str(ROOT)],
        )


def main() -> None:
    _ensure_dependencies()
    # Ya con dependencias, delegamos a la CLI real.
    from wizards_castle.presentation.cli import app

    app()


if __name__ == "__main__":
    main()
