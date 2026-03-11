"""Act 1 enemy definitions for Slay the Spire."""
import random
from slay_the_spire.enemy import Enemy, Intent, IntentType, random_hp
from slay_the_spire.effect import (
    Strength, Weak, Vulnerable, Frail, Ritual, Curl_Up,
    Entangled, Spore_Cloud, Thievery,
)


# =============================================================================
# JAW WORM
# =============================================================================
class JawWorm(Enemy):
    """Act 1 starting enemy. Alternates Chomp, Bellow, and Thrash."""

    def __init__(self):
        super().__init__("Jaw Worm", random_hp(40, 44))

    def choose_intent(self, combat):
        if self.turn == 0:
            # First move is always Chomp
            self.intent = Intent(IntentType.ATTACK, damage=11, description="Chomp")
        else:
            last = self.move_history[-1] if self.move_history else None
            moves = ["chomp", "bellow", "thrash"]
            if last:
                moves = [m for m in moves if m != last]
            choice = random.choice(moves)
            if choice == "chomp":
                self.intent = Intent(IntentType.ATTACK, damage=11, description="Chomp")
            elif choice == "bellow":
                self.intent = Intent(IntentType.ATTACK_DEFEND, damage=0, block=6,
                                     description="Bellow")
                self.intent.intent_type = IntentType.BUFF
            elif choice == "thrash":
                self.intent = Intent(IntentType.ATTACK_DEFEND, damage=7, block=5,
                                     description="Thrash")

    def take_turn(self, combat):
        desc = self.intent.description
        self.move_history.append(desc.lower() if desc else "chomp")
        if desc == "Chomp":
            combat.deal_damage_to_player(self.get_attack_damage(11), self)
            print(f"  {self.name} uses Chomp for {self.get_attack_damage(11)} damage!")
        elif desc == "Bellow":
            self.effects.add(Strength(3))
            self.gain_block(6)
            print(f"  {self.name} uses Bellow! Gains 3 Strength and 6 Block.")
        elif desc == "Thrash":
            combat.deal_damage_to_player(self.get_attack_damage(7), self)
            self.gain_block(5)
            print(f"  {self.name} uses Thrash for {self.get_attack_damage(7)} damage and gains 5 Block!")


# =============================================================================
# CULTIST
# =============================================================================
class Cultist(Enemy):
    """Turn 1: Incantation (3 Ritual). Then attacks with Dark Strike (6 dmg)."""

    def __init__(self):
        super().__init__("Cultist", random_hp(48, 54))

    def choose_intent(self, combat):
        if self.turn == 0:
            self.intent = Intent(IntentType.BUFF, description="Incantation")
        else:
            self.intent = Intent(IntentType.ATTACK, damage=6, description="Dark Strike")

    def take_turn(self, combat):
        if self.intent.description == "Incantation":
            self.effects.add(Ritual(3))
            print(f"  {self.name} chants! Gains 3 Ritual.")
        else:
            dmg = self.get_attack_damage(6)
            combat.deal_damage_to_player(dmg, self)
            print(f"  {self.name} uses Dark Strike for {dmg} damage!")
        self.move_history.append(self.intent.description)


# =============================================================================
# BLUE SLAVER
# =============================================================================
class BlueSlaver(Enemy):
    """Stab (12 dmg) or Rake (7 dmg + 1 Weak)."""

    def __init__(self):
        super().__init__("Blue Slaver", random_hp(46, 50))

    def choose_intent(self, combat):
        roll = random.random()
        if roll < 0.4:
            self.intent = Intent(IntentType.ATTACK_DEBUFF, damage=7,
                                 description="Rake")
        else:
            self.intent = Intent(IntentType.ATTACK, damage=12,
                                 description="Stab")

    def take_turn(self, combat):
        if self.intent.description == "Stab":
            dmg = self.get_attack_damage(12)
            combat.deal_damage_to_player(dmg, self)
            print(f"  {self.name} Stabs for {dmg} damage!")
        elif self.intent.description == "Rake":
            dmg = self.get_attack_damage(7)
            combat.deal_damage_to_player(dmg, self)
            combat.apply_effect_to_player("Weak", 1)
            print(f"  {self.name} Rakes for {dmg} damage and applies 1 Weak!")
        self.move_history.append(self.intent.description)


