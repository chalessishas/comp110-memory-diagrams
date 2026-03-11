"""Act 3 enemy definitions for Slay the Spire."""
import random
from slay_the_spire.enemy import Enemy, Intent, IntentType, random_hp
from slay_the_spire.effect import (
    Strength, Weak, Vulnerable, Frail, Thorns, Malleable,
    Fading, Strength as StrengthEffect,
)


# =============================================================================
# DARKLINGS
# =============================================================================
class Darkling(Enemy):
    """Attack-focused enemy that revives when killed unless all Darklings die
    on the same turn. Nip (7 dmg), Chomp (8 dmg + Husk), Regroup (heal/revive)."""

    def __init__(self):
        super().__init__("Darkling", random_hp(48, 56))
        self._revive_hp = None  # set to half max_hp if killed and others live

    def choose_intent(self, combat):
        roll = random.random()
        if roll < 0.5:
            self.intent = Intent(IntentType.ATTACK, damage=7, description="Nip")
        else:
            self.intent = Intent(IntentType.ATTACK, damage=8,
                                 description="Chomp")

    def take_turn(self, combat):
        desc = self.intent.description
        if desc == "Nip":
            dmg = self.get_attack_damage(7)
            combat.deal_damage_to_player(dmg, self)
            print(f"  {self.name} Nips for {dmg} damage!")
        elif desc == "Chomp":
            dmg = self.get_attack_damage(8)
            combat.deal_damage_to_player(dmg, self)
            print(f"  {self.name} Chomps for {dmg} damage!")
        elif desc == "Regroup":
            self.hp = min(self.max_hp, self.hp + self.max_hp // 2)
            print(f"  {self.name} Regroups and heals!")
        self.move_history.append(desc)

    def on_death(self, combat=None):
        """Darklings revive unless all are dead on the same turn."""
        if combat:
            other_darklings = [e for e in combat.enemies
                               if isinstance(e, Darkling) and e is not self and e.is_alive]
            if other_darklings:
                # Will be revived at end of enemy turn
                self._revive_hp = self.max_hp // 2
                self.hp = 0
                self.is_alive = False
                print(f"  {self.name} falls... but will revive unless all Darklings are killed!")
                return
        super().on_death(combat)

    def check_revive(self, combat):
        """Called after all enemy turns to check if revive should happen."""
        if self._revive_hp and not self.is_alive:
            other_darklings = [e for e in combat.enemies
                               if isinstance(e, Darkling) and e is not self]
            any_alive = any(d.is_alive or d._revive_hp for d in other_darklings)
            if any_alive:
                self.hp = self._revive_hp
                self.is_alive = True
                self._revive_hp = None
                self.choose_intent(combat)
                print(f"  {self.name} revives with {self.hp} HP!")


# =============================================================================
# ORB WALKER
# =============================================================================
class OrbWalker(Enemy):
    """Laser (11 dmg), Claw (15 dmg + burn status cards)."""

    def __init__(self):
        super().__init__("Orb Walker", random_hp(90, 96))

    def choose_intent(self, combat):
        last = self.move_history[-1] if self.move_history else None
        if last == "Laser":
            self.intent = Intent(IntentType.ATTACK, damage=15,
                                 description="Claw")
        elif last == "Claw":
            self.intent = Intent(IntentType.ATTACK, damage=11,
                                 description="Laser")
        else:
            if random.random() < 0.5:
                self.intent = Intent(IntentType.ATTACK, damage=11,
                                     description="Laser")
            else:
                self.intent = Intent(IntentType.ATTACK, damage=15,
                                     description="Claw")

    def take_turn(self, combat):
        desc = self.intent.description
        if desc == "Laser":
            dmg = self.get_attack_damage(11)
            combat.deal_damage_to_player(dmg, self)
            print(f"  {self.name} fires Laser for {dmg} damage!")
        elif desc == "Claw":
            dmg = self.get_attack_damage(15)
            combat.deal_damage_to_player(dmg, self)
            # Add a Burn to discard pile
            try:
                from slay_the_spire.card import create_card
                burn = create_card("burn")
                combat.player.discard_pile.append(burn)
                print(f"  {self.name} Claws for {dmg} damage and shuffles a Burn into your discard pile!")
            except Exception:
                print(f"  {self.name} Claws for {dmg} damage!")
        self.move_history.append(desc)


# =============================================================================
# SPIKER
# =============================================================================
class Spiker(Enemy):
    """Cut (7 dmg). Has Thorns (deal damage back when attacked)."""

    def __init__(self):
        super().__init__("Spiker", random_hp(42, 56))
        self.effects.add(Thorns(3))

    def choose_intent(self, combat):
        if random.random() < 0.7:
            self.intent = Intent(IntentType.ATTACK, damage=7, description="Cut")
        else:
            self.intent = Intent(IntentType.BUFF, description="Spike Up")

    def take_turn(self, combat):
        desc = self.intent.description
        if desc == "Cut":
            dmg = self.get_attack_damage(7)
            combat.deal_damage_to_player(dmg, self)
            print(f"  {self.name} Cuts for {dmg} damage!")
        elif desc == "Spike Up":
            self.effects.add(Thorns(2))
            print(f"  {self.name} Spikes Up! Gains 2 more Thorns.")
        self.move_history.append(desc)


# =============================================================================
# REPULSOR
# =============================================================================
class Repulsor(Enemy):
    """Bash (11 dmg) or Repulse (push a Daze into draw pile)."""

    def __init__(self):
        super().__init__("Repulsor", random_hp(29, 35))

    def choose_intent(self, combat):
        if random.random() < 0.5:
            self.intent = Intent(IntentType.ATTACK, damage=11,
                                 description="Bash")
        else:
            self.intent = Intent(IntentType.STRATEGIC, description="Repulse")

    def take_turn(self, combat):
        desc = self.intent.description
        if desc == "Bash":
            dmg = self.get_attack_damage(11)
            combat.deal_damage_to_player(dmg, self)
            print(f"  {self.name} Bashes for {dmg} damage!")
        elif desc == "Repulse":
            try:
                from slay_the_spire.card import create_card
                daze = create_card("daze")
                insert_idx = random.randint(0, len(combat.player.draw_pile))
                combat.player.draw_pile.insert(insert_idx, daze)
                print(f"  {self.name} Repulses! A Daze is shuffled into your draw pile.")
            except Exception:
                print(f"  {self.name} Repulses!")
        self.move_history.append(desc)


# =============================================================================
# TRANSIENT
# =============================================================================
class Transient(Enemy):
    """Attacks for 30 damage each turn. Loses 10 max HP per turn.
    Runs away after 5 turns. Has Fading."""

    def __init__(self):
        super().__init__("Transient", 999)
        self.effects.add(Fading(5))
        self._turns_alive = 0

    def choose_intent(self, combat):
        if self._turns_alive >= 5:
            self.intent = Intent(IntentType.ESCAPE, description="Fade Away")
        else:
            self.intent = Intent(IntentType.ATTACK, damage=30,
                                 description="Attack")

    def take_turn(self, combat):
        desc = self.intent.description
        self._turns_alive += 1
        if desc == "Fade Away":
            self.is_alive = False
            print(f"  {self.name} fades away into nothingness...")
        elif desc == "Attack":
            dmg = self.get_attack_damage(30)
            combat.deal_damage_to_player(dmg, self)
            # Lose 10 HP each turn
            self.hp = max(0, self.hp - 10)
            print(f"  {self.name} attacks for {dmg} damage! (HP left: {self.hp})")
            if self.hp <= 0:
                self.is_alive = False
        self.move_history.append(desc)

    def start_turn(self):
        """Override to prevent death from Fading tick (handled manually)."""
        self.block = 0
        self.turn += 1
        # Poison damage
        if self.effects.has("Poison"):
            poison = self.effects.get_stacks("Poison")
            self.hp -= poison
            self.effects.reduce("Poison", 1)
            if self.hp <= 0:
                self.hp = 0
                self.is_alive = False


# =============================================================================
# WRITHING MASS
# =============================================================================
class WrithingMass(Enemy):
    """Random intents each turn. Has Malleable (gains Block when attacked).
    Implant (10 dmg + Wound), Flail (16 dmg), Wither (10 dmg + 2 Weak + 2 Frail),
    Strong Strike (32 dmg), Multi-Strike (7 dmg x3)."""

    def __init__(self):
        super().__init__("Writhing Mass", 160)
        self.effects.add(Malleable(1))

    def choose_intent(self, combat):
        moves = [
            ("Implant", IntentType.ATTACK, 10, 1),
            ("Flail", IntentType.ATTACK, 16, 1),
            ("Wither", IntentType.ATTACK_DEBUFF, 10, 1),
            ("Strong Strike", IntentType.ATTACK, 32, 1),
            ("Multi-Strike", IntentType.ATTACK, 7, 3),
        ]
        last = self.move_history[-1] if self.move_history else None
        available = [m for m in moves if m[0] != last]
        choice = random.choice(available)
        name, itype, dmg, hits = choice
        self.intent = Intent(itype, damage=dmg, hits=hits, description=name)

    def take_turn(self, combat):
        desc = self.intent.description
        if desc == "Implant":
            dmg = self.get_attack_damage(10)
            combat.deal_damage_to_player(dmg, self)
            try:
                from slay_the_spire.card import create_card
                wound = create_card("wound")
                combat.player.discard_pile.append(wound)
                print(f"  {self.name} Implants for {dmg} damage and adds a Wound!")
            except Exception:
                print(f"  {self.name} Implants for {dmg} damage!")
        elif desc == "Flail":
            dmg = self.get_attack_damage(16)
            combat.deal_damage_to_player(dmg, self)
            print(f"  {self.name} Flails for {dmg} damage!")
        elif desc == "Wither":
            dmg = self.get_attack_damage(10)
            combat.deal_damage_to_player(dmg, self)
            combat.apply_effect_to_player("Weak", 2)
            combat.apply_effect_to_player("Frail", 2)
            print(f"  {self.name} Withers for {dmg} damage, applies 2 Weak and 2 Frail!")
        elif desc == "Strong Strike":
            dmg = self.get_attack_damage(32)
            combat.deal_damage_to_player(dmg, self)
            print(f"  {self.name} Strong Strikes for {dmg} massive damage!")
        elif desc == "Multi-Strike":
            for _ in range(3):
                dmg = self.get_attack_damage(7)
                combat.deal_damage_to_player(dmg, self)
            print(f"  {self.name} Multi-Strikes 3 times for {self.get_attack_damage(7)} damage each!")
        self.move_history.append(desc)


# =============================================================================
# JAW WORM HORDE (3 Jaw Worms from Act 1)
# =============================================================================
class JawWormHorde:
    """Not a class itself -- uses get_jaw_worm_horde_encounter() below."""
    pass


# =============================================================================
# GIANT HEAD
# =============================================================================
class GiantHead(Enemy):
    """Counts attacks played. Glare (15 dmg + 1 Weak).
    It Is Time (40 dmg, used after count reaches threshold).
    Gains Slow debuff mechanic (takes more dmg per card played)."""

    def __init__(self):
        super().__init__("Giant Head", 500)
        self._count = 0
        self._it_is_time = False
        from slay_the_spire.effect import Slow
        self.effects.add(Slow(1))

    def choose_intent(self, combat):
        if self._it_is_time:
            self.intent = Intent(IntentType.ATTACK, damage=40,
                                 description="It Is Time")
        else:
            last = self.move_history[-1] if self.move_history else None
            if last == "Count":
                self.intent = Intent(IntentType.ATTACK_DEBUFF, damage=15,
                                     description="Glare")
            elif last == "Glare":
                self.intent = Intent(IntentType.STRATEGIC,
                                     description="Count")
            else:
                if random.random() < 0.5:
                    self.intent = Intent(IntentType.ATTACK_DEBUFF, damage=15,
                                         description="Glare")
                else:
                    self.intent = Intent(IntentType.STRATEGIC,
                                         description="Count")

    def take_turn(self, combat):
        desc = self.intent.description
        if desc == "Glare":
            dmg = self.get_attack_damage(15)
            combat.deal_damage_to_player(dmg, self)
            combat.apply_effect_to_player("Weak", 1)
            print(f"  {self.name} Glares for {dmg} damage and applies 1 Weak!")
        elif desc == "Count":
            # Tracks attacks played this combat
            count = combat.player.attacks_played_this_turn if hasattr(combat.player, 'attacks_played_this_turn') else 0
            self._count += count
            print(f"  {self.name} is counting your attacks... (Count: {self._count})")
            if self._count >= 12:
                self._it_is_time = True
                print(f"  {self.name} declares: It Is Time!")
        elif desc == "It Is Time":
            dmg = self.get_attack_damage(40)
            combat.deal_damage_to_player(dmg, self)
            print(f"  {self.name}: IT IS TIME! Deals {dmg} massive damage!")
        self.move_history.append(desc)


# =============================================================================
# NEMESIS (Act 3 Elite)
# =============================================================================
class Nemesis(Enemy):
    """Scythe (45 dmg), Debuff (3 Burn into draw pile), goes Intangible.
    Alternates between attack turns and intangible turns."""

    def __init__(self):
        super().__init__("Nemesis", 185)

    def choose_intent(self, combat):
        if self.turn % 2 == 0:
            self.intent = Intent(IntentType.ATTACK, damage=45,
                                 description="Scythe")
        else:
            self.intent = Intent(IntentType.DEBUFF, description="Debuff")

    def take_turn(self, combat):
        desc = self.intent.description
        if desc == "Scythe":
            dmg = self.get_attack_damage(45)
            combat.deal_damage_to_player(dmg, self)
            print(f"  {self.name} uses Scythe for {dmg} damage!")
        elif desc == "Debuff":
            from slay_the_spire.effect import Intangible
            self.effects.add(Intangible(1))
            # Add burn cards to draw pile
            try:
                from slay_the_spire.card import create_card
                for _ in range(3):
                    burn = create_card("burn")
                    insert_idx = random.randint(0, len(combat.player.draw_pile))
                    combat.player.draw_pile.insert(insert_idx, burn)
                print(f"  {self.name} goes Intangible and shuffles 3 Burns into your draw pile!")
            except Exception:
                print(f"  {self.name} goes Intangible!")
        self.move_history.append(desc)


# =============================================================================
# REPTOMANCER (Act 3 Elite)
# =============================================================================
class ReptomancerDagger(Enemy):
    """Minion dagger: Stab (9 dmg + 1 Wound)."""

    def __init__(self):
        super().__init__("Dagger", random_hp(20, 25))
        self.is_minion = True

    def choose_intent(self, combat):
        self.intent = Intent(IntentType.ATTACK, damage=9,
                             description="Stab")

    def take_turn(self, combat):
        dmg = self.get_attack_damage(9)
        combat.deal_damage_to_player(dmg, self)
        try:
            from slay_the_spire.card import create_card
            wound = create_card("wound")
            combat.player.discard_pile.append(wound)
            print(f"  {self.name} Stabs for {dmg} damage and adds a Wound!")
        except Exception:
            print(f"  {self.name} Stabs for {dmg} damage!")
        self.move_history.append("Stab")


class Reptomancer(Enemy):
    """Summons daggers. Snake Strike (13 dmg x2), Big Bite (30 dmg)."""

    def __init__(self):
        super().__init__("Reptomancer", 180)

    def choose_intent(self, combat):
        alive_daggers = [e for e in combat.enemies
                         if e.is_alive and isinstance(e, ReptomancerDagger)]
        if len(alive_daggers) < 2 and random.random() < 0.5:
            self.intent = Intent(IntentType.STRATEGIC, description="Summon")
        else:
            last = self.move_history[-1] if self.move_history else None
            if last == "Big Bite":
                self.intent = Intent(IntentType.ATTACK, damage=13, hits=2,
                                     description="Snake Strike")
            elif last == "Snake Strike" or not last:
                if random.random() < 0.4:
                    self.intent = Intent(IntentType.ATTACK, damage=30,
                                         description="Big Bite")
                else:
                    self.intent = Intent(IntentType.ATTACK, damage=13, hits=2,
                                         description="Snake Strike")
            else:
                self.intent = Intent(IntentType.ATTACK, damage=13, hits=2,
                                     description="Snake Strike")

    def take_turn(self, combat):
        desc = self.intent.description
        if desc == "Summon":
            for _ in range(2):
                d = ReptomancerDagger()
                combat.enemies.append(d)
                d.choose_intent(combat)
            print(f"  {self.name} summons 2 Daggers!")
        elif desc == "Snake Strike":
            for _ in range(2):
                dmg = self.get_attack_damage(13)
                combat.deal_damage_to_player(dmg, self)
            print(f"  {self.name} Snake Strikes for {self.get_attack_damage(13)} damage x2!")
        elif desc == "Big Bite":
            dmg = self.get_attack_damage(30)
            combat.deal_damage_to_player(dmg, self)
            print(f"  {self.name} Big Bites for {dmg} damage!")
        self.move_history.append(desc)


# =============================================================================
# ENCOUNTER GENERATORS
# =============================================================================
def get_act3_normal_encounters():
    """Return list of possible Act 3 normal combat encounters."""
    return [
        lambda: [Darkling(), Darkling(), Darkling()],
        lambda: [OrbWalker()],
        lambda: [Spiker(), Spiker(), Spiker()],
        lambda: [Repulsor(), Repulsor()],
        lambda: [Repulsor(), Spiker()],
        lambda: [WrithingMass()],
        lambda: _create_jaw_worm_horde(),
        lambda: [Spiker(), Repulsor(), OrbWalker()],
    ]


def get_act3_elite_encounters():
    """Return list of possible Act 3 elite encounters."""
    return [
        lambda: [GiantHead()],
        lambda: [Transient()],
        lambda: [Nemesis()],
        lambda: _create_reptomancer_encounter(),
    ]


def _create_jaw_worm_horde():
    """Create a Jaw Worm Horde encounter (3 Jaw Worms)."""
    from slay_the_spire.enemies.act1 import JawWorm
    return [JawWorm(), JawWorm(), JawWorm()]


def _create_reptomancer_encounter():
    """Create a Reptomancer encounter with starting daggers."""
    rep = Reptomancer()
    daggers = [ReptomancerDagger(), ReptomancerDagger()]
    return [rep] + daggers
