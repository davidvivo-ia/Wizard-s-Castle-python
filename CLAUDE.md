# CLAUDE.md

## Misión

Tomar un programa de los años 80 (BASIC ZX Spectrum, Amstrad CPC, Sega
Mega Drive/Genesis, Commodore 64, MSX, Apple II, IBM PC, etc.) y
reconstruirlo como obra de software de 2026: juego completo, jugable,
empaquetado, testeado, documentado y con diseño visual cuidado.

Preservas la lógica funcional y el "alma" del original. Reimaginas todo
lo demás.

No es traducción línea a línea. Es reinterpretación con criterio de
ingeniero senior y sensibilidad de diseñador.

## Obtención del código original (FASE -1)

Antes de cualquier otra cosa, comprueba si `legacy/` contiene código
fuente.

### Caso A: `legacy/` ya tiene código
Procede directamente a la Fase 0.

### Caso B: `legacy/` está vacío o solo contiene una nota del usuario
La nota indicará el juego o tipo de programa que quiero recrear. Búscalo tú.
Tu trabajo es encontrar código fuente real de los años 80 y copiarlo a
`legacy/` antes de empezar.

(Resto de la spec — versión almacenada para referencia operativa,
ver mensaje original del usuario para texto canónico completo.)

## Resumen operativo

- Stack: Python 3.13+, uv, pydantic v2, typer, textual (default TUI),
  pygame-ce (si gráfico), structlog, pytest+hypothesis, ruff, mypy --strict.
- Layout: `src/<paquete>/{domain,application,infrastructure,presentation}`.
- Quality gates: `uv sync`, `ruff format --check`, `ruff check`,
  `mypy --strict src`, `pytest --cov=src` >=80%, `uv run <paquete> --demo --seed 42`.
- Documentación en español, código en inglés, mensajes de juego en español.
- Modo autónomo: no pregunto, decido y sigo. ADRs en `docs/adr/` para las
  decisiones importantes.
- Marcadores: `[DATO]`, `[INFERENCIA]`, `[SUPUESTO]`, `[LICENCIA CREATIVA]`.

Para Wizard's Castle (Power, 1980) la presentación es **Textual TUI**
(juego de texto puro con menús, sin sprites). Plataforma canónica para
arqueología: listado original Apple II / IBM PC en Microsoft BASIC.
