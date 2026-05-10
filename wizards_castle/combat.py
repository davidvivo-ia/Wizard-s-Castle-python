"""Combat resolution.

Faithful to the 1980 turn structure: the player chooses Attack / Retreat /
Cast / Bribe, then (if the monster survives) the monster strikes back.
Web (random levels of paralysis), Fireball (1d7+1d7 damage) and
Deathspell (kills monster but with a chance of killing the caster) come
straight from the original.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .data import MONSTERS, MonsterStats, Treasure, Weapon
from .player import Player
from .rng import GameRNG
from . import ui


@dataclass
class CombatOutcome:
    monster_defeated: bool = False
    fled: bool = False
    bribed: bool = False
    player_dead: bool = False


class Combat:
    def __init__(self, player: Player, rng: GameRNG, monster_index: int,
                 *, monster_has_runestaff: bool, vendor: bool = False,
                 input_fn: Callable[[str], str] = input) -> None:
        self.player = player
        self.rng = rng
        self.monster_index = monster_index
        self.stats: MonsterStats = MONSTERS[monster_index]
        self.monster_hp = self.stats.hit_points
        self.web_turns = 0  # turns the monster is paralyzed
        self.has_runestaff = monster_has_runestaff
        self.vendor = vendor  # True when fighting an angry vendor
        self._input = input_fn

    # ---- Top-level loop ----------------------------------------------
    def run(self) -> CombatOutcome:
        outcome = CombatOutcome()
        ui.bad(f"You are facing a {self.stats.name}!")
        while self.monster_hp > 0 and self.player.is_alive:
            choice = self._prompt_action()
            if choice == "A":
                self._attack(outcome)
            elif choice == "R":
                if self._retreat():
                    outcome.fled = True
                    return outcome
            elif choice == "C":
                self._cast(outcome)
            elif choice == "B":
                if self._bribe():
                    outcome.bribed = True
                    return outcome
            if self.monster_hp <= 0:
                outcome.monster_defeated = True
                if self.has_runestaff:
                    ui.good("You found the Runestaff on the corpse!")
                    self.player.has_runestaff = True
                ui.good(f"The {self.stats.name} lies dead at your feet.")
                return outcome
            # Monster's turn
            if self.web_turns > 0:
                self.web_turns -= 1
                ui.info(f"The {self.stats.name} is webbed and cannot attack.")
            else:
                self._monster_attacks()
            if not self.player.is_alive:
                outcome.player_dead = True
                return outcome
        return outcome

    # ---- Actions -----------------------------------------------------
    def _prompt_action(self) -> str:
        opts = ["A", "R"]
        if self.player.intelligence >= 15:
            opts.append("C")
        if self.player.treasures:
            opts.append("B")
        return ui.ask_choice("(A)ttack, (R)etreat" + (
            ", (C)ast spell" if "C" in opts else "") + (
            ", (B)ribe" if "B" in opts else ""), opts, input_fn=self._input)

    def _attack(self, outcome: CombatOutcome) -> None:
        if self.player.weapon == Weapon.NONE:
            ui.warn("You have no weapon to attack with!")
            return
        if self.player.book_stuck:
            ui.warn("You can't attack — the book is stuck to your hands!")
            return
        if self.rng.d(20) <= self.player.dexterity:
            dmg = self.player.weapon_damage
            self.monster_hp -= dmg
            ui.good(f"You hit the {self.stats.name} for {dmg} damage.")
            # Weapons may break on tough foes (Gargoyle/Dragon-class).
            if self.stats.hit_points >= 8 and self.rng.chance(1, 8):
                ui.bad("Your weapon shatters from the blow!")
                self.player.break_weapon()
        else:
            ui.warn(f"You miss the {self.stats.name}.")

    def _retreat(self) -> bool:
        ui.info("You turn to flee...")
        if self.rng.d(20) <= self.player.dexterity:
            ui.good("...and escape!")
            return True
        ui.bad("...but the monster catches you!")
        self._monster_attacks()
        return False

    def _bribe(self) -> bool:
        if not self.player.treasures:
            ui.warn("You have nothing to offer.")
            return False
        offering = self.rng.choice(sorted(self.player.treasures, key=int))
        ui.info(f"The {self.stats.name} eyes {offering.name.replace('_', ' ').title()}...")
        if self.rng.coin():
            self.player.treasures.discard(offering)
            ui.good("Bribe accepted. The monster departs.")
            return True
        ui.bad("Bribe refused!")
        return False

    def _cast(self, outcome: CombatOutcome) -> None:
        spells = ["W", "F"]
        if self.player.intelligence >= 15:
            spells.append("D")
        choice = ui.ask_choice("(W)eb, (F)ireball, (D)eathspell", spells,
                                input_fn=self._input)
        if choice == "W":
            self.player.adjust(strength=-1)
            self.web_turns = self.rng.d(2) + 1
            ui.magic(f"A web ensnares the {self.stats.name} for {self.web_turns} turns.")
        elif choice == "F":
            self.player.adjust(strength=-1, intelligence=-1)
            dmg = self.rng.d(7) + self.rng.d(7)
            self.monster_hp -= dmg
            ui.magic(f"Fireball hits for {dmg} damage!")
        elif choice == "D":
            self.player.adjust(intelligence=-1)
            if self.player.intelligence < self.rng.randint(1, 18):
                ui.bad("The deathspell rebounds! You die.")
                self.player.adjust(strength=-self.player.strength)
                outcome.player_dead = True
            else:
                self.monster_hp = 0
                ui.magic("Deathspell succeeds — the monster crumples to dust!")

    # ---- Monster's turn ----------------------------------------------
    def _monster_attacks(self) -> None:
        if self.rng.d(20) > self.player.dexterity:
            ui.info(f"The {self.stats.name} swings and misses.")
            return
        dmg = self.stats.damage
        applied = self.player.take_damage(dmg)
        ui.bad(f"The {self.stats.name} hits you! "
               f"({dmg} dmg, {applied} got through your armour)")
        if self.stats.can_drain and self.rng.chance(1, 3):
            ui.bad("The vampire drains your strength permanently!")
            self.player.max_strength = max(1, self.player.max_strength - 1)
            self.player.strength = min(self.player.strength, self.player.max_strength)
