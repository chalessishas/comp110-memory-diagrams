"""Boss enemy definitions for all acts in Slay the Spire."""
import random
from slay_the_spire.enemy import Enemy, Intent, IntentType, random_hp
from slay_the_spire.effect import (
    Strength, Vulnerable, Weak, Frail, Metallicize, Artifact,
    Intangible, Invincible, Beat_of_Death, Curiosity,
    Effect, EffectType,
)


# =============================================================================
# ACT 1 BOSSES
# =============================================================================


class LargeSlime(Enemy):
    """Spawned when Slime Boss splits at half HP."""

    def __init__(self, hp):
        super().__init__("Large Slime", hp, hp)
        self.is_minion = True

    def choose_intent(self, combat):
        last = self.move_history[-1] if self.move_history else None
        if last == "slam":
            self.intent = Intent(IntentType.DEBUFF, description="Goop Spray")
        else:
            self.intent = Intent(IntentType.ATTACK, damage=16, description="Slam")

    def take_turn(self, combat):
        desc = self.intent.description or ""
        if desc == "Slam":
            dmg = self.get_attack_damage(16)
            combat.deal_damage_to_player(dmg, self)
            print(f"  {self.name} slams for {dmg} damage!")
            self.move_history.append("slam")
        else:
            from slay_the_spire.card import create_card
            for _ in range(2):
                try:
                    slimed = create_card("slimed")
                    combat.player.discard_pile.append(slimed)
                except Exception:
                    pass
            print(f"  {self.name} sprays goop! 2 Slimed added to discard pile!")
            self.move_history.append("goop")


