"""Elite enemy definitions for all acts in Slay the Spire."""
import random
from slay_the_spire.enemy import Enemy, Intent, IntentType, random_hp
from slay_the_spire.effect import (
    Strength, Vulnerable, Weak, Frail, Metallicize, Enrage,
    Intangible, Effect, EffectType,
)


# =============================================================================
# ACT 1 ELITES
# =============================================================================


class GremlinNob(Enemy):
    """Act 1 Elite. Enrages when the player plays Skills.
    Rush (32 dmg), Skull Bash (8 dmg + 2 Vulnerable).
    Gains 2 Strength each time player plays a Skill (via Enrage effect).
    """

    def __init__(self):
        super().__init__("Gremlin Nob", random_hp(106, 111))
        self.effects.add(Enrage(2))

    def choose_intent(self, combat):
        if self.turn == 0:
            # Always opens with Rush
            self.intent = Intent(IntentType.ATTACK, damage=32, description="Rush")
        else:
            last = self.move_history[-1] if self.move_history else None
            if last == "skull_bash":
                self.intent = Intent(IntentType.ATTACK, damage=32, description="Rush")
            else:
                # 33% Skull Bash, 67% Rush (never 3x same in a row)
                if random.random() < 0.33:
                    self.intent = Intent(
                        IntentType.ATTACK_DEBUFF, damage=8,
                        description="Skull Bash",
                    )
                else:
                    self.intent = Intent(IntentType.ATTACK, damage=32, description="Rush")

    def take_turn(self, combat):
        if "Rush" in (self.intent.description or ""):
            dmg = self.get_attack_damage(32)
            combat.deal_damage_to_player(dmg, self)
            print(f"  {self.name} uses Rush for {dmg} damage!")
            self.move_history.append("rush")
        else:
            dmg = self.get_attack_damage(8)
            combat.deal_damage_to_player(dmg, self)
            combat.apply_effect_to_player("Vulnerable", 2)
            print(f"  {self.name} uses Skull Bash for {dmg} damage and applies 2 Vulnerable!")
            self.move_history.append("skull_bash")


class Lagavulin(Enemy):
    """Act 1 Elite. Sleeps for 3 turns with 8 Metallicize.
    Wakes up when attacked or after 3 idle turns.
    Attack (18 dmg), Siphon Soul (-1 Str, -1 Dex to player).
    """

    def __init__(self):
        super().__init__("Lagavulin", random_hp(109, 111))
        self.asleep = True
        self.sleep_turns = 0
        self.effects.add(Metallicize(8))
        self.was_damaged = False

    def take_damage(self, amount, combat=None):
        actual = super().take_damage(amount, combat)
        if actual > 0 and self.asleep:
            self.was_damaged = True
        return actual

    def choose_intent(self, combat):
        if self.asleep:
            if self.was_damaged or self.sleep_turns >= 3:
                self._wake_up()
                self.intent = Intent(IntentType.ATTACK, damage=18, description="Attack")
            else:
                self.intent = Intent(IntentType.SLEEP, description="Sleeping")
        else:
            last = self.move_history[-1] if self.move_history else None
            if last == "siphon_soul":
                self.intent = Intent(IntentType.ATTACK, damage=18, description="Attack")
            elif last == "attack":
                self.intent = Intent(IntentType.ATTACK, damage=18, description="Attack")
                # Two attacks then siphon pattern
                if len(self.move_history) >= 2 and self.move_history[-2] == "attack":
                    self.intent = Intent(IntentType.DEBUFF, description="Siphon Soul")
            else:
                self.intent = Intent(IntentType.ATTACK, damage=18, description="Attack")

    def _wake_up(self):
        self.asleep = False
        self.effects.remove("Metallicize")
        print(f"  {self.name} wakes up!")

    def take_turn(self, combat):
        if self.asleep:
            self.sleep_turns += 1
            print(f"  {self.name} is sleeping... (turn {self.sleep_turns})")
            self.move_history.append("sleep")
            return

        if self.intent.description == "Siphon Soul":
            combat.apply_effect_to_player("Strength", -1)
            combat.apply_effect_to_player("Dexterity", -1)
            print(f"  {self.name} uses Siphon Soul! Player loses 1 Strength and 1 Dexterity!")
            self.move_history.append("siphon_soul")
        else:
            dmg = self.get_attack_damage(18)
            combat.deal_damage_to_player(dmg, self)
            print(f"  {self.name} attacks for {dmg} damage!")
            self.move_history.append("attack")