# =============================================================================
# RED SLAVER
# =============================================================================
class RedSlaver(Enemy):
    """Stab (13 dmg), Scrape (8 dmg + 1 Vuln), Entangle (1 Entangled)."""

    def __init__(self):
        super().__init__("Red Slaver", random_hp(46, 50))
        self._used_entangle = False

    def choose_intent(self, combat):
        if not self._used_entangle and self.turn >= 1 and random.random() < 0.25:
            self.intent = Intent(IntentType.DEBUFF, description="Entangle")
        else:
            roll = random.random()
            if roll < 0.45:
                self.intent = Intent(IntentType.ATTACK, damage=13,
                                     description="Stab")
            else:
                self.intent = Intent(IntentType.ATTACK_DEBUFF, damage=8,
                                     description="Scrape")

    def take_turn(self, combat):
        desc = self.intent.description
        if desc == "Stab":
            dmg = self.get_attack_damage(13)
            combat.deal_damage_to_player(dmg, self)
            print(f"  {self.name} Stabs for {dmg} damage!")
        elif desc == "Scrape":
            dmg = self.get_attack_damage(8)
            combat.deal_damage_to_player(dmg, self)
            combat.apply_effect_to_player("Vulnerable", 1)
            print(f"  {self.name} Scrapes for {dmg} damage and applies 1 Vulnerable!")
        elif desc == "Entangle":
            self._used_entangle = True
            combat.apply_effect_to_player("Entangled", 1)
            print(f"  {self.name} Entangles you! You cannot play Attacks this turn.")
        self.move_history.append(desc)


# =============================================================================
# SMALL SLIMES
# =============================================================================
class SmallAcidSlime(Enemy):
    """Lick (1 Weak) or Tackle (3 dmg)."""

    def __init__(self):
        super().__init__("Small Acid Slime", random_hp(8, 14))

    def choose_intent(self, combat):
        if random.random() < 0.5:
            self.intent = Intent(IntentType.DEBUFF, description="Lick")
        else:
            self.intent = Intent(IntentType.ATTACK, damage=3, description="Tackle")

    def take_turn(self, combat):
        if self.intent.description == "Lick":
            combat.apply_effect_to_player("Weak", 1)
            print(f"  {self.name} Licks! Applies 1 Weak.")
        else:
            dmg = self.get_attack_damage(3)
            combat.deal_damage_to_player(dmg, self)
            print(f"  {self.name} Tackles for {dmg} damage!")
        self.move_history.append(self.intent.description)


class SmallSpikeSlime(Enemy):
    """Tackle (4 dmg). Small spike slimes only attack."""

    def __init__(self):
        super().__init__("Small Spike Slime", random_hp(10, 14))

    def choose_intent(self, combat):
        self.intent = Intent(IntentType.ATTACK, damage=4, description="Tackle")

    def take_turn(self, combat):
        dmg = self.get_attack_damage(4)
        combat.deal_damage_to_player(dmg, self)
        print(f"  {self.name} Tackles for {dmg} damage!")
        self.move_history.append("Tackle")


# =============================================================================
# MEDIUM SLIMES
# =============================================================================
class MediumAcidSlime(Enemy):
    """Corrosive Spit (7 dmg + 1 Weak) or Tackle (10 dmg). Splits on death."""

    def __init__(self):
        super().__init__("Medium Acid Slime", random_hp(28, 32))

    def choose_intent(self, combat):
        if random.random() < 0.5:
            self.intent = Intent(IntentType.ATTACK_DEBUFF, damage=7,
                                 description="Corrosive Spit")
        else:
            self.intent = Intent(IntentType.ATTACK, damage=10,
                                 description="Tackle")

    def take_turn(self, combat):
        if self.intent.description == "Corrosive Spit":
            dmg = self.get_attack_damage(7)
            combat.deal_damage_to_player(dmg, self)
            combat.apply_effect_to_player("Weak", 1)
            print(f"  {self.name} spits acid for {dmg} damage and applies 1 Weak!")
        else:
            dmg = self.get_attack_damage(10)
            combat.deal_damage_to_player(dmg, self)
            print(f"  {self.name} Tackles for {dmg} damage!")
        self.move_history.append(self.intent.description)

    def on_death(self, combat=None):
        super().on_death(combat)
        if combat:
            s1 = SmallAcidSlime()
            s2 = SmallAcidSlime()
            s1.hp = self.max_hp // 2
            s1.max_hp = s1.hp
            s2.hp = self.max_hp // 2
            s2.max_hp = s2.hp
            combat.enemies.append(s1)
            combat.enemies.append(s2)
            s1.choose_intent(combat)
            s2.choose_intent(combat)
            print(f"  {self.name} splits into 2 Small Acid Slimes!")


