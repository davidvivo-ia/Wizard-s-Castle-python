"""Top-level game loop: character creation, command parser, win/lose check."""

from __future__ import annotations

import argparse
import secrets
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from . import ui
from .castle import Castle, generate_castle, step, wrap
from .data import (
    ARMOR_COST,
    Armor,
    CASTLE_LEVELS,
    CASTLE_SIZE,
    Curse,
    CURSE_TREASURE,
    FLARE_COST,
    Glyph,
    HELP_TEXT,
    INTRO_BANNER,
    LAMP_COST,
    RACE_STATS,
    Race,
    Sex,
    START_GOLD,
    TREASURE_NAME,
    Treasure,
    WEAPON_COST,
    Weapon,
)
from .events import handle_room
from .player import Player
from .rng import GameRNG
from .save import load_from_path, save_to_path


SAVE_PATH = Path("wizards_castle.save.json")


# ---------------------------------------------------------------------------
# Character creation
# ---------------------------------------------------------------------------

def create_character(rng: GameRNG, *, input_fn: Callable[[str], str] = input) -> Player:
    ui.banner(INTRO_BANNER)
    name = ui.ask("What is thy name, brave adventurer?", default="Sir Nameless",
                  input_fn=input_fn)
    race_letter = ui.ask_choice("Choose your race: (H)obbit, (E)lf, h(U)man, (D)warf",
                                ["H", "E", "U", "D"], input_fn=input_fn)
    race = {"H": Race.HOBBIT, "E": Race.ELF, "U": Race.HUMAN, "D": Race.DWARF}[race_letter]
    sex_letter = ui.ask_choice("Sex: (M)ale, (F)emale", ["M", "F"], input_fn=input_fn)
    sex = Sex.MALE if sex_letter == "M" else Sex.FEMALE

    player = Player.from_race(name, race, sex)
    player.gold = START_GOLD

    bonus = RACE_STATS[race].bonus_points
    ui.info(f"\nYou have {bonus} bonus points to distribute among STR, INT and DEX.")
    while bonus > 0:
        ui.info(f"  STR {player.strength}  INT {player.intelligence}  "
                f"DEX {player.dexterity}  ({bonus} left)")
        which = ui.ask_choice("Add to (S)trength, (I)ntelligence or (D)exterity",
                              ["S", "I", "D"], input_fn=input_fn)
        if which == "S":
            player.adjust(strength=+1)
        elif which == "I":
            player.adjust(intelligence=+1)
        else:
            player.adjust(dexterity=+1)
        bonus -= 1

    # Initial purchases.
    ui.info(f"\nYou have {player.gold} gp. Time to buy gear.")
    if player.gold >= ARMOR_COST[Armor.LEATHER]:
        for armor in (Armor.LEATHER, Armor.CHAINMAIL, Armor.PLATE):
            if player.gold >= ARMOR_COST[armor]:
                if ui.ask_choice(
                    f"Buy {armor.name.title()} armor for {ARMOR_COST[armor]} gp?",
                    ["Y", "N"], input_fn=input_fn,
                ) == "Y":
                    player.gold -= ARMOR_COST[armor]
                    player.armor = armor
                    break
    for weapon in (Weapon.DAGGER, Weapon.MACE, Weapon.SWORD):
        if player.gold >= WEAPON_COST[weapon]:
            if ui.ask_choice(
                f"Buy a {weapon.name.title()} for {WEAPON_COST[weapon]} gp?",
                ["Y", "N"], input_fn=input_fn,
            ) == "Y":
                player.gold -= WEAPON_COST[weapon]
                player.weapon = weapon
                break
    if player.gold >= LAMP_COST and ui.ask_choice(
        f"Buy a lamp for {LAMP_COST} gp?", ["Y", "N"], input_fn=input_fn) == "Y":
        player.gold -= LAMP_COST
        player.has_lamp = True
    if player.gold:
        raw = ui.ask(f"Buy flares ({FLARE_COST} gp each, you have {player.gold} gp)?",
                     default="0", input_fn=input_fn)
        try:
            n = max(0, min(int(raw), player.gold))
        except ValueError:
            n = 0
        player.gold -= n
        player.flares += n

    return player


# ---------------------------------------------------------------------------
# Game class
# ---------------------------------------------------------------------------

