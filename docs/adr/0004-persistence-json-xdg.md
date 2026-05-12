# ADR 0004 — Persistencia: JSON sobre XDG

- **Estado**: Aceptada
- **Fecha**: 2026-05-12

## Contexto

El BASIC original no guardaba partidas. Los ports modernos suelen ofrecer
save/load. Necesitamos un formato:

- Trivial de versionar (`version` field).
- Legible por humanos para debugging.
- Sin dependencias pesadas.
- Ubicado en una ruta estándar respetando XDG en Linux/macOS y `%LOCALAPPDATA%`
  en Windows.

## Decisión

- **Formato**: JSON (con `indent=2`), validado a la entrada por modelos
  Pydantic v2 (`SaveV1`).
- **Ubicación**: `platformdirs.user_data_dir("wizards_castle")` por defecto;
  esto resuelve a `~/.local/share/wizards_castle/` en Linux,
  `~/Library/Application Support/wizards_castle/` en macOS y
  `%LOCALAPPDATA%\wizards_castle\` en Windows.
- **Slots**: archivos `slot-NN.json` o `slot-<nombre>.json`. CLI permite
  guardar y cargar por nombre; UI muestra los slots existentes.
- **Versión**: campo `version: int = 1`. Migraciones futuras se gestionan en
  `infrastructure/save.py` con función `migrate_v1_to_v2`.

## Consecuencias

Positivas:

- Los saves son inspeccionables con `cat`.
- `platformdirs` aísla nuestra lógica de las diferencias de plataforma.
- Pydantic v2 valida en la frontera y deja el dominio limpio.

Negativas:

- Pydantic v2 es una dependencia más; la mantenemos sólo en `infrastructure/`.
- JSON no es ideal para mapas grandes; mitigado porque 8 × 8 × 8 = 512
  rooms generan un fichero de ~6 KB.