class Sentry(Enemy):
    """Act 1 Elite. Three Sentries fight together.
    Alternate between Bolt (9 dmg) and adding Dazed status cards.
    Pattern varies per sentry position.
    """

    def __init__(self, position=0):
        super().__init__(f"Sentry", random_hp(38, 42))
        self.position = position  # 0=left, 1=middle, 2=right

    def choose_intent(self, combat):
        # Position determines starting pattern:
        # Left(0) and Right(2) start with Bolt, Middle(1) starts with Daze
        if self.turn == 0:
            if self.position == 1:
                self.intent = Intent(IntentType.DEBUFF, description="Daze")
            else:
                self.intent = Intent(IntentType.ATTACK, damage=9, description="Bolt")
        else:
            last = self.move_history[-1] if self.move_history else None
            if last == "bolt":
                self.intent = Intent(IntentType.DEBUFF, description="Daze")
            else:
                self.intent = Intent(IntentType.ATTACK, damage=9, description="Bolt")

    def take_turn(self, combat):
        if self.intent.description == "Bolt":
            dmg = self.get_attack_damage(9)
            combat.deal_damage_to_player(dmg, self)
            print(f"  {self.name} fires Bolt for {dmg} damage!")
            self.move_history.append("bolt")
        else:
            # Add 2 Dazed status cards to discard pile
            from slay_the_spire.card import create_card
            for _ in range(2):
                try:
                    daze = create_card("dazed")
                    combat.player.discard_pile.append(daze)
                except Exception:
                    pass
            print(f"  {self.name} adds 2 Dazed to your discard pile!")
            self.move_history.append("daze")


# =============================================================================
# ACT 2 ELITES
# =============================================================================


class SlaverRed(Enemy):
    """Act 2 Elite (paired with Blue). Stab (13 dmg), Scrape (8 + Vulnerable),
    Entangle (can't play attacks for 1 turn).
    """

    def __init__(self):
        super().__init__("Slaver (Red)", random_hp(46, 50))

    def choose_intent(self, combat):
        if self.turn == 0:
            self.intent = Intent(IntentType.ATTACK, damage=13, description="Stab")
        else:
            last = self.move_history[-1] if self.move_history else None
            roll = random.random()
            if last != "entangle" and not combat.player.effects.has("Entangled") and roll < 0.25:
                self.intent = Intent(IntentType.DEBUFF, description="Entangle")
            elif roll < 0.55:
                self.intent = Intent(
                    IntentType.ATTACK_DEBUFF, damage=8,
                    description="Scrape",
                )
            else:
                self.intent = Intent(IntentType.ATTACK, damage=13, description="Stab")

    def take_turn(self, combat):
        desc = self.intent.description or ""
        if desc == "Stab":
            dmg = self.get_attack_damage(13)
            combat.deal_damage_to_player(dmg, self)
            print(f"  {self.name} stabs for {dmg} damage!")
            self.move_history.append("stab")
        elif desc == "Scrape":
            dmg = self.get_attack_damage(8)
            combat.deal_damage_to_player(dmg, self)
            combat.apply_effect_to_player("Vulnerable", 1)
            print(f"  {self.name} scrapes for {dmg} damage and applies Vulnerable!")
            self.move_history.append("scrape")
        elif desc == "Entangle":
            combat.apply_effect_to_player("Entangled", 1)
            print(f"  {self.name} entangles you! Cannot play Attacks this turn!")
            self.move_history.append("entangle")


