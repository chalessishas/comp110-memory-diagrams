"""Act 2 enemy definitions for Slay the Spire."""
import random
from slay_the_spire.enemy import Enemy, Intent, IntentType, random_hp
from slay_the_spire.effect import (
    Strength, Weak, Vulnerable, Frail, Curl_Up, Flight,
    Malleable, Minion, Ritual, Artifact,
)


# =============================================================================
# SNAKE PLANT
# =============================================================================
class SnakePlant(Enemy):
    """Chomp (7 dmg x2) or Bite (7 dmg + 2 Weak)."""

    def __init__(self):
        super().__init__("Snake Plant", random_hp(75, 79))

    def choose_intent(self, combat):
        last = self.move_history[-1] if self.move_history else None
        if last == "Chomp":
            self.intent = Intent(IntentType.ATTACK_DEBUFF, damage=7,
                                 description="Bite")
        elif last == "Bite":
            self.intent = Intent(IntentType.ATTACK, damage=7, hits=2,
                                 description="Chomp")
        else:
            if random.random() < 0.5:
                self.intent = Intent(IntentType.ATTACK, damage=7, hits=2,
                                     description="Chomp")
            else:
                self.intent = Intent(IntentType.ATTACK_DEBUFF, damage=7,
                                     description="Bite")

    def take_turn(self, combat):
        desc = self.intent.description
        if desc == "Chomp":
            for i in range(2):
                dmg = self.get_attack_damage(7)
                combat.deal_damage_to_player(dmg, self)
            print(f"  {self.name} Chomps twice for {self.get_attack_damage(7)} damage each!")
        elif desc == "Bite":
            dmg = self.get_attack_damage(7)
            combat.deal_damage_to_player(dmg, self)
            combat.apply_effect_to_player("Weak", 2)
            print(f"  {self.name} Bites for {dmg} damage and applies 2 Weak!")
        self.move_history.append(desc)


# =============================================================================
# CENTURION + MYSTIC
# =============================================================================
class Centurion(Enemy):
    """Fury (6 dmg x3) or Slash (12 dmg)."""

    def __init__(self):
        super().__init__("Centurion", random_hp(76, 80))

    def choose_intent(self, combat):
        last = self.move_history[-1] if self.move_history else None
        if last == "Fury":
            self.intent = Intent(IntentType.ATTACK, damage=12,
                                 description="Slash")
        elif last == "Slash":
            self.intent = Intent(IntentType.ATTACK, damage=6, hits=3,
                                 description="Fury")
        else:
            if random.random() < 0.5:
                self.intent = Intent(IntentType.ATTACK, damage=6, hits=3,
                                     description="Fury")
            else:
                self.intent = Intent(IntentType.ATTACK, damage=12,
                                     description="Slash")

    def take_turn(self, combat):
        desc = self.intent.description
        if desc == "Fury":
            for _ in range(3):
                dmg = self.get_attack_damage(6)
                combat.deal_damage_to_player(dmg, self)
            print(f"  {self.name} strikes with Fury! {self.get_attack_damage(6)} damage x3!")
        elif desc == "Slash":
            dmg = self.get_attack_damage(12)
            combat.deal_damage_to_player(dmg, self)
            print(f"  {self.name} Slashes for {dmg} damage!")
        self.move_history.append(desc)


class Mystic(Enemy):
    """Heal (16 HP to weakest ally) or Buff (give ally 2 Strength)."""

    def __init__(self):
        super().__init__("Mystic", random_hp(48, 56))

    def choose_intent(self, combat):
        # Prefer healing if an ally is hurt
        allies = [e for e in combat.enemies if e.is_alive and e is not self]
        hurt_allies = [e for e in allies if e.hp < e.max_hp]
        if hurt_allies and random.random() < 0.6:
            self.intent = Intent(IntentType.BUFF, description="Heal")
        elif allies:
            self.intent = Intent(IntentType.BUFF, description="Buff")
        else:
            self.intent = Intent(IntentType.ATTACK, damage=8,
                                 description="Attack")

    def take_turn(self, combat):
        desc = self.intent.description
        allies = [e for e in combat.enemies if e.is_alive and e is not self]
        if desc == "Heal" and allies:
            target = min(allies, key=lambda e: e.hp)
            heal_amount = 16
            target.hp = min(target.max_hp, target.hp + heal_amount)
            print(f"  {self.name} heals {target.name} for {heal_amount} HP!")
        elif desc == "Buff" and allies:
            target = random.choice(allies)
            target.effects.add(Strength(2))
            print(f"  {self.name} buffs {target.name} with 2 Strength!")
        else:
            dmg = self.get_attack_damage(8)
            combat.deal_damage_to_player(dmg, self)
            print(f"  {self.name} attacks for {dmg} damage!")
        self.move_history.append(desc)


