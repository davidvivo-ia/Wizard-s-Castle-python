# Arquitectura

## Visión general

Arquitectura hexagonal (puertos + adaptadores) con cuatro capas concéntricas.
El núcleo (`domain`) no conoce nada del exterior; las capas externas dependen
hacia adentro, jamás al revés.

```
┌────────────────────────────────────────────────────────────────────┐
│                        presentation/                               │
│  Textual TUI · Typer CLI · Demo runner                             │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                      application/                            │  │
│  │  Use cases: NewGame, MovePlayer, FightMonster, OpenChest…    │  │
│  │                                                              │  │
│  │  ┌────────────────────────────────────────────────────────┐  │  │
│  │  │                    domain/                             │  │  │
│  │  │  Pure: Castle, Room, Player, Monster, Treasure,        │  │  │
│  │  │  Curse, Combat resolution functions, RNG protocol      │  │  │
│  │  └────────────────────────────────────────────────────────┘  │  │
│  │                                                              │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                   infrastructure/                            │  │
│  │  RNG impl (random.Random), JSON save/load, XDG paths,        │  │
│  │  structlog config, theme assets loader                       │  │
│  └──────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────┘
            │                                │
            ▼                                ▼
       Terminal TTY                   ~/.local/share/wizards_castle/
```

## Capas

### `domain/` — núcleo puro
- Cero IO. Cero dependencias externas (ni `random`, ni `pathlib`, ni `time`).
- Tipos inmutables: `dataclass(frozen=True, slots=True)` o `Enum`.
- Modela las reglas del castillo: generación, movimiento, resolución de
  combate, eventos de habitación. Las funciones reciben un `Random` como
  protocolo (puerto), no instancian uno.
- Cobertura objetivo: ≥ 90 %.

### `application/` — orquestación
- Casos de uso que combinan operaciones de dominio en transacciones
  reproducibles. Cada uno toma una `GameState` (inmutable) y devuelve
  `(GameState_nueva, list[GameEvent])`.
- Ningún caso de uso lee del usuario: recibe la decisión ya tomada.
- Permite que la presentación sea intercambiable (TUI, CLI, demo).

### `infrastructure/` — adaptadores
- Implementación concreta del puerto RNG (`StdLibRandom`).
- Persistencia JSON con esquema versionado (`SaveV1`).
- Resolución XDG de `~/.local/share/wizards_castle/`.
- Configuración de `structlog`.

### `presentation/` — interfaz humana
- Textual TUI con CSS propio en `assets/wizards_castle.tcss`.
- Typer CLI: `wizards-castle`, `wizards-castle --demo --seed 42`,
  `wizards-castle --classic`.
- Demo runner determinista: alimenta decisiones desde un `GameDirector` que
  busca el Orb of Zot por BFS sobre el mapa generado con el seed dado.

## Puertos (interfaces)

```python
class RandomSource(Protocol):
    def randint(self, a: int, b: int) -> int: ...
    def choice(self, seq: Sequence[T]) -> T: ...
    def shuffle(self, seq: list[T]) -> None: ...

class GameClock(Protocol):
    def now(self) -> datetime: ...

class SaveStore(Protocol):
    def save(self, slot: str, state: GameState) -> None: ...
    def load(self, slot: str) -> GameState: ...
    def list_slots(self) -> list[str]: ...
```

## Flujo de un turno

```
TUI capta tecla
   │
   ▼
TUI traduce a Command (enum)
   │
   ▼
Use case ExecuteCommand(state, command, rng) ──► domain.movement
                                            └──► domain.combat
                                            └──► domain.events
   │
   ▼
(state', events') devuelto al TUI
   │
   ▼
TUI renderiza events' como mensajes y refresca widgets
```

## Inmutabilidad

`GameState` es `frozen=True, slots=True`. Cada caso de uso devuelve un nuevo
state (compartiendo subobjetos vía referencia). Esto permite:

- Tests deterministas sin mocks ni `setUp`.
- Replay y *rewind* (no implementado en v1.0, viable en v1.1).
- Save trivial: serializa el state actual.

## Dependencias entre módulos

```
presentation ──► application ──► domain
       │              │
       └──► infrastructure ◄────┘
```

Ningún ciclo, sin importes hacia capas externas.

## Errores

Jerarquía propia en `domain/errors.py`:

```
WizardsCastleError
├── DomainError
│   ├── InvalidMoveError
│   ├── NoStairsError
│   └── BlindError
├── ApplicationError
│   └── SaveCorruptedError
└── PresentationError
```

Mensajes en español en la presentación; los mensajes técnicos en logs van en
inglés.

## Observabilidad

`structlog` con renderer `ConsoleRenderer` en TTY, JSON en pipe/CI.
Eventos clave loggeados con nivel INFO: `game.start`, `room.entered`,
`combat.resolved`, `treasure.acquired`, `game.over`.
