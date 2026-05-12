# Análisis arqueológico del programa original

## Fase 0 — Encuadre

### Programa
*The Wizard's Castle*, de **Joseph R. Power**, publicado como listado en la
revista *Recreational Computing*, julio/agosto de 1980.

### Lenguaje y dialecto
Microsoft BASIC (Exidy Sorcerer y Heath/Zenith). El listado adapta convenciones
muy específicas de esta familia:

- `DEFINT A-Z` declara todas las variables como enteros 16-bit.
- `DEF FNA(Q)=...` define funciones inline de un único argumento.
- `:` separa varias sentencias por línea (compactación memoria-cinta).
- Cadenas terminadas en `$`, arrays homónimos. Subíndices 1-based.
- Sin alcance léxico: todo es global. Bucles cerrados por `NEXT Q`,
  saltos con `GOTO` y `GOSUB`/`RETURN`.
- I/O: `INPUT`, `LINE INPUT`, `PRINT`, control de pantalla con
  `PRINT CHR$(27);"E"` (clear screen ANSI Heath H-19) y `CHR$(7)` (bell).

### Plataforma original
Exidy Sorcerer (1978), procesador Z80, 8-32 KB de RAM, ROM de Microsoft BASIC.
El listado se portó casi inmediatamente a TRS-80, Apple II, Commodore PET,
CP/M, y a IBM PC en BASICA/GW-BASIC. Para este proyecto tomamos como **versión
canónica** el listado `legacy/exidy-sorcerer/origwiz.bas` por ser el más
fiel al texto impreso original (una sentencia por línea, numeración cada 5).

### Año
1980. Power lo había escrito a mediados de los 70 según notas del autor en
`legacy/ibm-pc/backstory.md`.

### Sinopsis funcional
Roguelike de texto en un castillo 3D de 8 × 8 × 8 = 512 habitaciones. El
jugador crea un personaje (raza, sexo, atributos, equipamiento), entra por la
sala E en la planta 1, y explora para encontrar el *Orb of Zot* — escondido
dentro de una sala "warp" en algún nivel — y salir vivo por la entrada.

Lo que hay en las habitaciones: monstruos, tesoros, vendedores, libros,
cofres, charcos mágicos, sumideros, orbes de cristal, bengalas, pilas de oro,
escaleras y los famosos warps. Combate por turnos con ataque/retirada/conjuro/
soborno. Cuatro razas con atributos distintos. Tres maldiciones latentes que
se activan al entrar en habitaciones marcadas. Vampiros que drenan
permanentemente la fuerza. Una cura para la ceguera (Opal Eye), un disolvente
de libros pegados (Blue Flame), tres tesoros que neutralizan maldiciones.

### Lectura crítica
Para 1980, el diseño es notable: aleatoriedad bien aprovechada, economía
interna de tesoros↔maldiciones, balance entre exploración y combate, sin
pantallas gráficas pero con tanto contenido como un Adventure de Crowther.
Los bugs documentados son todos *typos de imprenta*, no errores de lógica.
La mecánica más controvertida es el coste fijo de subir un punto de stat
(1000 gp en vendedor), que escala mal con la dificultad.

### Versiones comparadas en `legacy/`
| Carpeta | Procedencia | Uso aquí |
| --- | --- | --- |
| `exidy-sorcerer/origwiz.bas` | *Recreational Computing* jul/ago 1980, transcrito por J. F. Stetson para Heath MS-BASIC | **Canónica** para arqueología y mapeo línea-a-línea. |
| `ibm-pc/castle.bas` | Greg Stein + Beej Jorgensen | Referencia comparativa; tiene compactación con `:`, mismo flujo. |
| `ibm-pc/castle_commented.bas` | Beej Jorgensen | Rosetta Stone — variables y secciones explicadas en comentarios. |

---

## Fase 1 — Arqueología

### Grafo de flujo (alto nivel)

