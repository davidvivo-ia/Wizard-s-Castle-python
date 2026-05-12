# TODO — backlog para v1.1+

Items recogidos durante la implementación de v1.0 y aplazados deliberadamente.

## v1.1
- [ ] Audio: beeps sintetizados estilo AY-3-8912 (`infrastructure/audio.py`).
- [ ] Tema claro pulido (`assets/light.tcss`).
- [ ] Hambre con efecto: penalización tras 60 turnos sin matar monstruo
  (el original sólo lo cuenta).
- [ ] Late-game scaling del coste de pociones del vendedor (1000 → 1000+turn*10)
  para que no se trivialice tras un cofre grande.
- [ ] Replay de partidas guardadas (rewind sobre `GameState` inmutable).
- [ ] Internacionalización: extraer mensajes a `assets/i18n/{es,en}.toml`.

## Limitaciones conocidas v1.0
- Modo `--classic` aproxima el sesgo del RND Apple II con un LCG corto;
  no es bit-exact.
- TUI no probada en Windows Terminal Legacy (pre-Windows 10 1909).
