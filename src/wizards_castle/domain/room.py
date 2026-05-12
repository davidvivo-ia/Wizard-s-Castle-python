"""Modelo inmutable de habitación."""

from __future__ import annotations

from dataclasses import dataclass, replace

from wizards_castle.domain.catalog import Glyph


@dataclass(frozen=True, slots=True)
class Room:
    """Una habitación del castillo.

    `glyph` es el tipo visible. `payload` lleva el subtipo (índice de
    monstruo o de tesoro, cantidad de oro/bengalas, etc.). `discovered`
    indica si el jugador ya ha visto la sala. `cleared` se activa cuando
    el contenido se ha resuelto (monstruo muerto, tesoro cogido).
    """

    glyph: Glyph = Glyph.EMPTY
    payload: int | None = None
    discovered: bool = False
    cleared: bool = False

    def reveal(self) -> Room:
        """Marca la habitación como descubierta sin cambiar nada más."""
        return replace(self, discovered=True)

    def clear(self) -> Room:
        """Vacía la habitación tras resolver su contenido."""
        return replace(self, glyph=Glyph.EMPTY, payload=None, cleared=True)

    def to_short(self) -> str:
        """Glifo de un carácter para el mapa, respetando descubrimiento."""
        return self.glyph.value if self.discovered else Glyph.UNKNOWN.value