class SlaverBlue(Enemy):
    """Act 2 Elite (paired with Red). Stab (12 dmg), Rake (7 + Weak)."""

    def __init__(self):
        super().__init__("Slaver (Blue)", random_hp(46, 50))

    def choose_intent(self, combat):
        if self.turn == 0:
            self.intent = Intent(IntentType.ATTACK, damage=12, description="Stab")
        else:
            last = self.move_history[-1] if self.move_history else None
            if last == "rake" or random.random() < 0.5:
                self.intent = Intent(IntentType.ATTACK, damage=12, description="Stab")
            else:
                self.intent = Intent(
                    IntentType.ATTACK_DEBUFF, damage=7,
                    description="Rake",
                )

    def take_turn(self, combat):
        desc = self.intent.description or ""
        if desc == "Stab":
            dmg = self.get_attack_damage(12)
            combat.deal_damage_to_player(dmg, self)
            print(f"  {self.name} stabs for {dmg} damage!")
            self.move_history.append("stab")
        elif desc == "Rake":
            dmg = self.get_attack_damage(7)
            combat.deal_damage_to_player(dmg, self)
            combat.apply_effect_to_player("Weak", 1)
            print(f"  {self.name} rakes for {dmg} damage and applies Weak!")
            self.move_history.append("rake")


class BookOfStabbing(Enemy):
    """Act 2 Elite. Multi Stab attack that gains more hits each turn.
    Starts with 6 damage x multiple hits, gaining +1 hit per turn.
    """

    def __init__(self):
        super().__init__("Book of Stabbing", 168)
        self.stab_count = 3  # starting number of hits

    def choose_intent(self, combat):
        self.intent = Intent(
            IntentType.ATTACK, damage=6, hits=self.stab_count,
            description="Multi Stab",
        )

    def take_turn(self, combat):
        dmg = self.get_attack_damage(6)
        total = 0
        for _ in range(self.stab_count):
            combat.deal_damage_to_player(dmg, self)
            total += dmg
        print(f"  {self.name} stabs {self.stab_count} times for {dmg} each! (Total: {total})")
        self.stab_count += 1
        self.move_history.append("multi_stab")


class GremlinMinion(Enemy):
    """A small Gremlin summoned by Gremlin Leader."""

    def __init__(self):
        hp = random_hp(12, 16)
        super().__init__("Gremlin", hp)
        self.is_minion = True

    def choose_intent(self, combat):
        self.intent = Intent(IntentType.ATTACK, damage=6, description="Scratch")

    def take_turn(self, combat):
        dmg = self.get_attack_damage(6)
        combat.deal_damage_to_player(dmg, self)
        print(f"  {self.name} scratches for {dmg} damage!")
        self.move_history.append("scratch")


class GremlinLeader(Enemy):
    """Act 2 Elite. Summons Gremlin minions, buffs them with Strength.
    Rally (+3 Str to all Gremlins), Encourage (buff + block).
    """

    def __init__(self):
        super().__init__("Gremlin Leader", random_hp(140, 148))
        self.gremlins = []

    def choose_intent(self, combat):
        alive_gremlins = [g for g in self.gremlins if g.is_alive]
        if len(alive_gremlins) < 2:
            self.intent = Intent(IntentType.STRATEGIC, description="Summon")
        else:
            last = self.move_history[-1] if self.move_history else None
            if last == "rally" or random.random() < 0.5:
                self.intent = Intent(IntentType.BUFF, block=10, description="Encourage")
            else:
                self.intent = Intent(IntentType.BUFF, description="Rally")

    def take_turn(self, combat):
        desc = self.intent.description or ""
        if desc == "Summon":
            # Summon up to 2 Gremlins
            while len([g for g in self.gremlins if g.is_alive]) < 3:
                gremlin = GremlinMinion()
                self.gremlins.append(gremlin)
                combat.enemies.append(gremlin)
                gremlin.choose_intent(combat)
            print(f"  {self.name} summons Gremlins!")
            self.move_history.append("summon")
        elif desc == "Rally":
            for g in self.gremlins:
                if g.is_alive:
                    g.effects.add(Strength(3))
            self.effects.add(Strength(3))
            print(f"  {self.name} rallies! All Gremlins gain 3 Strength!")
            self.move_history.append("rally")
        elif desc == "Encourage":
            for g in self.gremlins:
                if g.is_alive:
                    g.effects.add(Strength(3))
                    g.gain_block(6)
            self.gain_block(10)
            print(f"  {self.name} encourages! Gremlins gain 3 Str + Block, Leader gains 10 Block!")
            self.move_history.append("encourage")