```
                ┌──────────────────────────────┐
                │ 1090..1180  INIT ARRAYS      │
                │  - C$(34), I$(34)  rooms     │
                │  - L(512)          map flat  │
                │  - W$(8), E$(8)    items/food│
                │  - R$(4)           races     │
                └──────────────┬───────────────┘
                               │
                ┌──────────────▼───────────────┐
                │ 1185..1245  Intro banner     │
                │  (sólo primera partida)      │
                └──────────────┬───────────────┘
                               │
                ┌──────────────▼───────────────┐
                │ 1250..1495  GENERATE CASTLE  │
                │  - place entrance at (1,4,1) │
                │  - stairs up/down each level │
                │  - 12 monsters per level     │
                │  - 24 items + 3 vendors / lvl│
                │  - 8 treasures sprinkled     │
                │  - 3 curse rooms             │
                │  - Runestaff inside monster  │
                │  - Orb of Zot inside a warp  │
                └──────────────┬───────────────┘
                               │
                ┌──────────────▼───────────────┐
                │ 1500..1930  CHARACTER CREATE │
                │  race → stats, bonus points, │
                │  buy armor/weapon/lamp/flares│
                └──────────────┬───────────────┘
                               │
                ┌──────────────▼───────────────┐
                │ 3450  ROOM ENTRY (status +   │
                │       resolve room contents) │◀──┐
                └──────────────┬───────────────┘   │
                               │                   │
                ┌──────────────▼───────────────┐   │
                │ 1940..2430  MAIN LOOP        │   │
                │  curse ticks, random hint    │   │
                │  prompt command N/S/E/W/U/D/ │   │
                │  M/F/L/G/T/DR/O/H/Q          │   │
                └──────────────┬───────────────┘   │
                               │                   │
                ┌──────────────▼───────────────┐   │
                │ Dispatch:                    │   │
                │ 2435 move N                  │   │
                │ 2440 move S/E/W              │   │
                │ 2465 up, 2480 down           │───┤ back to room entry
                │ 2540 map, 2620 flare         │   │
                │ 2770 lamp, 2890 drink pool   │   │
                │ 2965 open chest/book         │   │
                │ 3185 gaze orb, 3315 teleport │   │
                │ 3390 quit                    │   │
                │ → on monster: 4185 COMBAT    │───┘
                └──────────────────────────────┘

                ┌──────────────────────────────┐
                │ 4185..4905  COMBAT           │
                │  attack / retreat / spell /  │
                │  bribe; vampire drain        │
                │  armour soak via 4860 GOSUB  │
                └──────────────┬───────────────┘
                               │
                ┌──────────────▼───────────────┐
                │ 4910  DEATH                  │
                │ 4970  EXIT WITHOUT/WITH ORB  │
                │ 5055  POST-GAME SUMMARY      │
                │ 5110  Play again? → 1105     │
                └──────────────────────────────┘
```

### Inventario de variables globales

| Símbolo | Tipo | Significado |
| --- | --- | --- |
| `X, Y, Z` | int | Posición actual del jugador (1-8 cada eje, Z = nivel). |
| `RC` | int | Race code: 1=Hobbit, 2=Elf, 3=Man, 4=Dwarf. |
| `SX` | int | Sex: 0=female, 1=male. |
| `ST, IQ, DX` | int | Strength, Intelligence, Dexterity. Tope 18 vía `FNC`. |
| `GP` | int | Gold pieces. |
| `FL` | int | Flares. |
| `LF` | int | Lamp flag (0/1). |
| `WV, AV` | int | Weapon value (0..3) y armor value (0..3). |
| `AH` | int | Armor hit points restantes (7/14/21 según AV). |
| `T` | int | Turn counter. |
| `H` | int | Last meal turn (60-turn hunger window tras matar). |
| `BL` | int | Blind flag. |
| `BF` | int | Book-stuck flag. |
| `VF` | int | Vendor-hostility flag (attacked vendor previously). |
| `RF, OF` | int | Runestaff flag / Orb-of-Zot-acquired flag. |
| `TC` | int | Treasure count. |
| `T(8)` | int[] | Treasure ownership flags. |
| `C(3,4)` | int[][] | Curse rooms: `(curse_idx, [x,y,z,active])`. |
| `R(3), O(3)` | int[] | Coordenadas del Runestaff (R) y del Orb of Zot (O). |
| `L(512)` | int[] | Mapa lineal 8×8×8. Indexado por `FND(Z)`. |
| `C$(34)` | str[] | Descripción larga de cada tipo de contenido. |
| `I$(34)` | str[] | Glifo de 1 carácter de cada tipo. |
| `W$(8)` | str[] | Nombres de armas y armaduras. |
| `E$(8)` | str[] | Sufijos de comida ("sandwich", "stew", ...). |
| `R$(4)` | str[] | Nombres de razas. |
| `NG` | int | Numero de partida (`NG` >1 salta el intro). |

