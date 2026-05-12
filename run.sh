#!/usr/bin/env bash
# Wizard's Castle — lanzador Linux / macOS.
# Usa `uv` si está disponible; si no, cae a `python run.py`.

set -euo pipefail
cd "$(dirname "$0")"

if command -v uv >/dev/null 2>&1; then
    exec uv run wizards-castle "$@"
fi

if command -v python3 >/dev/null 2>&1; then
    exec python3 run.py "$@"
fi

if command -v python >/dev/null 2>&1; then
    exec python run.py "$@"
fi

echo "Necesitas Python 3.13+ instalado." >&2
exit 1
