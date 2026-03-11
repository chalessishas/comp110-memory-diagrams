"""Status effects (buffs and debuffs) system for Slay the Spire."""
from enum import Enum, auto


class EffectType(Enum):
    BUFF = auto()
    DEBUFF = auto()


class Effect:
    """A stackable buff or debuff on a combatant."""

    def __init__(self, name, effect_type, stacks=1, description=""):
        self.name = name
        self.effect_type = effect_type
        self.stacks = stacks
        self.description = description

    def __repr__(self):
        return f"{self.name}({self.stacks})"


# --- Buff/Debuff definitions ---
# Each is a factory function returning an Effect instance

# === COMMON BUFFS ===
def Strength(n=1):
    return Effect("Strength", EffectType.BUFF, n, "Deal additional damage with attacks.")

def Dexterity(n=1):
    return Effect("Dexterity", EffectType.BUFF, n, "Gain additional Block from cards.")

def Focus(n=1):
    return Effect("Focus", EffectType.BUFF, n, "Increases the effectiveness of Orb passives.")

def Artifact(n=1):
    return Effect("Artifact", EffectType.BUFF, n, "Negates the next debuff(s) applied.")

def Metallicize(n=1):
    return Effect("Metallicize", EffectType.BUFF, n, "Gain Block at the end of your turn.")

def Plated_Armor(n=1):
    return Effect("Plated Armor", EffectType.BUFF, n, "Gain Block at the end of your turn. Reduced when taking unblocked damage.")

def Thorns(n=1):
    return Effect("Thorns", EffectType.BUFF, n, "Deal damage back when attacked.")

def Barricade(n=1):
    return Effect("Barricade", EffectType.BUFF, n, "Block is not removed at the start of your turn.")

def Rage(n=1):
    return Effect("Rage", EffectType.BUFF, n, "Gain Block whenever you play an Attack.")

def Brutality(n=1):
    return Effect("Brutality", EffectType.BUFF, n, "At the start of your turn, lose 1 HP and draw 1 card.")

def Combust(n=1):
    return Effect("Combust", EffectType.BUFF, n, "At the end of your turn, lose 1 HP and deal damage to ALL enemies.")

def Dark_Embrace(n=1):
    return Effect("Dark Embrace", EffectType.BUFF, n, "Whenever a card is Exhausted, draw 1 card.")

def Evolve(n=1):
    return Effect("Evolve", EffectType.BUFF, n, "Whenever a Status card is drawn, draw card(s).")

def Feel_No_Pain(n=1):
    return Effect("Feel No Pain", EffectType.BUFF, n, "Whenever a card is Exhausted, gain Block.")

def Fire_Breathing(n=1):
    return Effect("Fire Breathing", EffectType.BUFF, n, "Whenever a Status or Curse is drawn, deal damage to ALL enemies.")

def Flame_Barrier(n=1):
    return Effect("Flame Barrier", EffectType.BUFF, n, "When attacked, deal damage back.")

def Juggernaut(n=1):
    return Effect("Juggernaut", EffectType.BUFF, n, "Whenever you gain Block, deal damage to a random enemy.")

def Berserk(n=1):
    return Effect("Berserk", EffectType.BUFF, n, "At the start of your turn, gain Energy.")

def Corruption(n=1):
    return Effect("Corruption", EffectType.BUFF, n, "Skills cost 0. Whenever you play a Skill, Exhaust it.")

def Demon_Form(n=1):
    return Effect("Demon Form", EffectType.BUFF, n, "At the start of your turn, gain Strength.")

def Double_Tap(n=1):
    return Effect("Double Tap", EffectType.BUFF, n, "The next Attack is played twice.")

def Rupture(n=1):
    return Effect("Rupture", EffectType.BUFF, n, "Whenever you lose HP from a card, gain Strength.")

def Rebound(n=1):
    return Effect("Rebound", EffectType.BUFF, n, "The next card you play is put on top of your draw pile.")

def Noxious_Fumes(n=1):
    return Effect("Noxious Fumes", EffectType.BUFF, n, "At the start of your turn, apply Poison to ALL enemies.")

def Accuracy(n=1):
    return Effect("Accuracy", EffectType.BUFF, n, "Shivs deal additional damage.")

def After_Image(n=1):
    return Effect("After Image", EffectType.BUFF, n, "Whenever you play a card, gain Block.")

def Envenom(n=1):
    return Effect("Envenom", EffectType.BUFF, n, "Whenever you deal unblocked attack damage, apply Poison.")

