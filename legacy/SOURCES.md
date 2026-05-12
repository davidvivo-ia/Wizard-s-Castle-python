# Fuentes del código legacy

Este directorio contiene **código BASIC original de 1980** preservado tal cual
para su uso como referencia arqueológica. Read-only.

## Programa: *The Wizard's Castle*

- **Autor**: Joseph R. Power
- **Año**: 1980 (escrito a mediados de los 70, publicado oficialmente en 1980)
- **Publicación canónica**: revista *Recreational Computing*, número de
  julio/agosto de 1980.
- **Plataforma original**: Exidy Sorcerer en Microsoft BASIC, portado de
  inmediato a Heath/Zenith Microsoft BASIC, TRS-80, Apple II, Commodore PET,
  CP/M, IBM PC (BASICA/GW-BASIC). El dialecto Microsoft BASIC es el común a
  todos esos ports.
- **Copyright**: 1980 Joseph R. Power. De facto abandonware desde hace
  décadas; el código fue publicado para mecanografiarse en casa, sin
  registro formal de copyright cumplido. Mantenido públicamente en
  repositorios académicos y de preservación digital. Lo usamos aquí bajo
  criterio de *fair use* educativo y arqueológico.

## Archivos importados

### `ibm-pc/castle.bas`
- **URL**: <https://github.com/beejjorgensen/Wizards-Castle-Info/blob/master/src/castle.bas>
- **Descargado**: 2026-05-12 desde `raw.githubusercontent.com`.
- **Procedencia última**: Beej Jorgensen lo recuperó del repositorio
  `gstein.svn.beanstalkapp.com/oss/trunk/wizcastle/wiz.bas` (Greg Stein) con
  correcciones tipográficas verificadas contra el escaneo del artículo
  original de *Recreational Computing*. Las correcciones están listadas en
  la cabecera del fichero como `Was:` / `Now:`.
- **Líneas**: 372.

### `ibm-pc/castle_commented.bas`
- **URL**: <https://github.com/beejjorgensen/Wizards-Castle-Info/blob/master/src/castle_commented.bas>
- **Descargado**: 2026-05-12.
- **Notas**: Misma fuente con comentarios añadidos por Beej línea a línea.
  No es código original puro, pero es invaluable como Rosetta Stone. Lo
  guardamos para mapeo de variables y secciones.
- **Líneas**: 1221.

### `exidy-sorcerer/origwiz.bas`
- **URL**: <https://github.com/gondur/The-Wizard-s-Castle/blob/master/origwiz.bas>
- **Descargado**: 2026-05-12.
- **Procedencia última**: Listado publicado en *Recreational Computing*
  jul/ago 1980, modificado por J. F. Stetson para Heath Microsoft BASIC.
  Cabecera del fichero documenta la transcripción.
- **Líneas**: 919. Más prolijo que `castle.bas` (números de línea cada 5
  en vez de cada 10, una sentencia por línea en lugar de la
  compactación con `:`).
- **Versión elegida como canónica para arqueología**: ésta, por estar
  más cerca del listado tipográfico original y ser estructuralmente
  más limpia.

### `ibm-pc/wizards_castle_spec.md`
- **URL**: <https://github.com/beejjorgensen/Wizards-Castle-Info/blob/master/doc/wizards_castle_spec.md>
- **Descargado**: 2026-05-12.
- **Notas**: Especificación detallada del comportamiento del juego escrita
  por Beej Jorgensen tras leer el BASIC. No es legacy estrictamente, pero
  acelera enormemente la fase de arqueología. Lo tratamos como anexo de
  referencia secundaria.

### `ibm-pc/backstory.md`
- **URL**: <https://github.com/beejjorgensen/Wizards-Castle-Info/blob/master/doc/backstory.md>
- **Descargado**: 2026-05-12.
- **Notas**: Trasfondo narrativo recuperado del artículo de revista.

## Licencia

Los ficheros `.bas` originales están bajo el copyright original de Joseph R.
Power (1980). Se incluyen aquí bajo el principio de preservación arqueológica
de software histórico y *fair use* educativo. **No se distribuirá ningún
binario derivado de estos ficheros**: el port en `src/` es una reimplementación
limpia escrita desde cero leyendo el BASIC como especificación.

La documentación de Beej Jorgensen (`wizards_castle_spec.md`, `backstory.md`)
está licenciada como CC-BY-SA según declara su repositorio.
