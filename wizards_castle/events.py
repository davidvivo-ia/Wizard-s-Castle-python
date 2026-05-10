"""What happens when the player enters a special room."""

from __future__ import annotations

from typing import Callable

from .castle import Castle, Room, wrap
from .data import (
    ARMOR_COST,
    Armor,
    CASTLE_LEVELS,
    CASTLE_SIZE,
    Curse,
    Glyph,
    LAMP_COST,
    FLARE_COST,
    MONSTERS,
    Treasure,
    TREASURE_NAME,
    WEAPON_COST,
    Weapon,
)
from .player import Player
from .rng import GameRNG
from . import ui
from .combat import Combat


# ---------------------------------------------------------------------------
# Per-room handlers
# ---------------------------------------------------------------------------

def handle_room(player: Player, castle: Castle, room: Room, rng: GameRNG, *,
                input_fn: Callable[[str], str] = input) -> None:
    """Resolve the room the player just entered. Mutates player/room/castle."""

    if room.cleared:
        return

    g = room.glyph
    if g == Glyph.GOLD:
        amount = rng.d(10) + rng.d(10)
        player.gold += amount
        ui.good(f"You scoop up {amount} gold pieces.")
        room.cleared = True
        room.glyph = Glyph.EMPTY
    elif g == Glyph.FLARES:
        amount = rng.d(5) + 1
        player.flares += amount
        ui.good(f"You pocket {amount} flares.")
        room.cleared = True
        room.glyph = Glyph.EMPTY
    elif g == Glyph.SINKHOLE:
        ui.magic("The floor opens — you plunge to the level below!")
        x, y, z = player.position
        if z < CASTLE_LEVELS:
            player.position = (x, y, z + 1)
            castle.at(player.position).discovered = True
    elif g == Glyph.WARP:
        if player.position == castle.orb_of_zot_at and not player.has_orb_of_zot:
            ui.magic("Inside the warp you find the ORB OF ZOT!")
            player.has_orb_of_zot = True
            room.cleared = True
            room.glyph = Glyph.EMPTY
        else:
            new_pos = (rng.d(CASTLE_SIZE), rng.d(CASTLE_SIZE), rng.d(CASTLE_LEVELS))
            ui.magic("The warp twists reality — you are flung elsewhere!")
            player.position = new_pos
            castle.at(new_pos).discovered = True
    elif g == Glyph.MONSTER:
        _handle_monster(player, castle, room, rng, input_fn=input_fn)
    elif g == Glyph.TREASURE:
        t = Treasure(int(room.payload))
        player.treasures.add(t)
        ui.good(f"You pick up {TREASURE_NAME[t]}!")
        room.cleared = True
        room.glyph = Glyph.EMPTY
    elif g == Glyph.VENDOR:
        _handle_vendor(player, room, rng, input_fn=input_fn)
    elif g == Glyph.POOL:
        _handle_pool(player, rng, input_fn=input_fn)
    elif g == Glyph.CHEST:
        _handle_chest(player, room, rng, input_fn=input_fn)
    elif g == Glyph.BOOK:
        _handle_book(player, room, rng, input_fn=input_fn)
    elif g == Glyph.CRYSTAL_ORB:
        _handle_crystal_orb(player, castle, rng, input_fn=input_fn)


# ---------------------------------------------------------------------------
# Specific handlers
# ---------------------------------------------------------------------------

def _handle_monster(player: Player, castle: Castle, room: Room, rng: GameRNG,
                    *, input_fn: Callable[[str], str]) -> None:
    monster_idx = int(room.payload or 0)
    has_runestaff = (player.position == castle.runestaff_monster_at and not player.has_runestaff)
    fight = Combat(player, rng, monster_idx, monster_has_runestaff=has_runestaff,
                   input_fn=input_fn)
    outcome = fight.run()
    if outcome.monster_defeated or outcome.bribed:
        room.cleared = True
        room.glyph = Glyph.EMPTY