def Infinite_Blades(n=1):
    return Effect("Infinite Blades", EffectType.BUFF, n, "At the start of your turn, add a Shiv to your hand.")

def A_Thousand_Cuts(n=1):
    return Effect("A Thousand Cuts", EffectType.BUFF, n, "Whenever you play a card, deal damage to ALL enemies.")

def Tools_of_the_Trade(n=1):
    return Effect("Tools of the Trade", EffectType.BUFF, n, "At the start of your turn, draw 1 card and discard 1 card.")

def Well_Laid_Plans(n=1):
    return Effect("Well-Laid Plans", EffectType.BUFF, n, "At the end of your turn, Retain up to card(s).")

def Phantasmal_Killer(n=1):
    return Effect("Phantasmal Killer", EffectType.BUFF, n, "Your next Attack deals double damage.")

def Nightmare_Buff(n=1):
    return Effect("Nightmare", EffectType.BUFF, n, "Next turn, add copies of a card to your hand.")

def Creative_AI_Buff(n=1):
    return Effect("Creative AI", EffectType.BUFF, n, "At the start of your turn, add a random Power to your hand.")

def Echo_Form(n=1):
    return Effect("Echo Form", EffectType.BUFF, n, "The first card you play each turn is played twice.")

def Electrodynamics(n=1):
    return Effect("Electrodynamics", EffectType.BUFF, n, "Lightning hits ALL enemies. Whenever you receive unblocked damage, Channel Lightning.")

def Heatsink(n=1):
    return Effect("Heatsink", EffectType.BUFF, n, "Whenever you play a Power, draw 1 card.")

def Hello_World(n=1):
    return Effect("Hello World", EffectType.BUFF, n, "At the start of your turn, add a random Common card to your hand.")

def Loop(n=1):
    return Effect("Loop", EffectType.BUFF, n, "Your first Orb triggers its passive an additional time.")

def Machine_Learning(n=1):
    return Effect("Machine Learning", EffectType.BUFF, n, "At the start of your turn, draw 1 additional card.")

def Storm(n=1):
    return Effect("Storm", EffectType.BUFF, n, "Whenever you play a Power, Channel 1 Lightning.")

def Buffer(n=1):
    return Effect("Buffer", EffectType.BUFF, n, "Prevent the next time you would lose HP.")

def Mantra(n=1):
    return Effect("Mantra", EffectType.BUFF, n, "When you reach 10 Mantra, enter Divinity.")

def Devotion(n=1):
    return Effect("Devotion", EffectType.BUFF, n, "At the start of your turn, gain Mantra.")

def Establishment(n=1):
    return Effect("Establishment", EffectType.BUFF, n, "Whenever a card is Retained, reduce its cost by 1.")

def Fasting(n=1):
    return Effect("Fasting", EffectType.BUFF, n, "Gain additional Energy each turn. Lose Strength and Dexterity.")

def Like_Water(n=1):
    return Effect("Like Water", EffectType.BUFF, n, "If in Calm, gain Block at end of turn.")

def Mental_Fortress(n=1):
    return Effect("Mental Fortress", EffectType.BUFF, n, "Whenever you change Stance, gain Block.")

def Study(n=1):
    return Effect("Study", EffectType.BUFF, n, "At the end of your turn, add an Insight to your draw pile.")

def Battle_Hymn(n=1):
    return Effect("Battle Hymn", EffectType.BUFF, n, "At the start of your turn, add Smite(s) to your hand.")

def Foresight(n=1):
    return Effect("Foresight", EffectType.BUFF, n, "At the start of your turn, Scry.")

def Omega(n=1):
    return Effect("Omega", EffectType.BUFF, n, "At the end of your turn, deal 50 damage to ALL enemies.")

def Deva_Form(n=1):
    return Effect("Deva Form", EffectType.BUFF, n, "At the start of your turn, gain Energy and increase this gain.")

def Master_Reality(n=1):
    return Effect("Master Reality", EffectType.BUFF, n, "Whenever a card is created during combat, Upgrade it.")

def Rushdown(n=1):
    return Effect("Rushdown", EffectType.BUFF, n, "Whenever you enter Wrath, draw cards.")

def Wireheading(n=1):
    return Effect("Wireheading", EffectType.BUFF, n, "At the start of your turn, gain Energy.")

def Intangible(n=1):
    return Effect("Intangible", EffectType.BUFF, n, "Reduce ALL damage taken and HP loss to 1.")

def Regeneration(n=1):
    return Effect("Regeneration", EffectType.BUFF, n, "Heal HP at the end of turn. Reduce by 1 each turn.")