### Códigos de contenido de habitación (`L(...)`)

Almacenados como `código + 100` mientras estén ocultos.
`FNE(Q) = Q - 100` si `Q > 99` los desvela.

| Código | Contenido | Glifo |
| --- | --- | --- |
| 1 | Empty room | `.` |
| 2 | Entrance | `E` |
| 3 | Stairs up | `U` |
| 4 | Stairs down | `D` |
| 5 | Magic pool | `P` |
| 6 | Chest | `C` |
| 7 | Gold pieces | `G` |
| 8 | Flares | `F` |
| 9 | Warp | `W` |
| 10 | Sinkhole | `S` |
| 11 | Crystal orb | `O` |
| 12 | Book | `B` |
| 13 | Kobold | `M` |
| 14 | Orc | `M` |
| 15 | Wolf | `M` |
| 16 | Goblin | `M` |
| 17 | Ogre | `M` |
| 18 | Troll | `M` |
| 19 | Bear | `M` |
| 20 | Minotaur | `M` |
| 21 | Gargoyle | `M` |
| 22 | Chimera | `M` |
| 23 | Balrog | `M` |
| 24 | Dragon | `M` |
| 25 | Vendor | `V` |
| 26 | Ruby Red (treasure) | `T` |
| 27 | Norn Stone | `T` |
| 28 | Pale Pearl | `T` |
| 29 | Opal Eye | `T` |
| 30 | Green Gem | `T` |
| 31 | Blue Flame | `T` |
| 32 | Palantir | `T` |
| 33 | Silmaril | `T` |
| 34 | "Unknown" / hidden glyph | `?` |

### Inventario de subrutinas (por línea)

| Línea | Etiqueta | Qué hace |
| --- | --- | --- |
| `5285` | `place_random` | Toma `Q` y `Z`, busca slot vacío (101) en el nivel `Z`, asigna `L(FND(Z))=Q`. |
| `5375` | `print_separator` | Imprime 64 asteriscos. |
| `5405` | `prompt_choice` | "YOUR CHOICE", lee `O$` y se queda con la primera letra. |
| `5415` | `read_one_char` | `INPUT O$ : O$=LEFT$(O$,1)`. |
| `5430` | `read_bonus_points` | Pide cuántos puntos asignar a `Z$`, valida 0..OT. |
| `5485` | `read_coord_1_8` | Pide coordenada 1..8, valida. |
| `5525` | `vendor_potion_prompt` | "Buy a potion of `Z$` for 1000 gp"? |
| `5540` | `print_new_stat` | "Your `Z$` is now `Q`." |
| `5555` | `vendor_buy_header` | "These are the types of `Z$` you can buy:" |
| `5570` | `print_position` | "You are at (X,Y) level Z." |
| `4860` | `apply_damage` | Damage soak: armadura absorbe, AH baja, se rompe si llega a 0; resto a ST. |
| `5305` | `runestaff_drop` | Recompensa al matar al monstruo que llevaba el Runestaff: arma+armadura+pociones+lamp. |

### Funciones inline (`DEF FN...`)