# =============================================================================
# ACT 3 ELITES
# =============================================================================


class GiantHead(Enemy):
    """Act 3 Elite. Count (slow building), Glare (35 dmg),
    It Is Time (grows in damage). Punishes low card play.
    """

    def __init__(self):
        super().__init__("Giant Head", 500)
        self.slow_stacks = 0
        self.it_is_time_count = 0
        self.effects.add(Effect("Slow", EffectType.DEBUFF, 0, "Takes more damage per card played."))

    def choose_intent(self, combat):
        if self.turn == 0:
            self.intent = Intent(IntentType.ATTACK, damage=13, description="Count")
        else:
            last = self.move_history[-1] if self.move_history else None
            if self.turn <= 4:
                if last == "glare" or random.random() < 0.6:
                    self.intent = Intent(IntentType.ATTACK, damage=13, description="Count")
                else:
                    self.intent = Intent(IntentType.ATTACK, damage=35, description="Glare")
            else:
                # After turn 5, It Is Time starts building
                self.it_is_time_count += 5
                base = 30 + self.it_is_time_count
                self.intent = Intent(IntentType.ATTACK, damage=base, description="It Is Time")

    def take_turn(self, combat):
        desc = self.intent.description or ""
        if desc == "Count":
            dmg = self.get_attack_damage(13)
            combat.deal_damage_to_player(dmg, self)
            print(f"  {self.name} counts for {dmg} damage!")
            self.move_history.append("count")
        elif desc == "Glare":
            dmg = self.get_attack_damage(35)
            combat.deal_damage_to_player(dmg, self)
            print(f"  {self.name} glares for {dmg} damage!")
            self.move_history.append("glare")
        elif desc == "It Is Time":
            dmg = self.get_attack_damage(self.intent.damage)
            combat.deal_damage_to_player(dmg, self)
            print(f"  {self.name} declares IT IS TIME for {dmg} damage!")
            self.move_history.append("it_is_time")


class Nemesis(Enemy):
    """Act 3 Elite. Scythe (45 dmg), Debilitate (add 3 Burns to draw pile).
    Goes intangible every other turn.
    """

    def __init__(self):
        super().__init__("Nemesis", 185)

    def choose_intent(self, combat):
        # Nemesis alternates: attack, intangible+debilitate, attack, etc.
        if self.turn % 3 == 0:
            self.intent = Intent(IntentType.ATTACK, damage=45, description="Scythe")
        elif self.turn % 3 == 1:
            self.intent = Intent(IntentType.DEBUFF, description="Debilitate")
        else:
            self.intent = Intent(IntentType.ATTACK, damage=45, description="Scythe")

    def take_turn(self, combat):
        desc = self.intent.description or ""
        if desc == "Scythe":
            dmg = self.get_attack_damage(45)
            combat.deal_damage_to_player(dmg, self)
            print(f"  {self.name} swings Scythe for {dmg} damage!")
            self.move_history.append("scythe")
        elif desc == "Debilitate":
            # Add 3 Burns to draw pile and go intangible
            from slay_the_spire.card import create_card
            for _ in range(3):
                try:
                    burn = create_card("burn")
                    pos = random.randint(0, max(0, len(combat.player.draw_pile)))
                    combat.player.draw_pile.insert(pos, burn)
                except Exception:
                    pass
            self.effects.add(Intangible(1))
            print(f"  {self.name} debilitates! 3 Burns added to draw pile! Nemesis becomes Intangible!")
            self.move_history.append("debilitate")