class SlimeBoss(Enemy):
    """Act 1 Boss (HP 140). Goop Spray, Slam (35 dmg), Preparing.
    Splits into 2 Large Slimes at half HP.
    """

    def __init__(self):
        super().__init__("Slime Boss", 140)
        self.has_split = False

    def choose_intent(self, combat):
        last = self.move_history[-1] if self.move_history else None
        if last == "preparing":
            self.intent = Intent(IntentType.ATTACK, damage=35, description="Slam")
        elif last == "slam":
            self.intent = Intent(IntentType.DEBUFF, description="Goop Spray")
        else:
            self.intent = Intent(IntentType.STRATEGIC, description="Preparing")

    def take_turn(self, combat):
        desc = self.intent.description or ""
        if desc == "Preparing":
            print(f"  {self.name} is preparing...")
            self.move_history.append("preparing")
        elif desc == "Slam":
            dmg = self.get_attack_damage(35)
            combat.deal_damage_to_player(dmg, self)
            print(f"  {self.name} slams for {dmg} damage!")
            self.move_history.append("slam")
        elif desc == "Goop Spray":
            from slay_the_spire.card import create_card
            for _ in range(3):
                try:
                    slimed = create_card("slimed")
                    combat.player.discard_pile.append(slimed)
                except Exception:
                    pass
            print(f"  {self.name} sprays goop! 3 Slimed added to discard pile!")
            self.move_history.append("goop")

    def take_damage(self, amount, combat=None):
        actual = super().take_damage(amount, combat)
        if not self.has_split and self.hp <= self.max_hp // 2 and self.is_alive:
            self._split(combat)
        return actual

    def _split(self, combat):
        """Split into 2 Large Slimes."""
        self.has_split = True
        split_hp = max(1, self.hp if self.hp > 0 else self.max_hp // 2)
        self.is_alive = False
        self.hp = 0
        if combat:
            s1 = LargeSlime(split_hp)
            s2 = LargeSlime(split_hp)
            combat.enemies.append(s1)
            combat.enemies.append(s2)
            s1.choose_intent(combat)
            s2.choose_intent(combat)
            print(f"  {self.name} SPLITS into two Large Slimes!")

    def on_death(self, combat=None):
        if not self.has_split and combat:
            self._split(combat)
        else:
            super().on_death(combat)


class TheGuardian(Enemy):
    """Act 1 Boss (HP 240). Two modes: Offensive and Defensive.
    Mode shifts at 30 HP damage threshold.
    Offensive: Twin Slam (32), Fierce Bash (32 + 2 Vuln), Whirlwind (5x4).
    Defensive: gains 20 Block + Sharp Hide (3 dmg when attacked), Roll Attack.
    """

    def __init__(self):
        super().__init__("The Guardian", 240)
        self.mode = "offensive"  # "offensive" or "defensive"
        self.mode_shift_threshold = 30
        self.damage_taken_this_mode = 0

    def take_damage(self, amount, combat=None):
        actual = super().take_damage(amount, combat)
        if self.mode == "offensive" and actual > 0:
            self.damage_taken_this_mode += actual
            if self.damage_taken_this_mode >= self.mode_shift_threshold:
                self._shift_to_defensive()
        return actual

    def _shift_to_defensive(self):
        self.mode = "defensive"
        self.damage_taken_this_mode = 0
        self.gain_block(20)
        from slay_the_spire.effect import Sharp_Hide
        self.effects.add(Sharp_Hide(3))
        print(f"  {self.name} shifts to DEFENSIVE mode! Gains 20 Block and Sharp Hide!")

    def _shift_to_offensive(self):
        self.mode = "offensive"
        self.damage_taken_this_mode = 0
        self.effects.remove("Sharp Hide")
        print(f"  {self.name} shifts to OFFENSIVE mode!")

    def choose_intent(self, combat):
        if self.mode == "defensive":
            last = self.move_history[-1] if self.move_history else None
            if last == "defensive_stance":
                self._shift_to_offensive()
                self.intent = Intent(IntentType.ATTACK, damage=32, description="Twin Slam")
            else:
                self.intent = Intent(
                    IntentType.ATTACK_DEFEND, damage=9, block=20,
                    description="Roll Attack",
                )
                self.move_history.append("defensive_stance")
                return
        # Offensive mode
        last = self.move_history[-1] if self.move_history else None
        roll = random.random()
        if last != "fierce_bash" and roll < 0.30:
            self.intent = Intent(
                IntentType.ATTACK_DEBUFF, damage=32,
                description="Fierce Bash",
            )
        elif roll < 0.60:
            self.intent = Intent(
                IntentType.ATTACK, damage=5, hits=4,
                description="Whirlwind",
            )
        else:
            self.intent = Intent(IntentType.ATTACK, damage=32, description="Twin Slam")

    def take_turn(self, combat):
        desc = self.intent.description or ""
        if desc == "Twin Slam":
            dmg = self.get_attack_damage(32)
            combat.deal_damage_to_player(dmg, self)
            print(f"  {self.name} Twin Slam for {dmg} damage!")
            self.move_history.append("twin_slam")
        elif desc == "Fierce Bash":
            dmg = self.get_attack_damage(32)
            combat.deal_damage_to_player(dmg, self)
            combat.apply_effect_to_player("Vulnerable", 2)
            print(f"  {self.name} Fierce Bash for {dmg} damage! Applies 2 Vulnerable!")
            self.move_history.append("fierce_bash")
        elif desc == "Whirlwind":
            dmg = self.get_attack_damage(5)
            for _ in range(4):
                combat.deal_damage_to_player(dmg, self)
            print(f"  {self.name} Whirlwind for {dmg}x4 damage!")
            self.move_history.append("whirlwind")
        elif desc == "Roll Attack":
            self.gain_block(20)
            dmg = self.get_attack_damage(9)
            combat.deal_damage_to_player(dmg, self)
            print(f"  {self.name} gains 20 Block and Roll Attacks for {dmg} damage!")
            self.move_history.append("roll_attack")


class Hexaghost(Enemy):
    """Act 1 Boss (HP 250). Six ghostly flames.
    Activate, Divider (hp/12+1 x6), Sear (6 + Burn),
    Inferno (2x6 + Burns), Tackle (5x2).
    """

    def __init__(self):
        super().__init__("Hexaghost", 250)
        self.activated = False
        self.divider_done = False

    def choose_intent(self, combat):
        if self.turn == 0:
            self.intent = Intent(IntentType.STRATEGIC, description="Activate")
        elif not self.divider_done:
            # Divider: player_hp / 12 + 1, x6
            player_hp = combat.player.hp if combat else 80
            div_dmg = player_hp // 12 + 1
            self.intent = Intent(
                IntentType.ATTACK, damage=div_dmg, hits=6,
                description="Divider",
            )
        else:
            # Cycle: Sear, Tackle, Sear, Inferno, repeat
            cycle_pos = (self.turn - 2) % 4
            if cycle_pos == 0 or cycle_pos == 2:
                self.intent = Intent(
                    IntentType.ATTACK_DEBUFF, damage=6,
                    description="Sear",
                )
            elif cycle_pos == 1:
                self.intent = Intent(
                    IntentType.ATTACK, damage=5, hits=2,
                    description="Tackle",
                )
            else:
                self.intent = Intent(
                    IntentType.ATTACK, damage=2, hits=6,
                    description="Inferno",
                )

    def take_turn(self, combat):
        desc = self.intent.description or ""
        if desc == "Activate":
            self.activated = True
            print(f"  {self.name} activates 6 ghostly flames!")
            self.move_history.append("activate")
        elif desc == "Divider":
            dmg = self.get_attack_damage(self.intent.damage)
            for _ in range(6):
                combat.deal_damage_to_player(dmg, self)
            print(f"  {self.name} Divider for {dmg}x6 damage!")
            self.divider_done = True
            self.move_history.append("divider")
        elif desc == "Sear":
            dmg = self.get_attack_damage(6)
            combat.deal_damage_to_player(dmg, self)
            from slay_the_spire.card import create_card
            try:
                burn = create_card("burn")
                combat.player.discard_pile.append(burn)
            except Exception:
                pass
            print(f"  {self.name} sears for {dmg} damage! A Burn is added to your discard pile!")
            self.move_history.append("sear")
        elif desc == "Tackle":
            dmg = self.get_attack_damage(5)
            for _ in range(2):
                combat.deal_damage_to_player(dmg, self)
            print(f"  {self.name} tackles for {dmg}x2 damage!")
            self.move_history.append("tackle")
        elif desc == "Inferno":
            dmg = self.get_attack_damage(2)
            for _ in range(6):
                combat.deal_damage_to_player(dmg, self)
            from slay_the_spire.card import create_card
            for _ in range(3):
                try:
                    burn = create_card("burn")
                    combat.player.discard_pile.append(burn)
                except Exception:
                    pass
            print(f"  {self.name} Inferno for {dmg}x6 damage! 3 Burns added to discard pile!")
            self.move_history.append("inferno")


# =============================================================================
# ACT 2 BOSSES
# =============================================================================


class TheChamp(Enemy):
    """Act 2 Boss (HP 420). Two phases.
    Phase 1: Execute, Heavy Slash, Defensive Stance.
    At half HP: enrages (removes debuffs, gains Str + Metallicize).
    Phase 2: more aggressive attacks.
    """

    def __init__(self):
        super().__init__("The Champ", 420)
        self.phase = 1
        self.enraged = False

    def take_damage(self, amount, combat=None):
        actual = super().take_damage(amount, combat)
        if not self.enraged and self.hp <= self.max_hp // 2 and self.is_alive:
            self._enrage()
        return actual

    def _enrage(self):
        self.enraged = True
        self.phase = 2
        # Remove all debuffs
        debuff_names = list(self.effects.get_debuffs().keys())
        for name in debuff_names:
            self.effects.remove(name)
        self.effects.add(Strength(5))
        self.effects.add(Metallicize(5))
        print(f"  {self.name} ENRAGES! Removes all debuffs, gains 5 Strength and 5 Metallicize!")

    def choose_intent(self, combat):
        if self.phase == 1:
            last = self.move_history[-1] if self.move_history else None
            roll = random.random()
            if last == "defensive":
                self.intent = Intent(IntentType.ATTACK, damage=22, description="Heavy Slash")
            elif roll < 0.30:
                self.intent = Intent(
                    IntentType.DEFEND, block=15,
                    description="Defensive Stance",
                )
            elif roll < 0.60:
                self.intent = Intent(IntentType.ATTACK, damage=22, description="Heavy Slash")
            else:
                self.intent = Intent(
                    IntentType.ATTACK_DEBUFF, damage=10, hits=2,
                    description="Execute",
                )
        else:
            # Phase 2: more aggressive
            last = self.move_history[-1] if self.move_history else None
            roll = random.random()
            if last != "face_slap" and roll < 0.35:
                self.intent = Intent(
                    IntentType.ATTACK_DEBUFF, damage=12,
                    description="Face Slap",
                )
            elif roll < 0.70:
                self.intent = Intent(IntentType.ATTACK, damage=22, description="Heavy Slash")
            else:
                self.intent = Intent(
                    IntentType.ATTACK_DEBUFF, damage=10, hits=2,
                    description="Execute",
                )

    def take_turn(self, combat):
        desc = self.intent.description or ""
        if desc == "Heavy Slash":
            dmg = self.get_attack_damage(22)
            combat.deal_damage_to_player(dmg, self)
            print(f"  {self.name} Heavy Slash for {dmg} damage!")
            self.move_history.append("heavy_slash")
        elif desc == "Execute":
            dmg = self.get_attack_damage(10)
            for _ in range(2):
                combat.deal_damage_to_player(dmg, self)
            print(f"  {self.name} Execute for {dmg}x2 damage!")
            self.move_history.append("execute")
        elif desc == "Defensive Stance":
            self.gain_block(15)
            self.effects.add(Metallicize(5))
            print(f"  {self.name} takes Defensive Stance! Gains 15 Block and 5 Metallicize!")
            self.move_history.append("defensive")
        elif desc == "Face Slap":
            dmg = self.get_attack_damage(12)
            combat.deal_damage_to_player(dmg, self)
            combat.apply_effect_to_player("Frail", 2)
            combat.apply_effect_to_player("Vulnerable", 2)
            print(f"  {self.name} Face Slap for {dmg} damage! Applies 2 Frail and 2 Vulnerable!")
            self.move_history.append("face_slap")


class AutomatonOrb(Enemy):
    """Orb minion spawned by Bronze Automaton."""

    def __init__(self):
        super().__init__("Orb", random_hp(52, 58))
        self.is_minion = True

    def choose_intent(self, combat):
        last = self.move_history[-1] if self.move_history else None
        if last == "stasis":
            self.intent = Intent(IntentType.ATTACK, damage=8, description="Beam")
        else:
            self.intent = Intent(IntentType.STRATEGIC, description="Stasis")

    def take_turn(self, combat):
        desc = self.intent.description or ""
        if desc == "Beam":
            dmg = self.get_attack_damage(8)
            combat.deal_damage_to_player(dmg, self)
            print(f"  {self.name} beams for {dmg} damage!")
            self.move_history.append("beam")
        else:
            # Stasis: steal a card from draw pile
            if combat.player.draw_pile:
                stolen = combat.player.draw_pile.pop()
                print(f"  {self.name} steals {stolen.name} via Stasis!")
            else:
                print(f"  {self.name} tries Stasis but draw pile is empty!")
            self.move_history.append("stasis")


class BronzeAutomaton(Enemy):
    """Act 2 Boss (HP 300). Boost (+3 Str), Compressor (15 dmg + shuffle status),
    Hyper Beam (45 dmg, then stunned next turn). Spawns Orb minions.
    """

    def __init__(self):
        super().__init__("Bronze Automaton", 300)
        self.stunned = False
        self.orbs_spawned = False

    def choose_intent(self, combat):
        if self.stunned:
            self.intent = Intent(IntentType.STUN, description="Stunned")
            self.stunned = False
            return

        if not self.orbs_spawned:
            self.intent = Intent(IntentType.STRATEGIC, description="Spawn Orbs")
            return

        last = self.move_history[-1] if self.move_history else None
        roll = random.random()

        if last != "hyper_beam" and roll < 0.30:
            self.intent = Intent(IntentType.ATTACK, damage=45, description="Hyper Beam")
        elif roll < 0.55:
            self.intent = Intent(IntentType.BUFF, description="Boost")
        else:
            self.intent = Intent(
                IntentType.ATTACK_DEBUFF, damage=15,
                description="Compressor",
            )

    def take_turn(self, combat):
        desc = self.intent.description or ""
        if desc == "Spawn Orbs":
            o1 = AutomatonOrb()
            o2 = AutomatonOrb()
            combat.enemies.append(o1)
            combat.enemies.append(o2)
            o1.choose_intent(combat)
            o2.choose_intent(combat)
            self.orbs_spawned = True
            print(f"  {self.name} spawns 2 Orbs!")
            self.move_history.append("spawn")
        elif desc == "Boost":
            self.effects.add(Strength(3))
            print(f"  {self.name} boosts! Gains 3 Strength!")
            self.move_history.append("boost")
        elif desc == "Compressor":
            dmg = self.get_attack_damage(15)
            combat.deal_damage_to_player(dmg, self)
            from slay_the_spire.card import create_card
            for _ in range(2):
                try:
                    status = create_card("wound")
                    pos = random.randint(0, max(0, len(combat.player.draw_pile)))
                    combat.player.draw_pile.insert(pos, status)
                except Exception:
                    pass
            print(f"  {self.name} compresses for {dmg} damage! 2 status cards shuffled into draw pile!")
            self.move_history.append("compressor")
        elif desc == "Hyper Beam":
            dmg = self.get_attack_damage(45)
            combat.deal_damage_to_player(dmg, self)
            self.stunned = True
            print(f"  {self.name} fires Hyper Beam for {dmg} damage! (Will be stunned next turn)")
            self.move_history.append("hyper_beam")
        elif desc == "Stunned":
            print(f"  {self.name} is stunned and cannot act!")
            self.move_history.append("stunned")


class TorchHead(Enemy):
    """Minion summoned by Collector."""

    def __init__(self):
        super().__init__("Torch Head", random_hp(38, 42))
        self.is_minion = True

    def choose_intent(self, combat):
        self.intent = Intent(IntentType.ATTACK, damage=7, description="Tackle")

    def take_turn(self, combat):
        dmg = self.get_attack_damage(7)
        combat.deal_damage_to_player(dmg, self)
        print(f"  {self.name} tackles for {dmg} damage!")
        self.move_history.append("tackle")


class Collector(Enemy):
    """Act 2 Boss (HP 282). Summons Torch Head minions,
    Mega Debuff (3 Weak + 3 Vulnerable + 3 Frail), Fireball (18 dmg).
    """

    def __init__(self):
        super().__init__("The Collector", 282)
        self.torch_heads = []
        self.initial_summon_done = False

    def choose_intent(self, combat):
        if not self.initial_summon_done:
            self.intent = Intent(IntentType.STRATEGIC, description="Summon Torches")
            return

        alive_torches = [t for t in self.torch_heads if t.is_alive]
        last = self.move_history[-1] if self.move_history else None
        roll = random.random()

        if len(alive_torches) == 0 and last != "summon":
            self.intent = Intent(IntentType.STRATEGIC, description="Summon Torches")
        elif last != "mega_debuff" and roll < 0.25:
            self.intent = Intent(IntentType.DEBUFF, description="Mega Debuff")
        elif roll < 0.55:
            self.intent = Intent(IntentType.ATTACK, damage=18, description="Fireball")
        else:
            self.intent = Intent(
                IntentType.ATTACK_BUFF, damage=18, block=15,
                description="Fireball + Block",
            )

    def take_turn(self, combat):
        desc = self.intent.description or ""
        if desc == "Summon Torches":
            count = 0
            while len([t for t in self.torch_heads if t.is_alive]) < 2 and count < 2:
                torch = TorchHead()
                self.torch_heads.append(torch)
                combat.enemies.append(torch)
                torch.choose_intent(combat)
                count += 1
            self.initial_summon_done = True
            print(f"  {self.name} summons Torch Heads!")
            self.move_history.append("summon")
        elif desc == "Mega Debuff":
            combat.apply_effect_to_player("Weak", 3)
            combat.apply_effect_to_player("Vulnerable", 3)
            combat.apply_effect_to_player("Frail", 3)
            print(f"  {self.name} uses Mega Debuff! 3 Weak, 3 Vulnerable, 3 Frail!")
            self.move_history.append("mega_debuff")
        elif desc == "Fireball":
            dmg = self.get_attack_damage(18)
            combat.deal_damage_to_player(dmg, self)
            print(f"  {self.name} hurls a Fireball for {dmg} damage!")
            self.move_history.append("fireball")
        elif desc == "Fireball + Block":
            dmg = self.get_attack_damage(18)
            combat.deal_damage_to_player(dmg, self)
            self.gain_block(15)
            print(f"  {self.name} hurls a Fireball for {dmg} damage and gains 15 Block!")
            self.move_history.append("fireball_block")


# =============================================================================
# ACT 3 BOSSES
# =============================================================================


class AwakenedOne(Enemy):
    """Act 3 Boss (HP 300). Two phases.
    Phase 1: Slash (20), Soul Strike (6x4). Gains Str when player plays Powers.
    On death, revives with full HP for Phase 2 (more aggressive).
    """

    def __init__(self):
        super().__init__("Awakened One", 300)
        self.phase = 1
        self.has_revived = False
        self.effects.add(Curiosity(1))  # Gains 1 Str per Power played

    def choose_intent(self, combat):
        if self.phase == 1:
            last = self.move_history[-1] if self.move_history else None
            roll = random.random()
            if last != "soul_strike" and roll < 0.40:
                self.intent = Intent(
                    IntentType.ATTACK, damage=6, hits=4,
                    description="Soul Strike",
                )
            else:
                self.intent = Intent(IntentType.ATTACK, damage=20, description="Slash")
        else:
            # Phase 2: more aggressive
            last = self.move_history[-1] if self.move_history else None
            roll = random.random()
            if last != "dark_echo" and roll < 0.30:
                self.intent = Intent(IntentType.ATTACK, damage=40, description="Dark Echo")
            elif roll < 0.60:
                self.intent = Intent(
                    IntentType.ATTACK, damage=10, hits=3,
                    description="Sludge",
                )
            else:
                self.intent = Intent(IntentType.ATTACK, damage=20, description="Slash")

    def take_turn(self, combat):
        desc = self.intent.description or ""
        if desc == "Slash":
            dmg = self.get_attack_damage(20)
            combat.deal_damage_to_player(dmg, self)
            print(f"  {self.name} slashes for {dmg} damage!")
            self.move_history.append("slash")
        elif desc == "Soul Strike":
            dmg = self.get_attack_damage(6)
            for _ in range(4):
                combat.deal_damage_to_player(dmg, self)
            print(f"  {self.name} Soul Strike for {dmg}x4 damage!")
            self.move_history.append("soul_strike")
        elif desc == "Dark Echo":
            dmg = self.get_attack_damage(40)
            combat.deal_damage_to_player(dmg, self)
            print(f"  {self.name} Dark Echo for {dmg} damage!")
            self.move_history.append("dark_echo")
        elif desc == "Sludge":
            dmg = self.get_attack_damage(10)
            for _ in range(3):
                combat.deal_damage_to_player(dmg, self)
            print(f"  {self.name} Sludge for {dmg}x3 damage!")
            self.move_history.append("sludge")

    def on_death(self, combat=None):
        if self.phase == 1 and not self.has_revived:
            # Revive in Phase 2
            self.has_revived = True
            self.phase = 2
            self.hp = self.max_hp
            self.is_alive = True
            self.move_history.clear()
            # Remove Curiosity in phase 2
            self.effects.remove("Curiosity")
            # Clear debuffs on revive
            debuff_names = list(self.effects.get_debuffs().keys())
            for name in debuff_names:
                self.effects.remove(name)
            print(f"  {self.name} awakens with renewed fury! (Phase 2 - Full HP)")
        else:
            super().on_death(combat)


class TimeEater(Enemy):
    """Act 3 Boss (HP 456). Tracks cards played; after 12 cards, ends turn + heals.
    Haste (buff), Reverberate (7x3), Head Slam (26 + 2 Vuln + Draw Down),
    Ripple (9 + Slimed).
    """

    def __init__(self):
        super().__init__("Time Eater", 456)
        self.cards_played_count = 0

    def choose_intent(self, combat):
        last = self.move_history[-1] if self.move_history else None
        roll = random.random()

        if self.turn == 0:
            self.intent = Intent(IntentType.BUFF, description="Haste")
        elif last == "haste" or (last != "head_slam" and roll < 0.30):
            self.intent = Intent(
                IntentType.ATTACK_DEBUFF, damage=26,
                description="Head Slam",
            )
        elif roll < 0.55:
            self.intent = Intent(
                IntentType.ATTACK, damage=7, hits=3,
                description="Reverberate",
            )
        else:
            self.intent = Intent(
                IntentType.ATTACK_DEBUFF, damage=9,
                description="Ripple",
            )

    def take_turn(self, combat):
        desc = self.intent.description or ""
        if desc == "Haste":
            self.effects.add(Strength(2))
            self.gain_block(20)
            print(f"  {self.name} uses Haste! Gains 2 Strength and 20 Block!")
            self.move_history.append("haste")
        elif desc == "Head Slam":
            dmg = self.get_attack_damage(26)
            combat.deal_damage_to_player(dmg, self)
            combat.apply_effect_to_player("Vulnerable", 2)
            # Draw reduction (simplified)
            from slay_the_spire.effect import Draw_Reduction
            combat.player.effects.add(Draw_Reduction(1))
            print(f"  {self.name} Head Slam for {dmg} damage! 2 Vulnerable + Draw Down!")
            self.move_history.append("head_slam")
        elif desc == "Reverberate":
            dmg = self.get_attack_damage(7)
            for _ in range(3):
                combat.deal_damage_to_player(dmg, self)
            print(f"  {self.name} Reverberate for {dmg}x3 damage!")
            self.move_history.append("reverberate")
        elif desc == "Ripple":
            dmg = self.get_attack_damage(9)
            combat.deal_damage_to_player(dmg, self)
            from slay_the_spire.card import create_card
            try:
                slimed = create_card("slimed")
                combat.player.discard_pile.append(slimed)
            except Exception:
                pass
            print(f"  {self.name} Ripple for {dmg} damage! 1 Slimed added!")
            self.move_history.append("ripple")

    def on_player_card_played(self, combat):
        """Called by combat when a card is played (hooked via Time Warp effect).
        After 12 cards, end turn + heal.
        """
        self.cards_played_count += 1
        if self.cards_played_count >= 12:
            self.cards_played_count = 0
            self.effects.add(Strength(2))
            heal_amount = int(self.max_hp * 0.02)
            self.hp = min(self.max_hp, self.hp + heal_amount)
            print(f"  {self.name}: TIME WARP! Gains 2 Strength and heals {heal_amount} HP!")
            # Note: in actual game this also ends the player's turn


class Donu(Enemy):
    """Act 3 Boss (paired with Deca). HP 250.
    Buffs + attacks. Alternates with Deca.
    Circle of Power (3 Str to both), Beam (10x2).
    """

    def __init__(self):
        super().__init__("Donu", 250)
        self.partner = None  # Reference to Deca

    def choose_intent(self, combat):
        last = self.move_history[-1] if self.move_history else None
        if last == "circle_of_power":
            self.intent = Intent(
                IntentType.ATTACK, damage=10, hits=2,
                description="Beam",
            )
        else:
            self.intent = Intent(IntentType.BUFF, description="Circle of Power")

    def take_turn(self, combat):
        desc = self.intent.description or ""
        if desc == "Circle of Power":
            self.effects.add(Strength(3))
            if self.partner and self.partner.is_alive:
                self.partner.effects.add(Strength(3))
            print(f"  {self.name} uses Circle of Power! Both gain 3 Strength!")
            self.move_history.append("circle_of_power")
        elif desc == "Beam":
            dmg = self.get_attack_damage(10)
            for _ in range(2):
                combat.deal_damage_to_player(dmg, self)
            print(f"  {self.name} fires Beam for {dmg}x2 damage!")
            self.move_history.append("beam")


class Deca(Enemy):
    """Act 3 Boss (paired with Donu). HP 250.
    Debuffs + attacks. Alternates with Donu.
    Square of Protection (16 Block to both), Smash (23 + Vuln).
    """

    def __init__(self):
        super().__init__("Deca", 250)
        self.partner = None  # Reference to Donu

    def choose_intent(self, combat):
        last = self.move_history[-1] if self.move_history else None
        if last == "square_of_protection":
            self.intent = Intent(
                IntentType.ATTACK_DEBUFF, damage=23,
                description="Smash",
            )
        else:
            self.intent = Intent(
                IntentType.DEFEND, block=16,
                description="Square of Protection",
            )

    def take_turn(self, combat):
        desc = self.intent.description or ""
        if desc == "Square of Protection":
            self.gain_block(16)
            if self.partner and self.partner.is_alive:
                self.partner.gain_block(16)
            print(f"  {self.name} uses Square of Protection! Both gain 16 Block!")
            self.move_history.append("square_of_protection")
        elif desc == "Smash":
            dmg = self.get_attack_damage(23)
            combat.deal_damage_to_player(dmg, self)
            combat.apply_effect_to_player("Vulnerable", 2)
            print(f"  {self.name} smashes for {dmg} damage and applies 2 Vulnerable!")
            self.move_history.append("smash")


# =============================================================================
# ACT 4 BOSS (HEART)
# =============================================================================


class CorruptHeart(Enemy):
    """Act 4 Final Boss (HP 750). Beat of Death (1 dmg per card played).
    Invincible (max 200 damage per turn).
    Blood Shots (2x15), Echo (40 dmg), Debilitate (5 of each debuff),
    Buff (+2 Str, +2 Artifact).
    """

    def __init__(self):
        super().__init__("Corrupt Heart", 750)
        self.effects.add(Beat_of_Death(1))
        self.effects.add(Invincible(200))
        self.damage_taken_this_turn = 0

    def take_damage(self, amount, combat=None):
        if amount <= 0:
            return 0
        # Invincible: cap damage per turn at 200
        remaining_cap = 200 - self.damage_taken_this_turn
        if remaining_cap <= 0:
            print(f"  {self.name} is Invincible! No more damage this turn!")
            return 0
        capped = min(amount, remaining_cap)
        actual = super().take_damage(capped, combat)
        self.damage_taken_this_turn += actual
        return actual

    def start_turn(self):
        super().start_turn()
        self.damage_taken_this_turn = 0

    def choose_intent(self, combat):
        # Pattern: Debilitate -> Blood Shots -> Buff -> Echo -> repeat with variations
        cycle = self.turn % 4
        if cycle == 0:
            self.intent = Intent(IntentType.DEBUFF, description="Debilitate")
        elif cycle == 1:
            self.intent = Intent(
                IntentType.ATTACK, damage=2, hits=15,
                description="Blood Shots",
            )
        elif cycle == 2:
            self.intent = Intent(IntentType.BUFF, description="Buff")
        else:
            self.intent = Intent(IntentType.ATTACK, damage=40, description="Echo")

    def take_turn(self, combat):
        desc = self.intent.description or ""
        if desc == "Debilitate":
            combat.apply_effect_to_player("Vulnerable", 5)
            combat.apply_effect_to_player("Weak", 5)
            combat.apply_effect_to_player("Frail", 5)
            print(f"  {self.name} Debilitates! 5 Vulnerable, 5 Weak, 5 Frail!")
            self.move_history.append("debilitate")
        elif desc == "Blood Shots":
            dmg = self.get_attack_damage(2)
            for _ in range(15):
                combat.deal_damage_to_player(dmg, self)
            print(f"  {self.name} fires Blood Shots for {dmg}x15 damage!")
            self.move_history.append("blood_shots")
        elif desc == "Buff":
            self.effects.add(Strength(2))
            self.effects.add(Artifact(2))
            print(f"  {self.name} buffs! Gains 2 Strength and 2 Artifact!")
            self.move_history.append("buff")
        elif desc == "Echo":
            dmg = self.get_attack_damage(40)
            combat.deal_damage_to_player(dmg, self)
            print(f"  {self.name} Echo for {dmg} damage!")
            self.move_history.append("echo")


# =============================================================================
# ENCOUNTER FACTORY FUNCTIONS
# =============================================================================


def get_act1_bosses():
    """Return list of factory functions for Act 1 boss encounters."""
    return [
        lambda: [SlimeBoss()],
        lambda: [TheGuardian()],
        lambda: [Hexaghost()],
    ]


def get_act2_bosses():
    """Return list of factory functions for Act 2 boss encounters."""
    return [
        lambda: [TheChamp()],
        lambda: [BronzeAutomaton()],
        lambda: _create_collector_encounter(),
    ]


def _create_collector_encounter():
    """Create Collector encounter with initial Torch Heads."""
    collector = Collector()
    t1 = TorchHead()
    t2 = TorchHead()
    collector.torch_heads = [t1, t2]
    collector.initial_summon_done = True
    return [collector, t1, t2]


def get_act3_bosses():
    """Return list of factory functions for Act 3 boss encounters."""
    return [
        lambda: [AwakenedOne()],
        lambda: [TimeEater()],
        lambda: _create_donu_deca_encounter(),
    ]


def _create_donu_deca_encounter():
    """Create Donu & Deca encounter with cross-references."""
    donu = Donu()
    deca = Deca()
    donu.partner = deca
    deca.partner = donu
    return [donu, deca]


def get_act4_bosses():
    """Return list of factory functions for Act 4 boss encounter."""
    return [
        lambda: [CorruptHeart()],
    ]