| Función | Definición | Uso |
| --- | --- | --- |
| `FNA(Q)` | `1 + INT(RND(1)*Q)` | Tirada 1..Q (dado de Q caras). |
| `FNB(Q)` | `Q+8*((Q=9)-(Q=0))` | Wrap toroidal 1..8: 0→8, 9→1. |
| `FNC(Q)` | `-Q*(Q<19)-18*(Q>18)` | Clamp a 18 (sufre del bug de `(bool)`=-1 en MS-BASIC). |
| `FND(Q)` | `64*(Q-1)+8*(X-1)+Y` | Índice plano del array `L(...)` desde X,Y,Z. |
| `FNE(Q)` | `Q+100*(Q>99)` | Reveal: si oculto (>99), resta 100. |

### Mecánicas claves

- **Razas y stats iniciales** (líneas 1425-1565):
  - `ST = 2 + 2*RC` → Hobbit 4, Elf 6, Man 8, Dwarf 10.
  - `DX = 14 - 2*RC` → Hobbit 12, Elf 10, Man 8, Dwarf 6.
  - `IQ = 8` para todos.
  - `OT = 8 + 4*(RC=1)` → Hobbit 12 puntos extras, otros 8.
- **Gold inicial**: 60 gp.
- **Equipo**: armadura (P/C/L/N a 30/20/10/0 gp); arma (S/M/D/N a 30/20/10/0);
  lámpara 20 gp; bengalas 1 gp cada.
- **Combate** (líneas 4185-4855):
  - Bribe disponible sólo si llevas tesoros; el vendedor pide uno aleatorio.
  - Spells: Web (paraliza al monstruo 1..8 turnos, cuesta 1 ST),
    Fireball (2d7 daño, cuesta 1 ST + 1 IQ),
    Deathspell (mata si IQ > random; si no, IQ → 0 y mueres).
  - Ataque acierta si `DX ≥ FNA(20) + 3*BL`. Daño = WV (1..3).
  - Arma se rompe en monstruos 21 (gárgola) y 24 (dragón) con 1/8 prob.
  - Tras matar, "come 1 hora": si llevas más de 60 turnos sin matar, recupera
    hambre. Encuentras 1..1000 gp de botín. Si era el del Runestaff, lo recibes.
  - Daño recibido = `Q1 = 1+INT(A/2)` donde `A = código_monstruo - 12`.
    Soak por armadura, sobrante a ST.
- **Pool** (línea 2890): 8 resultados aleatorios (±1d3 a stats; cambia raza; cambia sexo).
- **Chest**: 1/4 explota (1d6 daño), 2/4 oro (1..1000), 1/4 gas (te empuja).
- **Book**: 1/6 ciegas, 1/6 zot poetry (nada), 1/6 PlayHobbit (nada), 1/6 DX=18,
  1/6 ST=18, 1/6 stuck-to-hands.
- **Crystal orb**: 1/6 yourself bloody (daño), 1/6 yourself drinking (nada),
  1/6 monster gazing back, 1/6 revela contenido aleatorio en nivel,
  1/6 muestra Orb of Zot (con 50% prob. real, 50% mentira), 1/6 soap opera.
- **Curses** (3 rooms con `C(i, x/y/z/active)`):
  1. Lethargy → `T = T + 1` extra cada turno.
  2. Leech → `GP -= FNA(5)` cada turno.
  3. Forgetfulness → re-oculta una habitación aleatoria del nivel.
  Cada curse `i` se activa al entrar en `C(i,1..3)`. Se neutraliza llevando
  el tesoro correspondiente (Ruby Red / Pale Pearl / Green Gem) que pone `T(i)=1`.
- **Sinkhole** (10): te tira un nivel hacia abajo automáticamente.
- **Warp** (9): te teletransporta a coordenadas aleatorias, *excepto* si tu
  posición coincide con `O()` (Orb of Zot) y tu comando fue 'T' (drink): entonces
  recibes el Orb.
- **Vendor** (25): trade / attack / ignore. Tradear vende tesoros y compra
  pociones (+1d6 a stat, 1000 gp), armadura/arma mejor (1250/1500/2000 gp),
  lámpara (1000 gp). Atacar incrementa `VF`; los vendedores hostiles dan
  combate con stats de monstruo nivel 13.

