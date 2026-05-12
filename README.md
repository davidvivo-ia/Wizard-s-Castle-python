# Wizard's Castle (Python 2026)

Reinterpretación moderna del clásico **The Wizard's Castle** (Joseph R. Power,
*Recreational Computing*, julio/agosto 1980).

```text
   __        ___                  _ _      ____           _   _
   \ \      / (_)______ _ _ __ __| ( )___ / ___|__ _ ___| |_| | ___
    \ \ /\ / /| |_  / _` | '__/ _` |// __| |   / _` / __| __| |/ _ \
     \ V  V / | |/ / (_| | | | (_| | \__ \ |__| (_| \__ \ |_| |  __/
      \_/\_/  |_/___\__,_|_|  \__,_| |___/\____\__,_|___/\__|_|\___|
```

## Instalación

```bash
uv sync           # crea entorno y dependencias
uv run wizards-castle           # lanza la TUI
uv run wizards-castle --demo --seed 42   # demo determinista
uv run wizards-castle --classic          # RNG sesgado tipo Apple II
```

## Arquitectura

Hexagonal en cuatro capas (`domain`, `application`, `infrastructure`,
`presentation`). Ver `docs/architecture.md`, `docs/design.md` y los ADRs en
`docs/adr/`.

## Calidad

```bash
uv run ruff format --check .
uv run ruff check .
uv run mypy --strict src
uv run pytest --cov=src --cov-report=term-missing
```

## Legacy

El BASIC original de 1980 vive en `legacy/` (read-only) con notas de
procedencia en `legacy/SOURCES.md`. El análisis arqueológico está en
`docs/original_program_analysis.md`.

## Licencia

MIT — ver [`LICENSE`](LICENSE).
