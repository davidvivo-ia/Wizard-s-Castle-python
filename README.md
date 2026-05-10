# Wizard's Castle (Python 2026 edition)

A modern Python port of **The Wizard's Castle** (Joseph R. Power, 1980), one of
the earliest BASIC roguelikes. Faithful to the 1980 source while bringing the
codebase up to 2026 standards.

```text
   __        ___                  _ _      ____           _   _
   \ \      / (_)______ _ _ __ __| ( )___ / ___|__ _ ___| |_| | ___
    \ \ /\ / /| |_  / _` | '__/ _` |// __| |   / _` / __| __| |/ _ \
     \ V  V / | |/ / (_| | | | (_| | \__ \ |__| (_| \__ \ |_| |  __/
      \_/\_/  |_/___\__,_|_|  \__,_| |___/\____\__,_|___/\__|_|\___|
```

## Quick start

```bash
pip install -e .
wizards-castle              # new game with a random seed
wizards-castle --seed 2026  # deterministic castle
wizards-castle --load my.save.json
```

Or without installing:

```bash
python -m wizards_castle
```

## What's in the box

- The full 8 × 8 × 8 toroidal castle with all the original room types
  (entrance, stairs up/down, magic pool, chest, gold pile, flares, warp,
  sinkhole, crystal orb, book, monster, vendor, treasure).
- 4 races (Hobbit, Elf, Human, Dwarf), 2 sexes, attribute distribution and
  starting purchases exactly as in the BASIC listing.
- 13 monsters with their original HP/damage values, including the Vampire's
  permanent strength drain.
- 8 treasures, the Runestaff (hidden in a random monster) and the Orb of Zot
  (hidden in a random warp on level 2-8).
- Combat menu: Attack / Retreat / Cast Web / Fireball / Deathspell / Bribe.
- Vendor shopping plus the +1 stat purchase for 1000 gp.
- Curses (Lethargy, Leech, Forgetfulness) and their warding treasures.
- Save/load to JSON.
- Map command with ANSI colour, lamp / flare reveal, crystal-orb visions.

## What got modernised

| Original BASIC                              | This port                                   |
| ------------------------------------------- | ------------------------------------------- |
| `GOTO`/`GOSUB` spaghetti                    | Modules with type hints and dataclasses     |
| `RND` bug (small period, biased)            | Stdlib `random.Random` with optional `--seed` |
| Single 80-column ALL CAPS UI                | ANSI colour, gracefully degrading to plain  |
| No way to save                              | JSON `save_to_path` / `load_from_path`      |
| No tests                                    | `pytest` suite (18 tests) covering map,    |
|                                             | player, combat and save round-trip          |
| Hardcoded English strings inline            | Centralised in `wizards_castle/data.py`     |

## Running the tests

```bash
pip install -e ".[dev]"
pytest -q
```

## Code map

```
wizards_castle/
├── __init__.py        package metadata
├── __main__.py        `python -m wizards_castle`
├── data.py            constants: races, monsters, treasures, glyphs
├── rng.py             seedable RNG wrapper
├── castle.py          map generation, Room, Coord helpers
├── player.py          Player dataclass: stats, inventory, curses
├── combat.py          combat resolver, spells, retreat, bribe
├── events.py          per-room handlers (pool, chest, vendor, …)
├── ui.py              ANSI colour, prompts, ASCII map renderer
├── save.py            JSON save/load
└── game.py            character creation, command parser, main loop

tests/                 pytest suite
```

## References used while porting

- *Decoded: The Wizard's Castle* by MaiZure — line-by-line annotated original
  BASIC: <http://maizure.org/projects/decoded-the-wizards-castle/>
- IF Archive BASIC source mirror:
  <https://www.ifarchive.org/indexes/if-archive/games/source/basic/>
- Internet Archive listing scan: <https://archive.org/details/TheWizardsCastle_1020>
- MyAbandonware notes on the original `RND` bug:
  <https://www.myabandonware.com/game/the-wizard-s-castle-1no>
- Jason Brian Hall's modern C reimplementation (cross-reference):
  <https://github.com/jasonbrianhall/wizardscastle>
- CRPG Addict review for design context:
  <https://crpgaddict.blogspot.com/2013/02/game-90-wizards-castle-1980.html>

## Licence

MIT — see [`LICENSE`](LICENSE).

## Credits

- **1980 original**: Joseph R. Power, in Microsoft BASIC.
- **2026 port**: this repository.
