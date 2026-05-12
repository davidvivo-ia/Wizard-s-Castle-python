# ADR 0001 — Capa de presentación: Textual TUI

- **Estado**: Aceptada
- **Fecha**: 2026-05-12

## Contexto

El BASIC original de Wizard's Castle (1980) es texto puro: `PRINT`, `INPUT`,
`LINE INPUT`, `CHR$(27);"E"` para limpiar pantalla, `CHR$(7)` para *bell*. No
usa caracteres semigráficos sofisticados ni atributos de color del Spectrum;
cabe íntegro en un terminal de 80 × 24 monocromo.

Las opciones consideradas para la presentación moderna son:

1. **CLI con Typer + Rich**: bucle imperativo, `print()` enriquecido, `prompt`
   por turno. Mínima fricción técnica pero imposible mostrar mapa y status
   simultáneamente sin tricks.
2. **TUI con Textual**: framework reactivo, layout declarativo en CSS,
   widgets, modales, animaciones sutiles. Permite reproducir la experiencia
   del original (un sólo terminal) elevándola con un panel persistente para
   mapa+status+log.
3. **Pygame-CE gráfico**: sprites, paleta limitada, pixel art. Excesivo para
   un juego que es 100 % texto en el original.

## Decisión

**Textual TUI.**

## Consecuencias

Positivas:

- Mantiene fidelidad al espíritu "todo en un terminal" del original.
- Permite mostrar mapa + status + log + input simultáneamente sin saturar.
- Animaciones sutiles (fade en modales, parpadeo del jugador) sin necesidad
  de gráficos.
- CSS propio reutilizable y testeable.
- Soporte de tema claro/oscuro y accesibilidad por teclado.

Negativas:

- Dependencia pesada (`textual` arrastra `rich`, `markdown-it-py`,
  `linkify-it-py`, `mdurl`).
- Curva de aprendizaje del modelo reactivo.
- Tests E2E requieren `Pilot` de Textual; los unitarios siguen siendo
  ortogonales gracias a la separación de capas.

Mitigación: el caso de uso `--demo` no usa Textual sino la presentación CLI
mínima, lo cual reduce superficie de fallo en CI y permite grabar GIFs.