class DaggerMinion(Enemy):
    """Minion summoned by Reptomancer. 9 damage attack."""

    def __init__(self):
        super().__init__("Dagger", random_hp(20, 25))
        self.is_minion = True

    def choose_intent(self, combat):
        self.intent = Intent(IntentType.ATTACK, damage=9, description="Stab")

    def take_turn(self, combat):
        dmg = self.get_attack_damage(9)
        combat.deal_damage_to_player(dmg, self)
        print(f"  {self.name} stabs for {dmg} damage!")
        self.move_history.append("stab")


class Reptomancer(Enemy):
    """Act 3 Elite. Summons Dagger minions, Big Bite (30 dmg),
    Snake Strike (16 dmg x2).
    """

    def __init__(self):
        super().__init__("Reptomancer", 180)
        self.daggers = []

    def choose_intent(self, combat):
        alive_daggers = [d for d in self.daggers if d.is_alive]
        if self.turn == 0:
            self.intent = Intent(IntentType.STRATEGIC, description="Summon Daggers")
        elif len(alive_daggers) == 0:
            self.intent = Intent(IntentType.STRATEGIC, description="Summon Daggers")
        else:
            last = self.move_history[-1] if self.move_history else None
            roll = random.random()
            if last != "snake_strike" and roll < 0.35:
                self.intent = Intent(
                    IntentType.ATTACK, damage=16, hits=2,
                    description="Snake Strike",
                )
            else:
                self.intent = Intent(IntentType.ATTACK, damage=30, description="Big Bite")

    def take_turn(self, combat):
        desc = self.intent.description or ""
        if desc == "Summon Daggers":
            count = 0
            while len([d for d in self.daggers if d.is_alive]) < 2 and count < 2:
                dagger = DaggerMinion()
                self.daggers.append(dagger)
                combat.enemies.append(dagger)
                dagger.choose_intent(combat)
                count += 1
            print(f"  {self.name} summons Daggers!")
            self.move_history.append("summon")
        elif desc == "Big Bite":
            dmg = self.get_attack_damage(30)
            combat.deal_damage_to_player(dmg, self)
            print(f"  {self.name} Big Bite for {dmg} damage!")
            self.move_history.append("big_bite")
        elif desc == "Snake Strike":
            dmg = self.get_attack_damage(16)
            for _ in range(2):
                combat.deal_damage_to_player(dmg, self)
            print(f"  {self.name} Snake Strike for {dmg}x2 damage!")
            self.move_history.append("snake_strike")


# =============================================================================
# ENCOUNTER FACTORY FUNCTIONS
# =============================================================================


def get_act1_elites():
    """Return list of factory functions for Act 1 elite encounters."""
    return [
        lambda: [GremlinNob()],
        lambda: [Lagavulin()],
        lambda: [Sentry(0), Sentry(1), Sentry(2)],
    ]


def get_act2_elites():
    """Return list of factory functions for Act 2 elite encounters."""
    return [
        lambda: [SlaverRed(), SlaverBlue()],
        lambda: [BookOfStabbing()],
        lambda: _create_gremlin_leader_encounter(),
    ]


def _create_gremlin_leader_encounter():
    """Create Gremlin Leader encounter with initial minions."""
    leader = GremlinLeader()
    g1 = GremlinMinion()
    g2 = GremlinMinion()
    leader.gremlins = [g1, g2]
    return [leader, g1, g2]


def get_act3_elites():
    """Return list of factory functions for Act 3 elite encounters."""
    return [
        lambda: [GiantHead()],
        lambda: [Nemesis()],
        lambda: _create_reptomancer_encounter(),
    ]


def _create_reptomancer_encounter():
    """Create Reptomancer encounter with initial daggers."""
    repto = Reptomancer()
    d1 = DaggerMinion()
    d2 = DaggerMinion()
    repto.daggers = [d1, d2]
    return [repto, d1, d2]