class MediumSpikeSlime(Enemy):
    """Flame Tackle (8 dmg + 1 Frail) or Lick (1 Frail). Splits on death."""

    def __init__(self):
        super().__init__("Medium Spike Slime", random_hp(28, 32))

    def choose_intent(self, combat):
        if random.random() < 0.5:
            self.intent = Intent(IntentType.ATTACK_DEBUFF, damage=8,
                                 description="Flame Tackle")
        else:
            self.intent = Intent(IntentType.DEBUFF, description="Lick")

    def take_turn(self, combat):
        if self.intent.description == "Flame Tackle":
            dmg = self.get_attack_damage(8)
            combat.deal_damage_to_player(dmg, self)
            combat.apply_effect_to_player("Frail", 1)
            print(f"  {self.name} uses Flame Tackle for {dmg} damage and applies 1 Frail!")
        else:
            combat.apply_effect_to_player("Frail", 1)
            print(f"  {self.name} Licks! Applies 1 Frail.")
        self.move_history.append(self.intent.description)

    def on_death(self, combat=None):
        super().on_death(combat)
        if combat:
            s1 = SmallSpikeSlime()
            s2 = SmallSpikeSlime()
            s1.hp = self.max_hp // 2
            s1.max_hp = s1.hp
            s2.hp = self.max_hp // 2
            s2.max_hp = s2.hp
            combat.enemies.append(s1)
            combat.enemies.append(s2)
            s1.choose_intent(combat)
            s2.choose_intent(combat)
            print(f"  {self.name} splits into 2 Small Spike Slimes!")


# =============================================================================
# LARGE SLIMES
# =============================================================================
class LargeAcidSlime(Enemy):
    """Corrosive Spit (11 dmg + 2 Weak), Tackle (16 dmg), Lick (2 Weak).
    Splits into 2 Medium Acid Slimes at half HP."""

    def __init__(self):
        super().__init__("Large Acid Slime", random_hp(65, 69))
        self._has_split = False

    def choose_intent(self, combat):
        last = self.move_history[-1] if self.move_history else None
        choices = ["Corrosive Spit", "Tackle", "Lick"]
        if last:
            choices = [c for c in choices if c != last]
        choice = random.choice(choices)
        if choice == "Corrosive Spit":
            self.intent = Intent(IntentType.ATTACK_DEBUFF, damage=11,
                                 description="Corrosive Spit")
        elif choice == "Tackle":
            self.intent = Intent(IntentType.ATTACK, damage=16,
                                 description="Tackle")
        else:
            self.intent = Intent(IntentType.DEBUFF, description="Lick")

    def take_turn(self, combat):
        desc = self.intent.description
        if desc == "Corrosive Spit":
            dmg = self.get_attack_damage(11)
            combat.deal_damage_to_player(dmg, self)
            combat.apply_effect_to_player("Weak", 2)
            print(f"  {self.name} spits acid for {dmg} damage and applies 2 Weak!")
        elif desc == "Tackle":
            dmg = self.get_attack_damage(16)
            combat.deal_damage_to_player(dmg, self)
            print(f"  {self.name} Tackles for {dmg} damage!")
        elif desc == "Lick":
            combat.apply_effect_to_player("Weak", 2)
            print(f"  {self.name} Licks! Applies 2 Weak.")
        self.move_history.append(desc)
        # Check split
        if not self._has_split and self.hp <= self.max_hp // 2 and self.hp > 0:
            self._split(combat)

    def _split(self, combat):
        self._has_split = True
        self.is_alive = False
        self.hp = 0
        m1 = MediumAcidSlime()
        m2 = MediumAcidSlime()
        split_hp = self.max_hp // 4
        m1.hp = split_hp
        m1.max_hp = split_hp
        m2.hp = split_hp
        m2.max_hp = split_hp
        combat.enemies.append(m1)
        combat.enemies.append(m2)
        m1.choose_intent(combat)
        m2.choose_intent(combat)
        print(f"  {self.name} splits into 2 Medium Acid Slimes!")