# =============================================================================
# CHOSEN
# =============================================================================
class Chosen(Enemy):
    """Poke (5 dmg x2), Hex (apply Hex curse), Debilitate (3 Vulnerable).
    Turn 1: always Hex, then alternates attacks and debuffs."""

    def __init__(self):
        super().__init__("Chosen", random_hp(95, 99))
        self._used_hex = False

    def choose_intent(self, combat):
        if not self._used_hex:
            self.intent = Intent(IntentType.DEBUFF, description="Hex")
        else:
            last = self.move_history[-1] if self.move_history else None
            if last == "Debilitate":
                self.intent = Intent(IntentType.ATTACK, damage=5, hits=2,
                                     description="Poke")
            elif last == "Poke":
                if random.random() < 0.35:
                    self.intent = Intent(IntentType.DEBUFF,
                                         description="Debilitate")
                else:
                    self.intent = Intent(IntentType.ATTACK, damage=5, hits=2,
                                         description="Poke")
            else:
                self.intent = Intent(IntentType.ATTACK, damage=5, hits=2,
                                     description="Poke")

    def take_turn(self, combat):
        desc = self.intent.description
        if desc == "Hex":
            self._used_hex = True
            combat.apply_effect_to_player("Hex", 1)
            print(f"  {self.name} casts Hex! Non-attack cards add Daze to draw pile.")
        elif desc == "Poke":
            for _ in range(2):
                dmg = self.get_attack_damage(5)
                combat.deal_damage_to_player(dmg, self)
            print(f"  {self.name} Pokes twice for {self.get_attack_damage(5)} damage each!")
        elif desc == "Debilitate":
            combat.apply_effect_to_player("Vulnerable", 3)
            print(f"  {self.name} uses Debilitate! Applies 3 Vulnerable.")
        self.move_history.append(desc)


# =============================================================================
# BYRD
# =============================================================================
class Byrd(Enemy):
    """Has Flight (takes 50% less damage, reduced by 1 on hit).
    Peck (1 dmg x5-6), Swoop (12 dmg), or Caw (1 Strength)."""

    def __init__(self):
        super().__init__("Byrd", random_hp(25, 31))
        self.effects.add(Flight(3))
        self._grounded = False

    def choose_intent(self, combat):
        if not self.effects.has("Flight"):
            self._grounded = True
        if self._grounded and random.random() < 0.35:
            # Re-flight
            self.intent = Intent(IntentType.BUFF, description="Fly")
        else:
            roll = random.random()
            if roll < 0.4:
                hits = random.choice([5, 6])
                self.intent = Intent(IntentType.ATTACK, damage=1, hits=hits,
                                     description="Peck")
            elif roll < 0.7:
                self.intent = Intent(IntentType.ATTACK, damage=12,
                                     description="Swoop")
            else:
                self.intent = Intent(IntentType.BUFF, description="Caw")

    def take_turn(self, combat):
        desc = self.intent.description
        if desc == "Peck":
            hits = self.intent.hits
            for _ in range(hits):
                dmg = self.get_attack_damage(1)
                combat.deal_damage_to_player(dmg, self)
            print(f"  {self.name} Pecks {hits} times for {self.get_attack_damage(1)} damage each!")
        elif desc == "Swoop":
            dmg = self.get_attack_damage(12)
            combat.deal_damage_to_player(dmg, self)
            print(f"  {self.name} Swoops for {dmg} damage!")
        elif desc == "Caw":
            self.effects.add(Strength(1))
            print(f"  {self.name} Caws! Gains 1 Strength.")
        elif desc == "Fly":
            self.effects.add(Flight(3))
            self._grounded = False
            print(f"  {self.name} takes flight! Gains 3 Flight.")
        self.move_history.append(desc)


