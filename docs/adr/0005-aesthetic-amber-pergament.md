# ADR 0005 — Estética: ámbar sobre pergamino

- **Estado**: Aceptada
- **Fecha**: 2026-05-12

## Contexto

Cómo "vestir" la TUI sin caer en pastiche y sin renunciar al guiño retro.
Tres direcciones consideradas:

1. **Mimetismo Spectrum**: paleta de los 15 colores Sinclair, BRIGHT 0/1,
   bordes a rayas. Atractivo pero estridente para una sesión larga.
2. **Plano moderno minimalista**: paleta neutra (gris-azulado), tipografía
   limpia. Profesional pero no transmite "1980".
3. **Ámbar sobre pergamino**: monitor monocromo cálido (homenaje a
   IBM 5151, Hercules, terminales VT220 amber) con tres acentos
   semánticos. Cálido, legible, evocador.

## Decisión

**Ámbar sobre pergamino.** Paleta y detalles en `docs/design.md`.

## Consecuencias

Positivas:

- Contraste WCAG AAA en la mayoría de combinaciones.
- Sesgo cálido reduce fatiga visual frente al azul puro.
- Permite que los acentos (tesoros = `primary`, magia = `accent`,
  daño = `error`) destaquen sin saturar.
- Coexistencia con tema claro (`assets/light.tcss`) que aún no está pulido
  pero queda en hueco para v1.1.

Negativas:

- En terminales con paletas no-true-color, los hex se aproximan a 256
  colors; verificado que sigue siendo legible.
- El "guiño Spectrum" se reserva al splash screen (banderas en bordes 800ms),
  para no comprometer la legibilidad del juego.