def _handle_pool(player: Player, rng: GameRNG, *,
                 input_fn: Callable[[str], str]) -> None:
    if ui.ask_choice("Drink from the pool?", ["Y", "N"], input_fn=input_fn) == "N":
        return
    roll = rng.d(8)
    if roll == 1:
        ui.bad("You feel weaker. (-1 STR)")
        player.adjust(strength=-1)
    elif roll == 2:
        ui.good("You feel stronger! (+1 STR)")
        player.adjust(strength=+1)
    elif roll == 3:
        ui.bad("You feel dimmer. (-1 INT)")
        player.adjust(intelligence=-1)
    elif roll == 4:
        ui.good("You feel cleverer! (+1 INT)")
        player.adjust(intelligence=+1)
    elif roll == 5:
        ui.bad("You feel clumsier. (-1 DEX)")
        player.adjust(dexterity=-1)
    elif roll == 6:
        ui.good("You feel nimbler! (+1 DEX)")
        player.adjust(dexterity=+1)
    elif roll == 7:
        # Change race
        from .data import Race
        new = rng.choice([r for r in Race if r != player.race])
        ui.magic(f"The pool transforms you into a {new.value}!")
        player.race = new
    else:
        from .data import Sex
        new_sex = Sex.FEMALE if player.sex == Sex.MALE else Sex.MALE
        ui.magic(f"The pool changes your sex — you are now {new_sex.value.lower()}.")
        player.sex = new_sex


def _handle_chest(player: Player, room: Room, rng: GameRNG, *,
                  input_fn: Callable[[str], str]) -> None:
    if ui.ask_choice("Open the chest?", ["Y", "N"], input_fn=input_fn) == "N":
        return
    roll = rng.d(3)
    if roll == 1:
        amount = rng.d(1000)
        player.gold += amount
        ui.good(f"The chest is full of gold! (+{amount} gp)")
    elif roll == 2:
        ui.bad("KABOOM! The chest explodes — you take damage.")
        player.take_damage(rng.d(6))
    else:
        ui.warn("A cloud of gas knocks you sideways — you stumble and lose a turn.")
        player.turn += 1
    room.cleared = True
    room.glyph = Glyph.EMPTY


def _handle_book(player: Player, room: Room, rng: GameRNG, *,
                 input_fn: Callable[[str], str]) -> None:
    if ui.ask_choice("Open the book?", ["Y", "N"], input_fn=input_fn) == "N":
        return
    roll = rng.d(6)
    if roll == 1:
        ui.magic("Flash! The book blinds you.")
        player.has_blindness = True
    elif roll == 2:
        ui.magic("The book teaches you the wisdom of the ancients! (+max INT)")
        player.intelligence = min(18, player.intelligence + 1)
        player.max_intelligence = max(player.max_intelligence, player.intelligence)
    elif roll == 3:
        ui.magic("The book teaches you new fighting forms! (+max DEX)")
        player.dexterity = min(18, player.dexterity + 1)
        player.max_dexterity = max(player.max_dexterity, player.dexterity)
    elif roll == 4:
        ui.magic("The book teaches you forgotten exercises! (+max STR)")
        player.strength = min(18, player.strength + 1)
        player.max_strength = max(player.max_strength, player.strength)
    elif roll == 5:
        ui.bad("The book sticks to your hands!")
        player.book_stuck = True
    else:
        ui.bad("The book bursts into flames in your face!")
        player.take_damage(rng.d(2))
    room.cleared = True
    room.glyph = Glyph.EMPTY


