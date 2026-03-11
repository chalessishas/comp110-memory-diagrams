"""Player state management."""
import random
from slay_the_spire.effect import EffectManager
from slay_the_spire.orb import OrbManager
from slay_the_spire.stance import StanceManager, StanceType
from slay_the_spire.card import CardType


class Player:
    """Represents the player character."""

    def __init__(self, name, max_hp, character_class, starter_relic=None):
        self.name = name
        self.character_class = character_class  # "ironclad", "silent", "defect", "watcher"
        self.max_hp = max_hp
        self.hp = max_hp
        self.gold = 99
        self.energy = 0
        self.max_energy = 3
        self.block = 0

        # Deck management
        self.deck = []           # master deck (all owned cards)
        self.draw_pile = []
        self.hand = []
        self.discard_pile = []
        self.exhaust_pile = []

        # Card draw
        self.base_draw = 5
        self.extra_draw = 0  # temporary draw bonuses

        # Effects
        self.effects = EffectManager()

        # Orbs (Defect)
        self.orbs = OrbManager(max_orbs=3 if character_class == "defect" else 0)

        # Stance (Watcher)
        self.stance = StanceManager()

        # Relics
        self.relics = []

        # Potions
        self.potions = [None, None, None]  # 3 potion slots
        self.max_potions = 3

        # Run tracking
        self.floor = 0
        self.act = 1
        self.ascension = 0
        self.cards_played_this_turn = 0
        self.cards_played_this_combat = 0
        self.attacks_played_this_turn = 0
        self.skills_played_this_turn = 0
        self.powers_played_this_turn = 0
        self.times_damaged_this_combat = 0
        self.damage_taken_this_combat = 0
        self.gold_gained_this_combat = 0
        self.hp_lost_this_combat = 0

    # === HP Management ===
    def heal(self, amount):
        old_hp = self.hp
        self.hp = min(self.max_hp, self.hp + amount)
        return self.hp - old_hp

    def lose_hp(self, amount):
        """Lose HP directly (not attack damage, bypasses block)."""
        if self.effects.has("Buffer"):
            self.effects.reduce("Buffer")
            return 0
        if self.effects.has("Intangible"):
            amount = 1
        self.hp -= amount
        self.hp_lost_this_combat += amount
        if self.hp <= 0:
            self.hp = 0
        return amount

    def take_damage(self, amount):
        """Take attack damage (reduced by block, then HP)."""
        if amount <= 0:
            return 0

        # Vulnerable: take 50% more
        if self.effects.has("Vulnerable"):
            amount = int(amount * 1.5)

        # Stance damage multiplier (Wrath: 2x incoming)
        amount = int(amount * self.stance.get_damage_taken_multiplier())

        # Buffer
        if self.effects.has("Buffer") and amount > 0:
            self.effects.reduce("Buffer")
            return 0

        # Intangible
        if self.effects.has("Intangible"):
            amount = 1

        # Apply block
        blocked = 0
        if self.block > 0:
            if amount <= self.block:
                self.block -= amount
                return 0
            else:
                blocked = self.block
                amount -= self.block
                self.block = 0

        # Reduce HP
        self.hp -= amount
        self.times_damaged_this_combat += 1
        self.damage_taken_this_combat += amount
        self.hp_lost_this_combat += amount
        if self.hp <= 0:
            self.hp = 0
        return amount

    def gain_block(self, amount):
        """Gain block, modified by Dexterity and Frail."""
        # Dexterity
        amount += self.effects.get_stacks("Dexterity")
        # Frail: 25% less
        if self.effects.has("Frail"):
            amount = int(amount * 0.75)
        amount = max(0, amount)
        self.block += amount
        # Juggernaut: deal damage on block gain
        return amount

    def gain_block_raw(self, amount):
        """Gain block without Dex/Frail modification."""
        self.block += amount
        return amount

    # === Energy ===
    def gain_energy(self, amount):
        self.energy += amount

    def spend_energy(self, amount):
        self.energy -= amount

    # === Card Management ===
    def start_combat(self):
        """Initialize for a new combat."""
        self.draw_pile = [c.copy() for c in self.deck]
        random.shuffle(self.draw_pile)
        self.hand = []
        self.discard_pile = []
        self.exhaust_pile = []
        self.block = 0
        self.effects.clear()
        self.orbs.clear()
        self.stance.clear()
        self.cards_played_this_combat = 0
        self.times_damaged_this_combat = 0
        self.damage_taken_this_combat = 0
        self.gold_gained_this_combat = 0
        self.hp_lost_this_combat = 0
        # Reset card costs
        for c in self.draw_pile:
            c.reset_cost()

    def start_turn(self):
        """Start of player's turn."""
        # Remove block (unless Barricade or Calipers)
        if not self.effects.has("Barricade"):
            calipers = self.has_relic("Calipers")
            if calipers:
                self.block = min(self.block, 15)
            else:
                self.block = 0

        # Gain energy
        self.energy = self.max_energy
        # Berserk
        if self.effects.has("Berserk"):
            self.energy += self.effects.get_stacks("Berserk")
        # Ice Cream relic: energy carries over (handled elsewhere)

        # Draw cards
        draw_count = self.base_draw + self.extra_draw
        self.extra_draw = 0
        # Draw Reduction
        if self.effects.has("Draw Reduction"):
            draw_count -= self.effects.get_stacks("Draw Reduction")
            self.effects.remove("Draw Reduction")
        # No Draw
        if self.effects.has("No Draw"):
            draw_count = 0
            self.effects.remove("No Draw")
        # Energized
        if self.effects.has("Energized"):
            self.energy += self.effects.get_stacks("Energized")
            self.effects.remove("Energized")
        # Next Turn Block
        if self.effects.has("Next Turn Block"):
            self.gain_block_raw(self.effects.get_stacks("Next Turn Block"))
            self.effects.remove("Next Turn Block")

        # Draw Card buff
        if self.effects.has("Draw Card"):
            draw_count += self.effects.get_stacks("Draw Card")
            self.effects.remove("Draw Card")

        self.draw_cards(draw_count)

        # Brutality
        if self.effects.has("Brutality"):
            self.lose_hp(self.effects.get_stacks("Brutality"))
            self.draw_cards(self.effects.get_stacks("Brutality"))

        # Reset per-turn counters
        self.cards_played_this_turn = 0
        self.attacks_played_this_turn = 0
        self.skills_played_this_turn = 0
        self.powers_played_this_turn = 0

    def draw_cards(self, count):
        """Draw cards from draw pile to hand."""
        drawn = []
        for _ in range(count):
            if len(self.hand) >= 10:  # max hand size
                break
            if not self.draw_pile:
                self.shuffle_discard_into_draw()
            if self.draw_pile:
                card = self.draw_pile.pop()
                self.hand.append(card)
                drawn.append(card)
        return drawn

    def shuffle_discard_into_draw(self):
        """Shuffle discard pile into draw pile."""
        self.draw_pile = self.discard_pile[:]
        self.discard_pile = []
        random.shuffle(self.draw_pile)

    def discard_card(self, card):
        """Move a card from hand to discard."""
        if card in self.hand:
            self.hand.remove(card)
        self.discard_pile.append(card)

    def exhaust_card(self, card):
        """Exhaust a card (remove from hand, add to exhaust pile)."""
        if card in self.hand:
            self.hand.remove(card)
        self.exhaust_pile.append(card)

    def end_turn(self):
        """End of player's turn - discard hand, trigger end-of-turn effects."""
        # Discard non-retained cards
        to_discard = []
        for card in self.hand[:]:
            if card.retain or self.effects.has("Runic Pyramid"):
                continue
            if card.ethereal:
                self.exhaust_card(card)
            else:
                to_discard.append(card)
        for card in to_discard:
            self.hand.remove(card)
            self.discard_pile.append(card)

        # Metallicize
        if self.effects.has("Metallicize"):
            self.gain_block_raw(self.effects.get_stacks("Metallicize"))
        # Plated Armor
        if self.effects.has("Plated Armor"):
            self.gain_block_raw(self.effects.get_stacks("Plated Armor"))
        # Combust
        if self.effects.has("Combust"):
            self.lose_hp(1)
            # damage ALL enemies handled in combat
        # Constricted
        if self.effects.has("Constricted"):
            self.lose_hp(self.effects.get_stacks("Constricted"))

        self.effects.tick_turn_end()

    # === Damage Calculation ===
    def calc_attack_damage(self, base_damage, card=None):
        """Calculate outgoing attack damage."""
        dmg = base_damage
        # Strength
        dmg += self.effects.get_stacks("Strength")
        # Vigor
        if self.effects.has("Vigor"):
            dmg += self.effects.get_stacks("Vigor")
            # Vigor consumed on first attack, handled in combat
        # Pen Nib: double damage
        if self.effects.has("Pen Nib"):
            dmg *= 2
        # Phantasmal Killer: double damage
        if self.effects.has("Phantasmal Killer"):
            dmg *= 2
        # Weak: 25% less
        if self.effects.has("Weak"):
            dmg = int(dmg * 0.75)
        # Wrath/Divinity stance multiplier
        dmg = int(dmg * self.stance.get_damage_multiplier())
        return max(0, dmg)

    # === Relic Helpers ===
    def has_relic(self, name):
        return any(r.name == name for r in self.relics)

    def get_relic(self, name):
        for r in self.relics:
            if r.name == name:
                return r
        return None

    def add_relic(self, relic):
        self.relics.append(relic)
        relic.on_obtain(self)

    # === Potion Helpers ===
    def add_potion(self, potion):
        for i in range(self.max_potions):
            if self.potions[i] is None:
                self.potions[i] = potion
                return True
        return False  # no room

    def use_potion(self, index, combat=None, target=None):
        if index < 0 or index >= self.max_potions:
            return False
        potion = self.potions[index]
        if potion is None:
            return False
        potion.use(self, combat, target)
        self.potions[index] = None
        return True

    def discard_potion(self, index):
        if 0 <= index < self.max_potions:
            self.potions[index] = None

    # === Card Reward ===
    def add_card_to_deck(self, card):
        self.deck.append(card)

    def remove_card_from_deck(self, index):
        if 0 <= index < len(self.deck):
            return self.deck.pop(index)
        return None

    # === Display ===
    def status_str(self):
        parts = [f"HP: {self.hp}/{self.max_hp}"]
        parts.append(f"Energy: {self.energy}/{self.max_energy}")
        if self.block > 0:
            parts.append(f"Block: {self.block}")
        effects_str = str(self.effects)
        if effects_str != "None":
            parts.append(f"Effects: [{effects_str}]")
        if self.character_class == "defect" and self.orbs.orbs:
            parts.append(f"Orbs: {self.orbs}")
        if self.character_class == "watcher" and self.stance.current != StanceType.NONE:
            parts.append(f"Stance: {self.stance}")
        return " | ".join(parts)

    def deck_str(self):
        if not self.deck:
            return "Empty deck"
        lines = []
        for i, c in enumerate(self.deck):
            lines.append(f"  {i+1}. {c.short_desc()}")
        return "\n".join(lines)

    def hand_str(self):
        if not self.hand:
            return "Empty hand"
        lines = []
        for i, c in enumerate(self.hand):
            playable = ">" if c.can_play(self, None) else " "
            lines.append(f"  {playable}{i+1}. {c.short_desc()}")
        return "\n".join(lines)

    def relics_str(self):
        if not self.relics:
            return "No relics"
        return ", ".join(r.name for r in self.relics)

    def potions_str(self):
        parts = []
        for i, p in enumerate(self.potions):
            if p:
                parts.append(f"{i+1}. {p.name}")
            else:
                parts.append(f"{i+1}. [empty]")
        return " | ".join(parts)
