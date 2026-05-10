"""Modern Python port of Joseph R. Power's 1980 BASIC game *The Wizard's Castle*.

The package faithfully reproduces the original mechanics (8x8x8 castle, four
races, thirteen monsters, eight treasures, runestaff, Orb of Zot, curses,
vendor) while bringing the codebase up to 2026 standards: type hints,
dataclasses, enums, deterministic seedable RNG, JSON save/load, ANSI colour
output and a full pytest suite.

The two reference texts used while porting are MaiZure's annotated decoding
of the original BASIC (http://maizure.org/projects/decoded-the-wizards-castle/)
and the source listings preserved at the IF Archive
(https://www.ifarchive.org/indexes/if-archive/games/source/basic/).
"""

from .game import Game

__all__ = ["Game", "__version__"]
__version__ = "1.0.0"