def Panache(n=1):
    return Effect("Panache", EffectType.BUFF, n, "Every 5 cards played, deal 10 damage to ALL enemies.")

def Sadistic(n=1):
    return Effect("Sadistic", EffectType.BUFF, n, "Whenever you apply a debuff, deal damage.")

def Amplify(n=1):
    return Effect("Amplify", EffectType.BUFF, n, "The next Power you play is played twice.")

def Burst(n=1):
    return Effect("Burst", EffectType.BUFF, n, "The next Skill is played twice.")

def Pen_Nib(n=1):
    return Effect("Pen Nib", EffectType.BUFF, n, "Your next Attack deals double damage.")

def Vigor(n=1):
    return Effect("Vigor", EffectType.BUFF, n, "Your next Attack deals additional damage.")

def Ritual(n=1):
    return Effect("Ritual", EffectType.BUFF, n, "At the end of your turn, gain Strength.")

def Draw_Reduction(n=1):
    return Effect("Draw Reduction", EffectType.BUFF, n, "Draw fewer cards next turn.")

def No_Draw(n=1):
    return Effect("No Draw", EffectType.BUFF, n, "You may not draw any additional cards.")

def Energized(n=1):
    return Effect("Energized", EffectType.BUFF, n, "Gain additional Energy next turn.")

def Draw_Card(n=1):
    return Effect("Draw Card", EffectType.BUFF, n, "Draw additional cards next turn.")

def Next_Turn_Block(n=1):
    return Effect("Next Turn Block", EffectType.BUFF, n, "Gain Block at the start of next turn.")


# === COMMON DEBUFFS ===
def Weak(n=1):
    return Effect("Weak", EffectType.DEBUFF, n, "Deal 25% less damage with attacks.")

def Vulnerable(n=1):
    return Effect("Vulnerable", EffectType.DEBUFF, n, "Take 50% more damage from attacks.")

def Frail(n=1):
    return Effect("Frail", EffectType.DEBUFF, n, "Gain 25% less Block from cards.")

def Poison(n=1):
    return Effect("Poison", EffectType.DEBUFF, n, "Lose HP at the start of turn, then reduce by 1.")

def Constricted(n=1):
    return Effect("Constricted", EffectType.DEBUFF, n, "Take damage at the end of your turn.")

def Entangled(n=1):
    return Effect("Entangled", EffectType.DEBUFF, n, "You may not play Attacks this turn.")

def Hex(n=1):
    return Effect("Hex", EffectType.DEBUFF, n, "Whenever you play a non-Attack card, add a Daze to your draw pile.")

def No_Block(n=1):
    return Effect("No Block", EffectType.DEBUFF, n, "You may not gain Block.")

def Choked(n=1):
    return Effect("Choked", EffectType.DEBUFF, n, "Whenever you play a card, lose HP.")

def Bias(n=1):
    return Effect("Bias", EffectType.DEBUFF, n, "At the start of your turn, lose Focus.")

def Lock_On(n=1):
    return Effect("Lock-On", EffectType.DEBUFF, n, "Lightning and Dark orbs deal 50% more damage.")

def Mark(n=1):
    return Effect("Mark", EffectType.DEBUFF, n, "Takes additional damage from specified attacks.")

def Slow(n=1):
    return Effect("Slow", EffectType.DEBUFF, n, "Lose 10% Strength for each card played.")

def Shackled(n=1):
    return Effect("Shackled", EffectType.DEBUFF, n, "Regain Strength at end of turn.")

def Wraith_Form_Effect(n=1):
    return Effect("Wraith Form", EffectType.DEBUFF, n, "Lose Dexterity at the start of your turn.")


# === ENEMY-SPECIFIC BUFFS ===
def Angry(n=1):
    return Effect("Angry", EffectType.BUFF, n, "Gain Strength when taking damage.")

def Curl_Up(n=1):
    return Effect("Curl Up", EffectType.BUFF, n, "Gain Block on first unblocked damage.")

def Enrage(n=1):
    return Effect("Enrage", EffectType.BUFF, n, "Gain Strength when a Skill is played.")

def Malleable(n=1):
    return Effect("Malleable", EffectType.BUFF, n, "Gain Block when attacked. Increases each time.")

def Mode_Shift(n=1):
    return Effect("Mode Shift", EffectType.BUFF, n, "After taking enough damage, changes behavior.")

def Sharp_Hide(n=1):
    return Effect("Sharp Hide", EffectType.BUFF, n, "Deal damage back when attacked.")