def _handle_crystal_orb(player: Player, castle: Castle, rng: GameRNG, *,
                        input_fn: Callable[[str], str]) -> None:
    if ui.ask_choice("Gaze into the crystal orb?", ["Y", "N"], input_fn=input_fn) == "N":
        return
    roll = rng.d(6)
    if roll == 1:
        ui.magic("You see yourself in a bloody heap.")
        player.take_damage(rng.d(2))
    elif roll == 2:
        ui.magic("You see a vivid image of an attacking monster... it strikes!")
        player.take_damage(1)
    elif roll == 3:
        # Reveal a random room on this level.
        z = player.position[2]
        x = rng.d(CASTLE_SIZE); y = rng.d(CASTLE_SIZE)
        room = castle.at((x, y, z))
        room.discovered = True
        ui.magic(f"You see {room.glyph.value} at ({x},{y}) on this level.")
    elif roll == 4:
        ui.magic("You see a soap opera rerun. Useless.")
    elif roll == 5:
        x, y, z = castle.orb_of_zot_at
        ui.magic(f"You see the Orb of Zot at level {z} ({x},{y}).")
    else:
        ui.bad("Your gaze is met by another's — and you are blinded.")
        player.has_blindness = True


# ---------------------------------------------------------------------------
# Vendor
# ---------------------------------------------------------------------------

def _handle_vendor(player: Player, room: Room, rng: GameRNG, *,
                   input_fn: Callable[[str], str]) -> None:
    ui.good("A vendor steps out of the shadows.")
    while True:
        opts = ["B", "S", "I", "L"]
        choice = ui.ask_choice(
            "(B)uy stats, (S)hop equipment, (I)gnore, (L)eave",
            opts, input_fn=input_fn,
        )
        if choice == "L" or choice == "I":
            return
        if choice == "B":
            _vendor_buy_stats(player, input_fn=input_fn)
        elif choice == "S":
            _vendor_shop(player, input_fn=input_fn)


def _vendor_buy_stats(player: Player, *, input_fn: Callable[[str], str]) -> None:
    cost = 1000
    if player.gold < cost:
        ui.warn(f"You need {cost} gp to buy stats from this vendor.")
        return
    stat = ui.ask_choice("Which stat? (S)trength, (I)nt, (D)ex",
                         ["S", "I", "D"], input_fn=input_fn)
    player.gold -= cost
    if stat == "S":
        player.strength = min(18, player.strength + 1)
        player.max_strength = max(player.max_strength, player.strength)
    elif stat == "I":
        player.intelligence = min(18, player.intelligence + 1)
        player.max_intelligence = max(player.max_intelligence, player.intelligence)
    else:
        player.dexterity = min(18, player.dexterity + 1)
        player.max_dexterity = max(player.max_dexterity, player.dexterity)
    ui.good("The vendor pockets the gold. Stat increased.")


def _vendor_shop(player: Player, *, input_fn: Callable[[str], str]) -> None:
    ui.info(f"You have {player.gold} gp.")
    # Armor
    for armor in (Armor.LEATHER, Armor.CHAINMAIL, Armor.PLATE):
        cost = ARMOR_COST[armor]
        if player.gold >= cost:
            if ui.ask_choice(f"Buy {armor.name.title()} armor for {cost} gp?",
                             ["Y", "N"], input_fn=input_fn) == "Y":
                player.gold -= cost
                player.armor = armor
                player.armor_damage = 0
                break
    # Weapons
    for weapon in (Weapon.DAGGER, Weapon.MACE, Weapon.SWORD):
        cost = WEAPON_COST[weapon]
        if player.gold >= cost:
            if ui.ask_choice(f"Buy a {weapon.name.title()} for {cost} gp?",
                             ["Y", "N"], input_fn=input_fn) == "Y":
                player.gold -= cost
                player.weapon = weapon
                break
    # Lamp
    if not player.has_lamp and player.gold >= LAMP_COST:
        if ui.ask_choice(f"Buy a lamp for {LAMP_COST} gp?", ["Y", "N"],
                         input_fn=input_fn) == "Y":
            player.gold -= LAMP_COST
            player.has_lamp = True
    # Flares
    if player.gold >= FLARE_COST:
        max_buy = min(player.gold, 20)
        raw = ui.ask(f"How many flares ({FLARE_COST} gp each, max {max_buy})?",
                     default="0", input_fn=input_fn)
        try:
            n = max(0, min(int(raw), max_buy))
        except ValueError:
            n = 0
        if n:
            player.gold -= n * FLARE_COST
            player.flares += n
            ui.good(f"You buy {n} flares.")