class LargeSpikeSlime(Enemy):
    """Flame Tackle (16 dmg + 2 Frail), Lick (2 Frail).
    Splits into 2 Medium Spike Slimes at half HP."""

    def __init__(self):
        super().__init__("Large Spike Slime", random_hp(65, 69))
        self._has_split = False

    def choose_intent(self, combat):
        if random.random() < 0.5:
            self.intent = Intent(IntentType.ATTACK_DEBUFF, damage=16,
                                 description="Flame Tackle")
        else:
            self.intent = Intent(IntentType.DEBUFF, description="Lick")

    def take_turn(self, combat):
        desc = self.intent.description
        if desc == "Flame Tackle":
            dmg = self.get_attack_damage(16)
            combat.deal_damage_to_player(dmg, self)
            combat.apply_effect_to_player("Frail", 2)
            print(f"  {self.name} uses Flame Tackle for {dmg} damage and applies 2 Frail!")
        elif desc == "Lick":
            combat.apply_effect_to_player("Frail", 2)
            print(f"  {self.name} Licks! Applies 2 Frail.")
        self.move_history.append(desc)
        # Check split
        if not self._has_split and self.hp <= self.max_hp // 2 and self.hp > 0:
            self._split(combat)

    def _split(self, combat):
        self._has_split = True
        self.is_alive = False
        self.hp = 0
        m1 = MediumSpikeSlime()
        m2 = MediumSpikeSlime()
        split_hp = self.max_hp // 4
        m1.hp = split_hp
        m1.max_hp = split_hp
        m2.hp = split_hp
        m2.max_hp = split_hp
        combat.enemies.append(m1)
        combat.enemies.append(m2)
        m1.choose_intent(combat)
        m2.choose_intent(combat)
        print(f"  {self.name} splits into 2 Medium Spike Slimes!")


# =============================================================================
# FUNGI BEAST
# =============================================================================
class FungiBeast(Enemy):
    """Bite (6 dmg) or Grow (3 Strength). Applies 2 Vulnerable on death."""

    def __init__(self):
        super().__init__("Fungi Beast", random_hp(22, 28))
        self.effects.add(Spore_Cloud(2))

    def choose_intent(self, combat):
        if random.random() < 0.6:
            self.intent = Intent(IntentType.ATTACK, damage=6, description="Bite")
        else:
            self.intent = Intent(IntentType.BUFF, description="Grow")

    def take_turn(self, combat):
        if self.intent.description == "Bite":
            dmg = self.get_attack_damage(6)
            combat.deal_damage_to_player(dmg, self)
            print(f"  {self.name} Bites for {dmg} damage!")
        else:
            self.effects.add(Strength(3))
            print(f"  {self.name} Grows! Gains 3 Strength.")
        self.move_history.append(self.intent.description)


# =============================================================================
# LOUSE (RED / GREEN)
# =============================================================================
class RedLouse(Enemy):
    """Bite (5-7 dmg) or Grow (3 Strength). Has Curl Up."""

    def __init__(self):
        super().__init__("Red Louse", random_hp(10, 15))
        self._bite_damage = random.randint(5, 7)
        self.effects.add(Curl_Up(random.randint(3, 7)))

    def choose_intent(self, combat):
        if random.random() < 0.75:
            self.intent = Intent(IntentType.ATTACK, damage=self._bite_damage,
                                 description="Bite")
        else:
            self.intent = Intent(IntentType.BUFF, description="Grow")

    def take_turn(self, combat):
        if self.intent.description == "Bite":
            dmg = self.get_attack_damage(self._bite_damage)
            combat.deal_damage_to_player(dmg, self)
            print(f"  {self.name} Bites for {dmg} damage!")
        else:
            self.effects.add(Strength(3))
            print(f"  {self.name} Grows! Gains 3 Strength.")
        self.move_history.append(self.intent.description)


class GreenLouse(Enemy):
    """Bite (5-7 dmg) or Spit Web (2 Weak). Has Curl Up."""

    def __init__(self):
        super().__init__("Green Louse", random_hp(10, 15))
        self._bite_damage = random.randint(5, 7)
        self.effects.add(Curl_Up(random.randint(3, 7)))

    def choose_intent(self, combat):
        if random.random() < 0.75:
            self.intent = Intent(IntentType.ATTACK, damage=self._bite_damage,
                                 description="Bite")
        else:
            self.intent = Intent(IntentType.DEBUFF, description="Spit Web")

    def take_turn(self, combat):
        if self.intent.description == "Bite":
            dmg = self.get_attack_damage(self._bite_damage)
            combat.deal_damage_to_player(dmg, self)
            print(f"  {self.name} Bites for {dmg} damage!")
        else:
            combat.apply_effect_to_player("Weak", 2)
            print(f"  {self.name} Spits Web! Applies 2 Weak.")
        self.move_history.append(self.intent.description)