### Bugs y rarezas detectadas

- **B1 — Typos del listado original** (corregidos por Beej al transcribir,
  ver cabecera de `legacy/ibm-pc/castle.bas`): mayúsculas dobles, espacios,
  saltos GOSUB equivocados. Todos están ya corregidos en `origwiz.bas`.
- **B2 — `FNC` clamp asimétrico**: `FNC(Q)` clampa por encima a 18 pero no
  protege por debajo. Si bebes un pool maligno con ST=2 puedes acabar con
  ST=-1, lo que el código maneja por `ON (1-(ST<1)) GOTO ...,4910` (muerte).
  No es bug en realidad, es la mecánica de muerte por stat ≤ 0.
- **B3 — `IF FNA(8) < 4 THEN A=O(1)...`** (línea 3290): cuando el orbe te
  enseña la ubicación del Orb of Zot tiene un 50% de probabilidad de mentir
  con un punto aleatorio. Característica intencional (línea 3290 escoge entre
  posición real y trampa), aunque el texto dice "you see X at (...)" sin
  pista de que pueda ser falso. **Comportamiento confirmado** por Beej.
- **B4 — `IF NG > 1 GOTO 1250`**: la pantalla de intro sólo aparece en la
  primera partida. Eso es intencional para evitar releerla.
- **B5 — Sobreescritura de slot**: la rutina 5285 no protege contra ciclos
  infinitos si por azar no quedan slots libres en el nivel. En la práctica
  no ocurre porque 12 monstruos + 24 items + 3 vendors = 39 < 64 slots,
  pero es una sigilosa bomba de potencial infinite-loop.
- **B6 — Hambre sin penalización**: el contador `H` se actualiza al matar
  un monstruo, pero no hay penalización si pasan 60 turnos sin comer.
  La frase "you spend an hour eating X" es puramente cosmética.
- **B7 — Vendor combat aritmética**: al matar a un vendedor (`A=13` rama
  especial en línea 5305), recibes plate+sword+pociones+lamp pero el
  contador `MC` (monster count, declarado pero apenas usado) decrece.
  `MC` se inicializa implícitamente a 0 y se decrementa en línea 4365.
  No tiene efecto observable. **Restos de funcionalidad incompleta.**

### Bugs corregidos en el port

- **B7 (variable `MC` muerta)**: eliminada. No tiene efecto en el original
  y aporta ruido.
- **B5 (potencial loop)**: la generación moderna usa una cola de slots
  pre-mezclada por nivel, garantizando placement determinista.
- **Bug de balance no en el original pero típico de ports**: el coste fijo
  de 1000 gp por +1d6 stat es absurdamente caro al inicio y absurdamente
  barato tras un par de cofres grandes. Mantenido tal cual por fidelidad,
  con `[LICENCIA CREATIVA]` documentada en `CHANGELOG.md` por si añadimos
  *late-game scaling* en v1.1.

### Decisiones tomadas como [INFERENCIA] / [SUPUESTO]

- **[INFERENCIA]** "Man" del original lo renombramos a "Human" en la versión
  Python: el listado lo usa indistintamente (`R$(3)="MAN"` luego se sobreescribe
  con `"HUMAN"` en línea 1570).
- **[INFERENCIA]** Los monstruos 21 "Gargoyle" y 22 "Chimera" sustituyen al
  par "Vampire/Werewolf" que aparece en algunas variantes (Apple II BASIC
  posterior). Mantenemos Gargoyle/Chimera por fidelidad al listado canónico.
- **[SUPUESTO]** Cuando el original dice "PLAY`R$(FNA(4))`" en el libro
  (línea 3050) genera "PLAYHOBBIT", "PLAYELF", "PLAYMAN", "PLAYDWARF" como
  parodia de revistas de adultos. Lo conservamos como huevo de pascua.
- **[LICENCIA CREATIVA]** El comando `INKEY$` vs `INPUT` del original lo
  reemplazamos por `Input` widget de Textual con autocompletado de
  comandos. La experiencia es más amable sin alterar la semántica.