def Spore_Cloud(n=1):
    return Effect("Spore Cloud", EffectType.BUFF, n, "On death, apply Vulnerable to player.")

def Thievery(n=1):
    return Effect("Thievery", EffectType.BUFF, n, "Steal gold on attack.")

def Time_Warp(n=1):
    return Effect("Time Warp", EffectType.BUFF, n, "After 12 cards are played, gain Strength and end turn.")

def Shifting(n=1):
    return Effect("Shifting", EffectType.BUFF, n, "Lose Strength at end of turn equal to damage blocked.")

def Fading(n=1):
    return Effect("Fading", EffectType.BUFF, n, "Die when this reaches 0.")

def Invincible(n=1):
    return Effect("Invincible", EffectType.BUFF, n, "Can only take this much damage per turn.")

def Minion(n=1):
    return Effect("Minion", EffectType.BUFF, n, "Flees when alone.")

def Split(n=1):
    return Effect("Split", EffectType.BUFF, n, "Splits into 2 when HP reaches 0.")

def Stasis(n=1):
    return Effect("Stasis", EffectType.BUFF, n, "On death, return stolen card.")

def Unawakened(n=1):
    return Effect("Unawakened", EffectType.BUFF, n, "Revives with new moveset when killed.")

def Beat_of_Death(n=1):
    return Effect("Beat of Death", EffectType.BUFF, n, "Deal damage whenever a card is played.")

def Painful_Stabs(n=1):
    return Effect("Painful Stabs", EffectType.BUFF, n, "When taking unblocked damage, add Wound to discard.")

def Curiosity(n=1):
    return Effect("Curiosity", EffectType.BUFF, n, "Gain Strength when player plays a Power.")

def Reactive(n=1):
    return Effect("Reactive", EffectType.BUFF, n, "When taking unblocked damage, change intent to attack.")

def Flight(n=1):
    return Effect("Flight", EffectType.BUFF, n, "Take 50% less damage. Reduced by 1 when attacked.")


class EffectManager:
    """Manages effects on a combatant."""

    def __init__(self):
        self.effects = {}  # name -> Effect

    def add(self, effect):
        """Add or stack an effect."""
        if effect.name in self.effects:
            self.effects[effect.name].stacks += effect.stacks
        else:
            self.effects[effect.name] = effect

    def remove(self, name):
        """Remove an effect entirely."""
        self.effects.pop(name, None)

    def has(self, name):
        """Check if an effect exists."""
        return name in self.effects

    def get(self, name):
        """Get an effect, returns None if not present."""
        return self.effects.get(name)

    def get_stacks(self, name):
        """Get stack count of an effect, 0 if not present."""
        e = self.effects.get(name)
        return e.stacks if e else 0

    def reduce(self, name, amount=1):
        """Reduce stacks of an effect. Remove if reaches 0."""
        if name in self.effects:
            self.effects[name].stacks -= amount
            if self.effects[name].stacks <= 0:
                del self.effects[name]

    def tick_turn_start(self):
        """Process effects at the start of turn. Returns dict of triggered effects."""
        triggered = {}
        # Weak, Vulnerable, Frail decrement at end of owner's turn (handled in tick_turn_end)
        return triggered

    def tick_turn_end(self):
        """Process effects at the end of turn. Returns list of effects to remove."""
        to_remove = []
        for name in list(self.effects.keys()):
            e = self.effects[name]
            if name in ("Weak", "Vulnerable", "Frail"):
                e.stacks -= 1
                if e.stacks <= 0:
                    to_remove.append(name)
            elif name == "Regeneration":
                e.stacks -= 1
                if e.stacks <= 0:
                    to_remove.append(name)
            elif name == "Intangible":
                e.stacks -= 1
                if e.stacks <= 0:
                    to_remove.append(name)
            elif name == "Fading":
                e.stacks -= 1
            elif name in ("Double Tap", "Burst", "Amplify", "Phantasmal Killer"):
                pass  # consumed on use
            elif name in ("Entangled",):
                to_remove.append(name)
            elif name == "Pen Nib":
                pass  # consumed on use
        for name in to_remove:
            self.remove(name)
        return to_remove

    def get_buffs(self):
        return {n: e for n, e in self.effects.items() if e.effect_type == EffectType.BUFF}

    def get_debuffs(self):
        return {n: e for n, e in self.effects.items() if e.effect_type == EffectType.DEBUFF}

    def clear(self):
        self.effects.clear()

    def __repr__(self):
        parts = []
        for e in self.effects.values():
            parts.append(f"{e.name}({e.stacks})")
        return ", ".join(parts) if parts else "None"