# =============================================================================
# GREMLINS
# =============================================================================
class MadGremlin(Enemy):
    """Scratch (4 dmg). Has Angry (gains 1 Strength when hit)."""

    def __init__(self):
        super().__init__("Mad Gremlin", random_hp(20, 24))
        from slay_the_spire.effect import Angry
        self.effects.add(Angry(1))

    def choose_intent(self, combat):
        self.intent = Intent(IntentType.ATTACK, damage=4, description="Scratch")

    def take_turn(self, combat):
        dmg = self.get_attack_damage(4)
        combat.deal_damage_to_player(dmg, self)
        print(f"  {self.name} Scratches for {dmg} damage!")
        self.move_history.append("Scratch")


class SneakyGremlin(Enemy):
    """Puncture (9 dmg)."""

    def __init__(self):
        super().__init__("Sneaky Gremlin", random_hp(10, 14))

    def choose_intent(self, combat):
        self.intent = Intent(IntentType.ATTACK, damage=9, description="Puncture")

    def take_turn(self, combat):
        dmg = self.get_attack_damage(9)
        combat.deal_damage_to_player(dmg, self)
        print(f"  {self.name} Punctures for {dmg} damage!")
        self.move_history.append("Puncture")


class FatGremlin(Enemy):
    """Smash (4 dmg + 1 Weak) or nothing."""

    def __init__(self):
        super().__init__("Fat Gremlin", random_hp(13, 17))

    def choose_intent(self, combat):
        self.intent = Intent(IntentType.ATTACK_DEBUFF, damage=4,
                             description="Smash")

    def take_turn(self, combat):
        dmg = self.get_attack_damage(4)
        combat.deal_damage_to_player(dmg, self)
        combat.apply_effect_to_player("Weak", 1)
        print(f"  {self.name} Smashes for {dmg} damage and applies 1 Weak!")
        self.move_history.append("Smash")


class ShieldGremlin(Enemy):
    """Protect (7 Block to a random ally) or Shield Bash (6 dmg)."""

    def __init__(self):
        super().__init__("Shield Gremlin", random_hp(12, 15))

    def choose_intent(self, combat):
        # Prefer protecting if there are allies
        alive_allies = [e for e in combat.enemies if e.is_alive and e is not self]
        if alive_allies and random.random() < 0.5:
            self.intent = Intent(IntentType.DEFEND, block=7, description="Protect")
        else:
            self.intent = Intent(IntentType.ATTACK, damage=6,
                                 description="Shield Bash")

    def take_turn(self, combat):
        if self.intent.description == "Protect":
            alive_allies = [e for e in combat.enemies if e.is_alive and e is not self]
            if alive_allies:
                target = random.choice(alive_allies)
                target.gain_block(7)
                print(f"  {self.name} protects {target.name} with 7 Block!")
            else:
                dmg = self.get_attack_damage(6)
                combat.deal_damage_to_player(dmg, self)
                print(f"  {self.name} Shield Bashes for {dmg} damage!")
        else:
            dmg = self.get_attack_damage(6)
            combat.deal_damage_to_player(dmg, self)
            print(f"  {self.name} Shield Bashes for {dmg} damage!")
        self.move_history.append(self.intent.description)


class GremlinWizard(Enemy):
    """Charges for 3 turns, then Ultimate Blast (25 dmg). Resets after blast."""

    def __init__(self):
        super().__init__("Gremlin Wizard", random_hp(23, 25))
        self._charge_count = 0

    def choose_intent(self, combat):
        if self._charge_count >= 3:
            self.intent = Intent(IntentType.ATTACK, damage=25,
                                 description="Ultimate Blast")
        else:
            self.intent = Intent(IntentType.STRATEGIC, description="Charging")

    def take_turn(self, combat):
        if self.intent.description == "Ultimate Blast":
            dmg = self.get_attack_damage(25)
            combat.deal_damage_to_player(dmg, self)
            self._charge_count = 0
            print(f"  {self.name} unleashes Ultimate Blast for {dmg} damage!")
        else:
            self._charge_count += 1
            print(f"  {self.name} is charging... ({self._charge_count}/3)")
        self.move_history.append(self.intent.description)