@dataclass
class Game:
    player: Player
    castle: Castle
    rng: GameRNG
    seed: int | None
    classic_mode: bool = False  # restrict commands to original BASIC keys
    input_fn: Callable[[str], str] = input

    @classmethod
    def new(cls, *, seed: int | None = None,
            input_fn: Callable[[str], str] = input,
            classic_mode: bool = False) -> "Game":
        rng = GameRNG(seed)
        player = create_character(rng, input_fn=input_fn)
        castle = generate_castle(rng)
        player.position = castle.entrance
        castle.at(player.position).discovered = True
        return cls(player=player, castle=castle, rng=rng, seed=seed,
                   classic_mode=classic_mode, input_fn=input_fn)

    @classmethod
    def load(cls, path: Path, *, input_fn: Callable[[str], str] = input,
             classic_mode: bool = False) -> "Game":
        player, castle, seed = load_from_path(path)
        rng = GameRNG(seed)
        return cls(player=player, castle=castle, rng=rng, seed=seed,
                   classic_mode=classic_mode, input_fn=input_fn)

    # -------------------------------------------------------------- run
    def run(self) -> None:
        ui.good("\nThe iron portcullis slams behind you. Welcome to the castle.\n")
        while self.player.is_alive:
            self._describe_room()
            if self._check_win():
                return
            cmd = self._prompt_command()
            self._execute(cmd)
            self._end_of_turn()
        ui.bad("\nYou have died in the castle. The Wizard cackles in the dark.")

    # --------------------------------------------------------- describe
    def _describe_room(self) -> None:
        room = self.castle.at(self.player.position)
        room.discovered = True
        x, y, z = self.player.position
        if self.player.has_blindness:
            ui.warn(f"[blind] You are at ({x},{y}) on level {z}.")
            return
        ui.info(f"\n— Level {z}, ({x},{y}) — you see {self._describe(room)}.")
        # Resolve room contents (combat/treasure/event).
        handle_room(self.player, self.castle, room, self.rng,
                    input_fn=self.input_fn)

    def _describe(self, room) -> str:
        from .data import GLYPH_DESCRIPTION
        return GLYPH_DESCRIPTION.get(room.glyph, "something")

    # ------------------------------------------------------------ input
    def _prompt_command(self) -> str:
        raw = ui.ask("Command (H for help)", default="H", input_fn=self.input_fn).upper()
        return raw[:1] if raw else "H"

    # ------------------------------------------------------------ exec
    def _execute(self, cmd: str) -> None:
        if cmd in ("N", "S", "E", "W"):
            self._move(cmd)
        elif cmd == "U":
            self._stairs(up=True)
        elif cmd == "D":
            self._stairs(up=False)
        elif cmd == "M":
            print(ui.render_level(self.castle, self.player, self.player.position[2]))
        elif cmd == "F":
            self._light_flare()
        elif cmd == "L":
            self._lamp()
        elif cmd == "G":
            self._gaze()
        elif cmd == "O":
            self._open()
        elif cmd == "T":
            self._drink()
        elif cmd == "R":
            self._read_runestaff()
        elif cmd == "I":
            ui.show_status(self.player)
        elif cmd == "?" or cmd == "H":
            print(HELP_TEXT)
        elif cmd == "Q":
            if ui.ask_choice("Really quit?", ["Y", "N"], input_fn=self.input_fn) == "Y":
                ui.warn("You flee the castle. The Wizard sneers.")
                # Force exit by killing the player.
                self.player.strength = 0
        elif cmd == "$":  # cheat code: full reveal (debug)
            for c in self.castle.all_coords():
                self.castle.at(c).discovered = True
        else:
            # Save command spelled out: "S" already used for South.
            if cmd == "V":
                save_to_path(SAVE_PATH, self.player, self.castle, self.seed)
                ui.good(f"Game saved to {SAVE_PATH}.")
            else:
                ui.warn(f"Unknown command: {cmd!r}. Type H for help.")

    # --------------------------------------------------------- movement
    def _move(self, direction: str) -> None:
        self.player.position = step(self.player.position, direction)
        self.castle.at(self.player.position).discovered = True

    def _stairs(self, *, up: bool) -> None:
        room = self.castle.at(self.player.position)
        want = Glyph.STAIRS_UP if up else Glyph.STAIRS_DOWN
        if room.glyph != want:
            ui.warn(f"There are no stairs going {'up' if up else 'down'} here.")
            return
        x, y, z = self.player.position
        new_z = z - 1 if up else z + 1
        if 1 <= new_z <= CASTLE_LEVELS:
            self.player.position = (x, y, new_z)
            self.castle.at(self.player.position).discovered = True

    def _light_flare(self) -> None:
        if self.player.flares <= 0:
            ui.warn("You have no flares.")
            return
        self.player.flares -= 1
        x, y, z = self.player.position
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                c = wrap((x + dx, y + dy, z))
                self.castle.at(c).discovered = True
        print(ui.render_level(self.castle, self.player, z))

    def _lamp(self) -> None:
        if not self.player.has_lamp:
            ui.warn("You have no lamp.")
            return
        d = ui.ask_choice("Shine which way?", ["N", "S", "E", "W"],
                          input_fn=self.input_fn)
        x, y, z = self.player.position
        for i in range(1, 4):
            c = step((x, y, z), d)
            self.castle.at(c).discovered = True
            x, y, _ = c
        print(ui.render_level(self.castle, self.player, z))

    # ------------------------------------------------------------ misc
    def _gaze(self) -> None:
        room = self.castle.at(self.player.position)
        if room.glyph == Glyph.CRYSTAL_ORB:
            handle_room(self.player, self.castle, room, self.rng,
                        input_fn=self.input_fn)
        else:
            ui.warn("There is no crystal orb here.")

    def _open(self) -> None:
        room = self.castle.at(self.player.position)
        if room.glyph in (Glyph.CHEST, Glyph.BOOK):
            handle_room(self.player, self.castle, room, self.rng,
                        input_fn=self.input_fn)
        else:
            ui.warn("Nothing here to open.")

    def _drink(self) -> None:
        room = self.castle.at(self.player.position)
        if room.glyph == Glyph.POOL:
            handle_room(self.player, self.castle, room, self.rng,
                        input_fn=self.input_fn)
        else:
            ui.warn("There is no pool here.")

    def _read_runestaff(self) -> None:
        if not self.player.has_runestaff:
            ui.warn("You have no runestaff to read.")
            return
        try:
            x = int(ui.ask("Teleport to X (1-8)", input_fn=self.input_fn))
            y = int(ui.ask("Teleport to Y (1-8)", input_fn=self.input_fn))
            z = int(ui.ask("Teleport to Z (1-8)", input_fn=self.input_fn))
        except ValueError:
            ui.warn("Bad coordinates.")
            return
        if not (1 <= x <= CASTLE_SIZE and 1 <= y <= CASTLE_SIZE
                and 1 <= z <= CASTLE_LEVELS):
            ui.warn("Out of range.")
            return
        self.player.position = (x, y, z)
        self.castle.at(self.player.position).discovered = True
        ui.magic("The Runestaff hums and the world flickers around you.")

    # ---------------------------------------------------- end of turn
    def _end_of_turn(self) -> None:
        self.player.turn += 1
        # Curse pickups: enter a room of a cursed level => acquire it
        x, y, z = self.player.position
        # In Power's BASIC, curses are pre-placed at random rooms; we simulate
        # by giving a small chance per level if the player lacks the warding
        # treasure. Cheap, faithful in spirit.
        for curse, treasure in CURSE_TREASURE.items():
            if curse in self.player.curses:
                continue
            if self.player.has_treasure(treasure):
                continue
            if self.rng.chance(1, 200):
                self.player.curses.add(curse)
                ui.bad(f"You feel a sudden chill — the curse of "
                       f"{curse.name.lower()} has taken hold.")
        # Apply curse effects.
        if Curse.LEECH in self.player.curses and not self.player.has_treasure(
                CURSE_TREASURE[Curse.LEECH]):
            stolen = self.rng.d(5)
            taken = min(self.player.gold, stolen)
            if taken:
                self.player.gold -= taken
                ui.warn(f"The Leech siphons {taken} gp from your pouch.")
        if Curse.FORGETFULNESS in self.player.curses and not self.player.has_treasure(
                CURSE_TREASURE[Curse.FORGETFULNESS]):
            if self.rng.chance(1, 4):
                forget = self.castle.at(
                    (self.rng.d(CASTLE_SIZE), self.rng.d(CASTLE_SIZE), z))
                forget.discovered = False
        if self.player.has_blindness and self.player.has_treasure(Treasure.OPAL_EYE):
            self.player.has_blindness = False
            ui.good("The Opal Eye restores your sight!")
        if self.player.book_stuck and self.player.has_treasure(Treasure.BLUE_FLAME):
            self.player.book_stuck = False
            ui.good("The Blue Flame burns the cursed book from your hands!")

    # --------------------------------------------------------- victory
    def _check_win(self) -> bool:
        if (self.player.has_orb_of_zot
                and self.player.position == self.castle.entrance):
            ui.good("\nYou stride through the entrance with the ORB OF ZOT held aloft!")
            ui.good("The Wizard is vanquished. You are a hero of the realm.")
            ui.show_status(self.player)
            # Force exit.
            self.player.strength = 0  # ends the loop next iter
            return True
        return False


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="wizards-castle",
        description="A modern Python port of Joseph R. Power's 1980 game.",
    )
    p.add_argument("--seed", type=int, default=None,
                   help="Deterministic seed for the RNG.")
    p.add_argument("--load", type=Path, default=None,
                   help="Load a saved game from this JSON file.")
    p.add_argument("--classic", action="store_true",
                   help="Restrict commands to the original BASIC keys.")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.load:
        game = Game.load(args.load, classic_mode=args.classic)
    else:
        seed = args.seed if args.seed is not None else secrets.randbits(32)
        game = Game.new(seed=seed, classic_mode=args.classic)
        ui.info(f"(seed={seed} — pass --seed {seed} to replay this castle)")
    try:
        game.run()
    except (KeyboardInterrupt, EOFError):
        ui.warn("\nInterrupted. Farewell.")
        return 130
    return 0