# =============================================================================
# SHELLED PARASITE
# =============================================================================
class ShelledParasite(Enemy):
    """Double Strike (6 dmg x2), Suck (10 dmg + 2 Weak), Fell (18 dmg).
    Has Plated Armor."""

    def __init__(self):
        super().__init__("Shelled Parasite", random_hp(68, 72))
        from slay_the_spire.effect import Plated_Armor
        self.effects.add(Plated_Armor(14))

    def choose_intent(self, combat):
        last = self.move_history[-1] if self.move_history else None
        if last == "Fell":
            # After Fell, use Double Strike or Suck
            if random.random() < 0.5:
                self.intent = Intent(IntentType.ATTACK, damage=6, hits=2,
                                     description="Double Strike")
            else:
                self.intent = Intent(IntentType.ATTACK_DEBUFF, damage=10,
                                     description="Suck")
        elif last == "Suck" or last == "Double Strike":
            if random.random() < 0.4:
                self.intent = Intent(IntentType.ATTACK, damage=18,
                                     description="Fell")
            elif random.random() < 0.5:
                self.intent = Intent(IntentType.ATTACK, damage=6, hits=2,
                                     description="Double Strike")
            else:
                self.intent = Intent(IntentType.ATTACK_DEBUFF, damage=10,
                                     description="Suck")
        else:
            self.intent = Intent(IntentType.ATTACK, damage=6, hits=2,
                                 description="Double Strike")

    def take_turn(self, combat):
        desc = self.intent.description
        if desc == "Double Strike":
            for _ in range(2):
                dmg = self.get_attack_damage(6)
                combat.deal_damage_to_player(dmg, self)
            print(f"  {self.name} Double Strikes for {self.get_attack_damage(6)} damage x2!")
        elif desc == "Suck":
            dmg = self.get_attack_damage(10)
            combat.deal_damage_to_player(dmg, self)
            combat.apply_effect_to_player("Weak", 2)
            print(f"  {self.name} Sucks for {dmg} damage and applies 2 Weak!")
        elif desc == "Fell":
            dmg = self.get_attack_damage(18)
            combat.deal_damage_to_player(dmg, self)
            print(f"  {self.name} Fells for {dmg} damage!")
        self.move_history.append(desc)


# =============================================================================
# SPHERIC GUARDIAN
# =============================================================================
class SphericGuardian(Enemy):
    """Slam (10 dmg + 15 Block), Activate (gain 25 Block), Harden (15 Block).
    Very defensive enemy with high block values."""

    def __init__(self):
        super().__init__("Spheric Guardian", random_hp(20, 20))
        self._activated = False

    def choose_intent(self, combat):
        if not self._activated:
            self.intent = Intent(IntentType.BUFF, description="Activate")
        else:
            last = self.move_history[-1] if self.move_history else None
            if last == "Slam":
                self.intent = Intent(IntentType.DEFEND, block=15,
                                     description="Harden")
            else:
                self.intent = Intent(IntentType.ATTACK_DEFEND, damage=10,
                                     block=15, description="Slam")

    def take_turn(self, combat):
        desc = self.intent.description
        if desc == "Activate":
            self._activated = True
            self.gain_block(25)
            print(f"  {self.name} Activates! Gains 25 Block.")
        elif desc == "Slam":
            dmg = self.get_attack_damage(10)
            combat.deal_damage_to_player(dmg, self)
            self.gain_block(15)
            print(f"  {self.name} Slams for {dmg} damage and gains 15 Block!")
        elif desc == "Harden":
            self.gain_block(15)
            print(f"  {self.name} Hardens! Gains 15 Block.")
        self.move_history.append(desc)