# =============================================================================
# LOOTER
# =============================================================================
class Looter(Enemy):
    """Mug (10 dmg + steal gold), Lunge (12 dmg), Smoke Bomb (escape)."""

    def __init__(self):
        super().__init__("Looter", random_hp(44, 48))
        self.effects.add(Thievery(15))
        self._escape_turn = random.randint(3, 4)

    def choose_intent(self, combat):
        if self.turn >= self._escape_turn:
            self.intent = Intent(IntentType.ESCAPE, description="Smoke Bomb")
        elif self.turn == 0:
            self.intent = Intent(IntentType.ATTACK, damage=10, description="Mug")
        else:
            roll = random.random()
            if roll < 0.5:
                self.intent = Intent(IntentType.ATTACK, damage=10,
                                     description="Mug")
            else:
                self.intent = Intent(IntentType.ATTACK, damage=12,
                                     description="Lunge")

    def take_turn(self, combat):
        desc = self.intent.description
        if desc == "Mug":
            dmg = self.get_attack_damage(10)
            combat.deal_damage_to_player(dmg, self)
            stolen = 15
            if hasattr(combat.player, 'gold'):
                actual_stolen = min(stolen, combat.player.gold)
                combat.player.gold -= actual_stolen
                self.gold_reward += actual_stolen
            print(f"  {self.name} Mugs for {dmg} damage and steals {stolen} gold!")
        elif desc == "Lunge":
            dmg = self.get_attack_damage(12)
            combat.deal_damage_to_player(dmg, self)
            print(f"  {self.name} Lunges for {dmg} damage!")
        elif desc == "Smoke Bomb":
            self.is_alive = False
            print(f"  {self.name} uses Smoke Bomb and escapes!")
        self.move_history.append(desc)


# =============================================================================
# MUGGER
# =============================================================================
class Mugger(Enemy):
    """Similar to Looter but stronger: Mug (10 dmg + steal gold),
    Lunge (16 dmg), Smoke Bomb (escape)."""

    def __init__(self):
        super().__init__("Mugger", random_hp(48, 52))
        self.effects.add(Thievery(15))
        self._escape_turn = random.randint(3, 4)

    def choose_intent(self, combat):
        if self.turn >= self._escape_turn:
            self.intent = Intent(IntentType.ESCAPE, description="Smoke Bomb")
        elif self.turn == 0:
            self.intent = Intent(IntentType.ATTACK, damage=10, description="Mug")
        else:
            roll = random.random()
            if roll < 0.5:
                self.intent = Intent(IntentType.ATTACK, damage=10,
                                     description="Mug")
            else:
                self.intent = Intent(IntentType.ATTACK, damage=16,
                                     description="Lunge")

    def take_turn(self, combat):
        desc = self.intent.description
        if desc == "Mug":
            dmg = self.get_attack_damage(10)
            combat.deal_damage_to_player(dmg, self)
            stolen = 15
            if hasattr(combat.player, 'gold'):
                actual_stolen = min(stolen, combat.player.gold)
                combat.player.gold -= actual_stolen
                self.gold_reward += actual_stolen
            print(f"  {self.name} Mugs for {dmg} damage and steals {stolen} gold!")
        elif desc == "Lunge":
            dmg = self.get_attack_damage(16)
            combat.deal_damage_to_player(dmg, self)
            print(f"  {self.name} Lunges for {dmg} damage!")
        elif desc == "Smoke Bomb":
            self.is_alive = False
            print(f"  {self.name} uses Smoke Bomb and escapes!")
        self.move_history.append(desc)


# =============================================================================
# ENCOUNTER GENERATORS
# =============================================================================
def get_act1_normal_encounters():
    """Return list of possible Act 1 normal combat encounters."""
    return [
        lambda: [JawWorm()],
        lambda: [Cultist()],
        lambda: [BlueSlaver()],
        lambda: [RedSlaver()],
        lambda: [SmallAcidSlime(), SmallAcidSlime()],
        lambda: [SmallSpikeSlime(), SmallSpikeSlime()],
        lambda: [GreenLouse(), GreenLouse()],
        lambda: [RedLouse(), RedLouse()],
        lambda: [RedLouse(), GreenLouse()],
        lambda: [FungiBeast(), FungiBeast()],
        lambda: [MadGremlin(), SneakyGremlin(), FatGremlin(), ShieldGremlin()],
        lambda: [SneakyGremlin(), SneakyGremlin(), MadGremlin()],
        lambda: [Looter()],
        lambda: [GreenLouse(), RedLouse(), SmallAcidSlime()],
        lambda: [MediumAcidSlime()],
        lambda: [MediumSpikeSlime()],
    ]


def get_act1_elite_encounters():
    """Return list of possible Act 1 elite encounters."""
    return [
        lambda: [LargeAcidSlime()],
        lambda: [LargeSpikeSlime()],
        lambda: [GremlinWizard(), MadGremlin(), SneakyGremlin(),
                 FatGremlin(), ShieldGremlin()],
    ]
