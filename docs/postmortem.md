# Postmortem — Wizard's Castle (Python 2026)

Llevar el BASIC de Joseph R. Power de 1980 a Python 3.13 ha sido un ejercicio
de arqueología y de contraste. El listado original son 919 líneas de
Microsoft BASIC con `GOTO`/`GOSUB` enredados, variables de una letra,
`DEF FN` para funciones y un único nivel de granularidad: el programa es
un único bloque global. Cabe íntegro en 32 KB de RAM Z80.

El port moderno son ~1.6k líneas de Python distribuidas en cuatro capas
hexagonales: 478 sentencias en `domain/` puro, 222 en `application/`, 138
en `infrastructure/` y unas 320 en `presentation/`. Son dependencias
encapsuladas, dataclasses inmutables, type hints estrictos validados por
`mypy --strict`, RNG inyectado, persistencia JSON y TUI Textual con CSS
propio. Con tests automatizados (124 que cubren el 97 % del dominio),
property-based testing, y CI matrix Python 3.13/3.14.

Lo que se ganó: legibilidad sin pérdida de fidelidad mecánica,
mantenibilidad real, posibilidad de extender con audio/multijugador/replay
sin reescribir, determinismo total para tests y replays, y una experiencia
visual que respeta el espíritu retro pero no obliga al jugador a 80
columnas y `LINE INPUT`.

Lo que se perdió: la sensación de fragilidad y maravilla que tiene un
programa que cabe en una cinta de cassette. El BASIC original es opaco
hasta que lo lees, y entonces se vuelve transparente — *todo* está ahí,
sin abstracciones. La versión 2026 es transparente de otra manera: cada
módulo cuenta su parte, pero ya no puedes abarcarlo de una sentada con un
listado en papel.

¿Qué dice este ejercicio sobre cómo ha cambiado el oficio en 40 años? Que
hemos cambiado densidad por escala. Power escribía un mundo entero en 32
KB porque tenía que; nosotros pagamos megabytes de stack por la garantía
de que el código no muta sin que lo veamos. Ambas son virtudes. La
diferencia es que en 1980 el programador *tenía* que entender la máquina
entera para hacer algo bonito; en 2026 puede confiar en cuarenta capas
construidas por otros y dedicarse al diseño. Hemos perdido cercanía con
el silicio y ganado tiempo para pensar en la experiencia. Si Power leyera
este código probablemente refunfuñaría — pero el día que abriera la TUI y
viera su castillo seguir vivo, creo que sonreiría.
