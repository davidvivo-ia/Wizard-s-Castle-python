# Changelog

Todos los cambios notables de este proyecto se documentan aquí.
Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/),
versionado [SemVer](https://semver.org/lang/es/).

## [1.0.0] — 2026-05-12

Primera entrega completa del port. Reinterpretación 2026 del BASIC de
Joseph R. Power (1980) en Python 3.13+ con arquitectura hexagonal,
interfaz Textual, persistencia JSON y modo demo determinista.

### Preservado del original
- 8 × 8 × 8 castillo toroidal (wrap E/W/N/S, escaleras conectan niveles).
- 4 razas (Hobbit, Elf, Human, Dwarf) con sus stats canónicos
  (`ST = 2 + 2·RC`, `DX = 14 - 2·RC`, hobbit con +12 puntos extra).
- 12 monstruos del listado original, sus HP y daño (Kobold 2/1 →
  Dragón 13/4) incluyendo break-weapon de Gárgola y Dragón.
- 8 tesoros con sus efectos canónicos (Ojo de Ópalo cura ceguera,
  Llama Azul disuelve libros pegados, etc.).
- Combate Attack / Retreat / Web / Fireball / Deathspell / Bribe.
- 3 maldiciones (Letargia, Sanguijuela, Olvido) con sus tesoros de protección.
- Charcos mágicos con los 8 efectos (incluido cambio de raza/sexo).
- Warps que esconden el Orbe de Zot; Runestaff escondido en monstruo.
- Glifos de habitación de un único carácter ASCII como en el listado original.

### Modernizado
- Python 3.13+ con type hints estrictos (`mypy --strict`) y
  `dataclass(frozen=True, slots=True)` en todo el dominio.
- Arquitectura hexagonal: `domain` puro sin IO, `application` orquesta,
  `infrastructure` adaptadores, `presentation` Textual + Typer.
- RNG inyectado (`RandomSource` Protocol). Modo `--seed N` reproducible.
- Modo `--classic` con LCG corto que aproxima el sesgo del RND Apple II
  (no bit-exact pero captura el "sabor" repetitivo).
- Persistencia JSON con Pydantic v2; rutas XDG vía `platformdirs`.
- Logging con `structlog` (consola en TTY, JSON en pipes).
- Suite de tests: 124 unitarios + integración + propiedad (Hypothesis).
- CI matrix Python 3.13/3.14 con pre-commit hooks (ruff, mypy).

### Añadido
- Comando CLI `wizards-castle play` (TUI por defecto).
- Comando `wizards-castle demo --seed N` determinista (no requiere TTY).
- Comando `wizards-castle analyze --seed N` que imprime info del castillo.
- Comando `wizards-castle play --load <path>` para cargar partida.
- TUI con paleta "ámbar sobre pergamino" (ver `docs/design.md`).

### Licencias creativas tomadas
- **[LICENCIA CREATIVA] Vendor único por nivel**: el original coloca 3
  vendors por nivel (línea 1335 de `origwiz.bas`). Reducido a 1 para
  mejorar la jugabilidad sin perder funcionalidad.
- **[LICENCIA CREATIVA] Maldiciones probabilísticas**: el original
  pre-coloca las 3 curses en habitaciones específicas (`C(3,4)`); aquí
  se contraen con probabilidad pequeña por turno si no llevas el ward.
  Mantiene el efecto de juego sin la complejidad de tracking espacial.
- **[LICENCIA CREATIVA] Localización a español**: el original es 100 %
  inglés. Mensajes de juego traducidos preservando el tono ("**TWAS A
  SOAP OPERA**" → "una telenovela repetida").
- **[LICENCIA CREATIVA] Manuales de fuerza/dexteridad**: el original
  fija stat = 18 al leer el libro adecuado. Aquí simplificamos a +1
  permanente (más justo y escalable). [SUPUESTO] de balance.

### Bugs corregidos
- **B7** (variable `MC` muerta del original): eliminada por completo.
- **B5** (loop potencial en placement de salas): generación moderna usa
  cola pre-mezclada por nivel, garantía determinista de placement sin
  ciclos.
- Typos del listado original (corrección ya aplicada por Beej Jorgensen
  en `legacy/ibm-pc/castle.bas`, ver cabecera del fichero).

### Notas
- Cobertura de tests: 89 % global, 97 % en `domain/`.
- Calidad: `ruff format --check`, `ruff check`, `mypy --strict`,
  `pytest` y `wizards-castle demo --seed 42` pasan limpios.
