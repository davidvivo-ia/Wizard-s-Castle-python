# Sistema de diseño

## Concepto

> "Un castillo encantado de 1980 visto desde 2026: serif noble en un terminal
> de fósforo, glifos cuadrados, color contenido, sensación de pergamino bajo
> luz ámbar."

Fusión moderna-retro: la TUI de Textual respira como un Spectrum / Apple II
("scanlines" sugeridas por bordes y separadores), pero la legibilidad y el
ritmo son los de una IDE moderna. Sin emojis ni iconos vector, sólo glifos
ASCII / Unicode geométricos.

## Paleta

Inspirada en el ámbar de los monitores monocromos de la época, con tres
acentos para semántica de juego.

| Nombre semántico | Hex      | Rol                                       | Contraste vs `bg` |
| --- | --- | --- | --- |
| `bg`             | `#0E1014`| Fondo (negro azulado profundo)            | —                 |
| `bg-elevated`    | `#1A1D24`| Paneles destacados                        | —                 |
| `text`           | `#E6D9B8`| Texto principal (pergamino cálido)        | 11.4 : 1 (AAA)    |
| `muted`          | `#7A6F58`| Texto secundario                          | 4.6 : 1 (AA)      |
| `primary`        | `#FFB347`| Ámbar / acento principal (entrada, oro)   | 9.2 : 1 (AAA)     |
| `accent`         | `#7AC4FF`| Frío / mágico (orbe, warp, hechizo)       | 8.1 : 1 (AAA)     |
| `success`        | `#9CCB6F`| Éxito (subes stat, encuentras tesoro)     | 7.7 : 1 (AAA)     |
| `warning`        | `#E0B96A`| Aviso (curse, weapon broken)              | 7.0 : 1 (AAA)     |
| `error`          | `#E16A6A`| Daño, muerte                              | 5.0 : 1 (AA)      |

Todos los pares texto/fondo cumplen WCAG AA mínimo, AAA en la mayoría.

## Tipografía

- UI: **Noto Sans Mono** (fallback `IBM Plex Mono`, luego mono del sistema).
  Textual usa el monoespaciado de la terminal del usuario; recomendamos en
  `README.md` cualquier fuente Nerd Font o IBM Plex Mono.
- Decorativa (banner ASCII): **Big** del paquete `figlet`, renderizado a
  buildtime y guardado como cadena para no requerir dependencia.

## Espaciado

Sistema de **8 columnas** en el grid de Textual:

- `1` ≡ 1 columna terminal.
- `padding: 1 2` (vertical 1, horizontal 2) por defecto en paneles.
- Separación entre secciones: línea horizontal de `─` en `muted`.

## Iconografía

Glifos de un único carácter ASCII para fidelidad al original; opcionalmente
Unicode con `--unicode-glyphs`:

| Concepto | ASCII | Unicode |
| --- | --- | --- |
| Empty | `.` | `·` |
| Entrance | `E` | `▣` |
| Stairs up / down | `<` `>` | `▲` `▼` |
| Pool | `P` | `≈` |
| Chest | `C` | `▦` |
| Gold | `G` | `¤` |
| Flares | `F` | `✦` |
| Warp | `W` | `◯` |
| Sinkhole | `S` | `◢` |
| Crystal orb | `O` | `◉` |
| Book | `B` | `▤` |
| Monster | `M` | `♦` |
| Vendor | `V` | `▼` |
| Treasure | `T` | `◆` |
| Player | `*` | `★` |

## Estados clave

| Estado | Pantalla | Notas |
| --- | --- | --- |
| Splash | `SplashScreen` | Banner ASCII, tagline, prompt "Press Enter". |
| Character creation | `CharacterScreen` | Wizard 4 pasos: race → sex → bonus → gear. |
| Game | `GameScreen` | Mapa + log + status + input. |
| Combat | `CombatModal` | Sobre `GameScreen`, foco en monstruo. |
| Vendor | `VendorModal` | Sobre `GameScreen`, listado de oferta. |
| Game over | `GameOverScreen` | Resumen + "play again?" |
| Help | `HelpModal` | Tabla de comandos. |

## Layout principal `GameScreen`

```
┌──────────────────────────────────────────────────────────────────────┐
│  Wizard's Castle                            seed 42  ·  turn 17      │
├───────────────────────┬──────────────────────────────────────────────┤
│   ░ . ░ . ? ? ? ?     │ STR  9/10   INT  8/8   DEX 12/12             │
│   . > . . ? ? ? ?     │ Gold 137    Flares 4   Lamp ✓                │
│   . . * . ? ? ? ?     │ Weapon: Mace  Armor: Chainmail (10/14)       │
│   ? ? ? ? ? ? ? ?     │ Treasures: Pale Pearl, Palantir              │
│   ? ? ? ? ? ? ? ?     │ Curses: —    Runestaff: ✓   Orb of Zot: —    │
│   ? ? ? ? ? ? ? ?     │                                              │
│   ? ? ? ? ? ? ? ?     │ ▸ You step on a frog.                        │
│   ? ? ? ? ? ? ? ?     │ ▸ Here you find a magic pool.                │
│   Level 3, (3,3)      │ ▸ Drink from the pool? (Y/N)                 │
├───────────────────────┴──────────────────────────────────────────────┤
│  > _                                                                 │
└──────────────────────────────────────────────────────────────────────┘
```

## Microinteracciones

- **Movimiento**: el glifo `*` del jugador parpadea suavemente (CSS
  `animation`) durante 200 ms al entrar en una sala nueva.
- **Daño**: el panel de status hace flash en `error` durante 150 ms.
- **Tesoro**: línea de log con prefijo `★` en `primary`.
- **Combate**: el modal aparece con `transition` (fade) en 120 ms.

## Accesibilidad

- Navegación 100 % por teclado (Textual default).
- Modo claro/oscuro: el oscuro es default; claro vía `--theme light` carga
  `assets/light.tcss`.
- No dependemos sólo del color: cada estado relevante lleva un glifo o
  prefijo textual (`★`, `▸`, `!`, `×`).
- Respeta `NO_COLOR` y `FORCE_COLOR`.

## Toque distintivo

**Pantalla de carga estilo Spectrum**: al iniciar el juego, los bordes del
terminal se rellenan durante 800 ms con bandas alternadas de los siete colores
clásicos del ZX (negro, azul, rojo, magenta, verde, cian, amarillo) usando
caracteres `▀▄`. Es un homenaje breve, después colapsa al fondo `bg` y
desaparece. Skipable con Enter.

## Sonido

v1.0: silencio. Hay placeholder `infrastructure/audio.py` documentado para
v1.1 con beeps sintetizados (chip AY-3-8912 emulado vía `numpy`).

## Mensajes al usuario

En **español**, tono ligeramente arcaico para casar con el tema, sin
caer en el cliché:

- "Una bocanada de aire helado te recorre la espalda — has invocado la
  *Maldición de la Sanguijuela*."
- "El comerciante posa los ojos en tu Palantir y sonríe."
- "El balrog te alcanza con su látigo. Tu armadura cruje."

## Idiomas internos

| Capa | Idioma |
| --- | --- |
| Identificadores en código | Inglés |
| Logs (`structlog`) | Inglés |
| Commits | Inglés (Conventional) |
| Mensajes al jugador | Español |
| Documentación | Español |