# =============================================================================
# BOOK OF STABBING
# =============================================================================
class BookOfStabbing(Enemy):
    """Multi-Stab: attacks multiple times. Gains extra hits each turn."""

    def __init__(self):
        super().__init__("Book of Stabbing", 160)
        self._stab_count = 3

    def choose_intent(self, combat):
        self.intent = Intent(IntentType.ATTACK, damage=6,
                             hits=self._stab_count,
                             description="Multi-Stab")

    def take_turn(self, combat):
        hits = self._stab_count
        for _ in range(hits):
            dmg = self.get_attack_damage(6)
            combat.deal_damage_to_player(dmg, self)
        print(f"  {self.name} Multi-Stabs {hits} times for {self.get_attack_damage(6)} damage each!")
        self._stab_count += 1
        self.move_history.append("Multi-Stab")


# =============================================================================
# GREMLIN LEADER
# =============================================================================
class GremlinLeader(Enemy):
    """Summons gremlins, Rally (buff), and attacks.
    Summons gremlins when there are fewer than 3 alive."""

    def __init__(self):
        super().__init__("Gremlin Leader", random_hp(140, 148))
        self._rally_count = 0

    def choose_intent(self, combat):
        alive_minions = [e for e in combat.enemies
                         if e.is_alive and e is not self and e.is_minion]
        if len(alive_minions) < 2 and random.random() < 0.6:
            self.intent = Intent(IntentType.STRATEGIC, description="Summon")
        elif random.random() < 0.4:
            self.intent = Intent(IntentType.BUFF, description="Rally")
        else:
            self.intent = Intent(IntentType.ATTACK, damage=6, hits=3,
                                 description="Encourage")

    def take_turn(self, combat):
        desc = self.intent.description
        if desc == "Summon":
            gremlin_types = [MadGremlin, SneakyGremlin, FatGremlin, ShieldGremlin]
            for _ in range(2):
                gremlin_cls = random.choice(gremlin_types)
                g = gremlin_cls()
                g.is_minion = True
                combat.enemies.append(g)
                g.choose_intent(combat)
            print(f"  {self.name} summons 2 gremlins!")
        elif desc == "Rally":
            alive_allies = [e for e in combat.enemies if e.is_alive and e is not self]
            for ally in alive_allies:
                ally.effects.add(Strength(3))
            self.gain_block(6)
            self._rally_count += 1
            print(f"  {self.name} Rallies! All minions gain 3 Strength, leader gains 6 Block.")
        elif desc == "Encourage":
            for _ in range(3):
                dmg = self.get_attack_damage(6)
                combat.deal_damage_to_player(dmg, self)
            print(f"  {self.name} Encourages for {self.get_attack_damage(6)} damage x3!")
        self.move_history.append(desc)


# =============================================================================
# ENCOUNTER GENERATORS
# =============================================================================
def get_act2_normal_encounters():
    """Return list of possible Act 2 normal combat encounters."""
    return [
        lambda: [SnakePlant()],
        lambda: [Chosen()],
        lambda: [Byrd(), Byrd(), Byrd()],
        lambda: [ShelledParasite()],
        lambda: [Centurion(), Mystic()],
        lambda: [Byrd(), Byrd()],
        lambda: [Chosen(), Byrd()],
    ]


def get_act2_elite_encounters():
    """Return list of possible Act 2 elite encounters."""
    return [
        lambda: [SphericGuardian()],
        lambda: [BookOfStabbing()],
        lambda: _create_gremlin_leader_encounter(),
    ]


def _create_gremlin_leader_encounter():
    """Create a Gremlin Leader encounter with starting minions."""
    leader = GremlinLeader()
    from slay_the_spire.enemies.act1 import (
        MadGremlin, SneakyGremlin, FatGremlin, ShieldGremlin,
    )
    gremlin_types = [MadGremlin, SneakyGremlin, FatGremlin, ShieldGremlin]
    minions = []
    for _ in range(3):
        g = random.choice(gremlin_types)()
        g.is_minion = True
        minions.append(g)
    return [leader] + minions
