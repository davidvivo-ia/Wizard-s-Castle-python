"""GameState: aglutina jugador + castillo + flags globales."""

from __future__ import annotations

from dataclasses import dataclass, replace

from wizards_castle.domain.castle import Castle
from wizards_castle.domain.player import Player


@dataclass(frozen=True, slots=True)
class GameState:
    """El estado completo del juego en un instante dado."""

    player: Player
    castle: Castle
    seed: int | None = None
    classic_mode: bool = False
    vendor_hostile: bool = False  # VF del original (línea 3620)

    def with_player(self, player: Player) -> GameState:
        """Devuelve un estado nuevo con `player` reemplazando al actual."""
        return replace(self, player=player)

    def with_castle(self, castle: Castle) -> GameState:
        """Devuelve un estado nuevo con `castle` reemplazando al actual."""
        return replace(self, castle=castle)

    def with_vendor_hostile(self, value: bool = True) -> GameState:
        """Marca a los vendedores como hostiles (atacaste a uno)."""
        return replace(self, vendor_hostile=value)

    @property
    def is_won(self) -> bool:
        """`True` si el jugador ha salido por la entrada con el Orb of Zot."""
        return self.player.has_orb_of_zot and self.player.position == self.castle.entrance

    @property
    def is_lost(self) -> bool:
        """`True` si el jugador está muerto."""
        return not self.player.is_alive

    @property
    def is_finished(self) -> bool:
        """`True` si la partida ha terminado por victoria o derrota."""
        return self.is_won or self.is_lost
