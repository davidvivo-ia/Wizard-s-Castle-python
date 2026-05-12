"""Lanzador "doble-clic" del juego sin dependencias externas.

Uso:
    python run.py              # arranca la TUI con un personaje por defecto
    python run.py demo --seed 42        # demo determinista
    python run.py play --seed 42        # partida reproducible
    python run.py play --classic        # RNG sesgado tipo Apple II
    python run.py analyze --seed 42     # info del castillo generado

Compatible con Python 3.11 o superior. Si no tienes las dependencias
instaladas, este script las instala con `uv` (si está disponible) o `pip`.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MIN_VERSION = (3, 11)


def _check_python_version() -> None:
    if sys.version_info < MIN_VERSION:
        major, minor = MIN_VERSION
        current = f"{sys.version_info.major}.{sys.version_info.minor}"
        print(f"[ERROR] Necesitas Python {major}.{minor} o superior. Tienes {current}.")
        print("        Descarga la última versión en https://www.python.org/downloads/")
        sys.exit(1)


def _dependencies_ready() -> bool:
    try:
        import textual  # noqa: F401
        import typer  # noqa: F401

        import wizards_castle  # noqa: F401

        return True
    except ImportError:
        return False


def _install_dependencies() -> None:
    print("Instalando dependencias por primera vez... (puede tardar 30-60 s)")
    if shutil.which("uv"):
        print("  -> usando uv (rápido)")
        subprocess.check_call(["uv", "sync"], cwd=ROOT)
        # Re-lanzamos el script con el python del venv que uv ha creado.
        scripts_dir = "Scripts" if sys.platform == "win32" else "bin"
        venv_python = ROOT / ".venv" / scripts_dir / ("python.exe" if sys.platform == "win32" else "python")
        if venv_python.exists():
            subprocess.check_call([str(venv_python), str(Path(__file__)), *sys.argv[1:]])
            sys.exit(0)
    else:
        print("  -> usando pip (instala 'uv' para que sea más rápido)")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "--upgrade", "pip"],
        )
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-e", str(ROOT)],
        )


def main() -> None:
    _check_python_version()
    if not _dependencies_ready():
        _install_dependencies()
    # Ya con dependencias, delegamos a la CLI real.
    from wizards_castle.presentation.cli import app

    app()


if __name__ == "__main__":
    main()
