# Wizard's Castle (Python 2026)

Reinterpretación moderna de **The Wizard's Castle** (Joseph R. Power,
*Recreational Computing*, julio/agosto de 1980), uno de los primeros
roguelikes en BASIC.

```text
   __        ___                  _ _      ____           _   _
   \ \      / (_)______ _ _ __ __| ( )___ / ___|__ _ ___| |_| | ___
    \ \ /\ / /| |_  / _` | '__/ _` |// __| |   / _` / __| __| |/ _ \
     \ V  V / | |/ / (_| | | | (_| | \__ \ |__| (_| \__ \ |_| |  __/
      \_/\_/  |_/___\__,_|_|  \__,_| |___/\____\__,_|___/\__|_|\___|
```

> *"Many cycles ago, in the kingdom of N'Dic, the gnomic wizard Zot forged
> his great Orb of Power. He soon vanished, leaving behind his vast
> subterranean castle filled with esurient monsters, fabulous treasures,
> and the incredible Orb of Zot. From that time hence, many a bold youth
> has ventured into the Wizard's Castle. As of now, none has ever emerged
> victoriously."* — Joseph R. Power, 1980.

## Instalación rápida

```bash
git clone <repo>
cd Wizard-s-Castle-python
uv sync                                        # crea entorno y dependencias
uv run wizards-castle play                     # TUI Textual (juego principal)
uv run wizards-castle demo --seed 42           # demo determinista (sin TUI)
uv run wizards-castle play --seed 1234         # partida con seed concreta
uv run wizards-castle play --classic           # RNG sesgado tipo Apple II
uv run wizards-castle analyze --seed 42        # info del castillo generado
```

## Comandos en juego

| Tecla | Acción |
| --- | --- |
| `N` `S` `E` `W` | Mover al norte/sur/este/oeste (wrap toroidal) |
| `U` `D` | Subir / bajar escaleras (sólo si estás en una) |
| `M` | Ver mapa del nivel actual |
| `F` | Encender bengala (revela 3 × 3) |
| `L` | Iluminar con la lámpara (rayo en una dirección) |
| `T` | Beber del charco mágico |
| `O` | Abrir libro o cofre |
| `G` | Mirar la bola de cristal |
| `R` | Leer el Runestaff (teletransportarse) |
| `I` | Inventario / status |
| `V` | Guardar partida |
| `Q` | Salir |
| `H` o `?` | Ayuda |

## Documentación

| Documento | Contenido |
| --- | --- |
| [`docs/architecture.md`](docs/architecture.md) | Capas hexagonales, puertos, flujo de un turno. |
| [`docs/design.md`](docs/design.md) | Sistema de diseño: paleta, tipografía, layout. |
| [`docs/original_program_analysis.md`](docs/original_program_analysis.md) | Análisis arqueológico del BASIC original. |
| [`docs/postmortem.md`](docs/postmortem.md) | Reflexión final: qué se ganó, qué se perdió. |
| [`docs/adr/`](docs/adr/) | 5 ADRs: presentación, dominio inmutable, RNG, persistencia, estética. |
| [`legacy/SOURCES.md`](legacy/SOURCES.md) | Procedencia del BASIC original importado. |

## Calidad

```bash
uv run ruff format --check .
uv run ruff check .
uv run mypy --strict src
uv run pytest --cov=src --cov-report=term-missing
uv run wizards-castle demo --seed 42
```

Cobertura: 89 % global, 97 % en `domain/`. CI matrix Python 3.13/3.14.

## Estructura del proyecto

```
.
├── pyproject.toml
├── CLAUDE.md                  ← spec operativa del proyecto
├── README.md  CHANGELOG.md  TODO.md  LICENSE
├── .pre-commit-config.yaml
├── .github/workflows/ci.yml
├── legacy/                    ← BASIC original (read-only)
│   ├── exidy-sorcerer/origwiz.bas    canónica para arqueología
│   ├── ibm-pc/castle.bas             versión Beej Jorgensen
│   └── SOURCES.md
├── src/wizards_castle/
│   ├── domain/                núcleo puro (Player, Castle, combat, …)
│   ├── application/           casos de uso, demo runner, comandos
│   ├── infrastructure/        RNG, save JSON Pydantic, paths XDG, logging
│   ├── presentation/          Typer CLI + Textual TUI
│   └── assets/                CSS Textual
├── tests/{unit,integration,property}
└── docs/{architecture, design, original_program_analysis, postmortem, adr/}
```

## Licencia

MIT — ver [`LICENSE`](LICENSE). El código BASIC original en `legacy/`
está bajo el copyright de Joseph R. Power (1980); se incluye bajo
preservación arqueológica y *fair use* educativo.

## Créditos

- **1980 original**: Joseph R. Power, en Microsoft BASIC, publicado en
  *Recreational Computing* nº jul/ago.
- **2026 port**: este repositorio, escrito desde cero leyendo el BASIC
  como especificación.
- **Análisis y rescate del listado**: Beej Jorgensen
  (<https://github.com/beejjorgensen/Wizards-Castle-Info>) y Greg Stein.
