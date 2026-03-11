"""Enemy base class and intent system."""
import random
from enum import Enum, auto
from slay_the_spire.effect import EffectManager


class IntentType(Enum):
    ATTACK = auto()
    DEFEND = auto()
    BUFF = auto()
    DEBUFF = auto()
    ATTACK_DEBUFF = auto()
    ATTACK_DEFEND = auto()
    ATTACK_BUFF = auto()
    STRATEGIC = auto()  # special moves
    SLEEP = auto()
    STUN = auto()
    ESCAPE = auto()
    UNKNOWN = auto()


class Intent:
    """Represents what an enemy plans to do."""

    def __init__(self, intent_type, damage=0, hits=1, block=0, description=""):
        self.intent_type = intent_type
        self.damage = damage
        self.hits = hits
        self.block = block
        self.description = description

    def display(self):
        parts = []
        if self.damage > 0:
            if self.hits > 1:
                parts.append(f"ATK {self.damage}x{self.hits}")
            else:
                parts.append(f"ATK {self.damage}")
        if self.block > 0:
            parts.append(f"DEF {self.block}")
        type_labels = {
            IntentType.BUFF: "BUFF",
            IntentType.DEBUFF: "DEBUFF",
            IntentType.STRATEGIC: "???",
            IntentType.SLEEP: "Zzz",
            IntentType.STUN: "STUN",
            IntentType.ESCAPE: "FLEE",
        }
        if self.intent_type in type_labels and self.damage == 0:
            parts.append(type_labels[self.intent_type])
        if self.intent_type == IntentType.ATTACK_DEBUFF:
            parts.append("+DEBUFF")
        elif self.intent_type == IntentType.ATTACK_DEFEND:
            parts.append("+DEF")
        elif self.intent_type == IntentType.ATTACK_BUFF:
            parts.append("+BUFF")
        return " ".join(parts) if parts else "???"


class Enemy:
    """Base class for all enemies."""

    def __init__(self, name, max_hp, hp=None):
        self.name = name
        self.max_hp = max_hp
        self.hp = hp if hp is not None else max_hp
        self.block = 0
        self.effects = EffectManager()
        self.intent = None
        self.move_history = []  # track last moves for pattern logic
        self.turn = 0
        self.is_alive = True
        self.is_minion = False
        self.gold_reward = 0  # extra gold on kill
        self.powers_applied = []

    def choose_intent(self, combat):
        """Override in subclass. Set self.intent based on AI pattern."""
        self.intent = Intent(IntentType.ATTACK, damage=5)

    def take_turn(self, combat):
        """Execute the enemy's turn. Override in subclass for custom logic."""
        pass

    def take_damage(self, amount, combat=None):
        """Apply damage to this enemy after block."""
        if amount <= 0:
            return 0
        if self.block > 0:
            if amount <= self.block:
                self.block -= amount
                return 0
            else:
                amount -= self.block
                self.block = 0
        # Intangible
        if self.effects.has("Intangible"):
            amount = 1
        self.hp -= amount
        if self.hp <= 0:
            self.hp = 0
            self.on_death(combat)
        return amount

    def gain_block(self, amount):
        self.block += amount

    def on_death(self, combat=None):
        """Called when HP reaches 0."""
        self.is_alive = False
        # Spore Cloud: apply vulnerable on death
        if self.effects.has("Spore Cloud"):
            if combat and combat.player:
                combat.apply_effect_to_player("Vulnerable", self.effects.get_stacks("Spore Cloud"))

    def start_turn(self):
        """Called at the start of enemy's turn."""
        self.block = 0
        self.turn += 1
        # Poison damage
        if self.effects.has("Poison"):
            poison = self.effects.get_stacks("Poison")
            self.hp -= poison
            self.effects.reduce("Poison", 1)  # reduce by 1 after damage
            if self.hp <= 0:
                self.hp = 0
                self.is_alive = False

    def end_turn(self):
        """Called at the end of enemy's turn."""
        self.effects.tick_turn_end()
        # Metallicize
        if self.effects.has("Metallicize"):
            self.gain_block(self.effects.get_stacks("Metallicize"))
        # Plated Armor
        if self.effects.has("Plated Armor"):
            self.gain_block(self.effects.get_stacks("Plated Armor"))
        # Ritual
        if self.effects.has("Ritual"):
            from slay_the_spire.effect import Strength
            self.effects.add(Strength(self.effects.get_stacks("Ritual")))
        # Regeneration
        if self.effects.has("Regeneration"):
            regen = self.effects.get_stacks("Regeneration")
            self.hp = min(self.max_hp, self.hp + regen)

    def get_attack_damage(self, base_damage):
        """Calculate actual damage with strength, weak, etc."""
        dmg = base_damage
        # Strength
        dmg += self.effects.get_stacks("Strength")
        # Weak: 25% less
        if self.effects.has("Weak"):
            dmg = int(dmg * 0.75)
        return max(0, dmg)

    def status_str(self):
        """Display string for enemy status."""
        parts = [f"{self.name}: HP {self.hp}/{self.max_hp}"]
        if self.block > 0:
            parts.append(f"BLK {self.block}")
        effects_str = str(self.effects)
        if effects_str != "None":
            parts.append(f"[{effects_str}]")
        if self.intent:
            # Recalculate displayed damage with strength/weak
            if self.intent.damage > 0:
                actual_dmg = self.get_attack_damage(self.intent.damage)
                display_intent = Intent(
                    self.intent.intent_type,
                    damage=actual_dmg,
                    hits=self.intent.hits,
                    block=self.intent.block,
                    description=self.intent.description
                )
                parts.append(f"Intent: {display_intent.display()}")
            else:
                parts.append(f"Intent: {self.intent.display()}")
        return " | ".join(parts)

    def __repr__(self):
        return f"{self.name}(HP:{self.hp}/{self.max_hp})"


# === Helper for creating enemies with HP ranges ===
def random_hp(low, high):
    return random.randint(low, high)
