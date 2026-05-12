# ADR 0003 — RNG inyectado y modo classic

- **Estado**: Aceptada
- **Fecha**: 2026-05-12

## Contexto

El BASIC original usa `RND(1)` global. En Apple II y Exidy Sorcerer este
generador tiene un período corto y es famoso por reusar secuencias (ver notas
de MyAbandonware sobre el bug del `RND` en Wizard's Castle), lo que produce
castillos repetitivos y monstruos predecibles.

Dos requisitos en tensión:

1. **Determinismo y testeabilidad**: necesitamos seeds reproducibles, generar
   castillos idénticos a partir del mismo `--seed`, ejecutar `--demo --seed
   42` en CI sin nondeterminismo.
2. **Fidelidad opcional**: jugadores nostálgicos podrían querer la sensación
   del `RND` original.

## Decisión

- **Por defecto**: `random.Random(seed)` de la stdlib, inyectado como
  `RandomSource` (Protocol) en cada operación de dominio. Sin seed
  explícito, usamos `secrets.randbits(32)` para máxima entropía.
- **Modo classic**: `--classic` activa `LCGRandom`, una implementación de
  generador congruencial lineal corto que aproxima el comportamiento sesgado
  del Apple II BASIC. Documentado en `infrastructure/rng.py` con
  referencia a la fórmula histórica.
- **Cero llamadas globales**: `import random` está prohibido fuera de
  `infrastructure/rng.py`. Validado por una regla de `ruff` custom.

## Consecuencias

Positivas:

- Tests deterministas con `seed=0` o `seed=42`.
- `--demo --seed 42` produce siempre la misma partida grabable.
- Modo classic preserva el sabor original sin contaminar el código moderno.
- Hypothesis puede generar seeds aleatorias y comprobar propiedades.

Negativas:

- Hay que pasar el `RandomSource` por casi todas las funciones de dominio.
  Mitigado con un parámetro keyword `*, rng: RandomSource` consistente.

## Implementación de referencia (boceto)

```python
class RandomSource(Protocol):
    def randint(self, a: int, b: int, /) -> int: ...
    def choice(self, seq: Sequence[T], /) -> T: ...
    def shuffle(self, seq: list[T], /) -> None: ...
    def random(self) -> float: ...

class StdLibRandom(RandomSource):
    def __init__(self, seed: int | None = None) -> None: ...

class LCGRandom(RandomSource):
    """Aproxima el RND del Apple II BASIC: LCG de 16 bits con periodo corto."""
```
