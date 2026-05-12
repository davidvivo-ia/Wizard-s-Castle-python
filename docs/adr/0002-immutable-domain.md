# ADR 0002 — Modelo de dominio inmutable

- **Estado**: Aceptada
- **Fecha**: 2026-05-12

## Contexto

El estado del juego se modifica cada turno: posición del jugador, contenido de
la habitación visitada, stats, oro, inventario, banderas de maldiciones, mapa
descubierto. Hay dos enfoques canónicos:

1. **Mutable OOP**: `Player`, `Castle`, `Room` con métodos que mutan campos.
   Familiar en Python, fácil de escribir, difícil de razonar y testear con
   propiedades. La mutación encubierta es el origen de la mayoría de bugs en
   código de juego.
2. **Inmutable funcional**: `frozen=True, slots=True`. Cada operación devuelve
   una versión nueva del estado. Más verboso pero trivial de razonar, fácil
   de paralelizar y de serializar.

## Decisión

**Modelos de dominio inmutables con `dataclass(frozen=True, slots=True)`.**

Compartiremos subobjetos por referencia para que la copia sea barata. El
estado completo del juego es un `GameState` inmutable; cada caso de uso
recibe `state` y devuelve `(state', events)`.

## Consecuencias

Positivas:

- Tests sin mocks: pasas un `GameState` y compruebas que el devuelto cumple
  las invariantes esperadas.
- Replay y save trivial: serializar un `GameState` es serializar un árbol
  de dataclasses inmutables.
- `mypy --strict` da garantías reales: nadie muta nada por sorpresa.
- *Property-based testing* con Hypothesis es directo: generar `GameState`s y
  comprobar invariantes (suma de oro nunca negativa, número de tesoros no
  decrece tras pickup, etc.).

Negativas:

- Sintaxis más verbosa en sitios concretos (`dataclasses.replace(state,
  player=replace(state.player, gold=state.player.gold + n))`).
- El mapa `Castle` es grande (8 × 8 × 8 = 512 rooms) y se "copia" en cada
  turno; mitigado porque la inmutabilidad es estructural, no profunda
  (Python comparte referencias).

## Alternativas descartadas

- `attrs` con `frozen=True`: mismo trade-off, pero `dataclasses` viene en
  stdlib y satisface lo que necesitamos.
- `pydantic.BaseModel`: añade validación pesada que no necesitamos en el
  hot path. Pydantic queda reservado para fronteras IO/config (modelos de
  save, configuración CLI).
