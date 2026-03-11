"""Colorless card pool - available to all characters."""
from slay_the_spire.card import (
    make_card, CardType, CardRarity, CardColor, CardTarget,
)

# =============================================================================
#  UNCOMMON SKILLS
# =============================================================================

# Bandage Up: Heal 4 HP. Exhaust.
make_card(
    "bandage_up", "Bandage Up", 0, CardType.SKILL, CardRarity.UNCOMMON, CardColor.COLORLESS,
    target=CardTarget.SELF,
    description="Heal 4 HP. Exhaust.",
    base_magic=4, upgrade_magic=2,
    exhaust=True,
    upgrade_description="Heal 6 HP. Exhaust.",
    effects=[{"action": "heal", "amount": 4}],
)

# Blind: Apply 2 Weak to an enemy.
make_card(
    "blind", "Blind", 0, CardType.SKILL, CardRarity.UNCOMMON, CardColor.COLORLESS,
    target=CardTarget.ENEMY,
    description="Apply 2 Weak.",
    base_magic=2,
    upgrade_description="Apply 2 Weak to ALL enemies.",
    effects=[{"action": "apply_effect", "effect": "Weak", "stacks": 2, "target": "enemy"}],
)

# Dark Shackles: Enemy loses 9 Strength for the rest of this turn. Exhaust.
make_card(
    "dark_shackles", "Dark Shackles", 0, CardType.SKILL, CardRarity.UNCOMMON, CardColor.COLORLESS,
    target=CardTarget.ENEMY,
    description="Enemy loses 9 Strength for the rest of this turn. Exhaust.",
    base_magic=9, upgrade_magic=6,
    exhaust=True,
    upgrade_description="Enemy loses 15 Strength for the rest of this turn. Exhaust.",
    effects=[{"action": "apply_effect", "effect": "Shackled", "stacks": 9, "target": "enemy"}],
)

# Deep Breath: Shuffle your discard pile into your draw pile. Draw 1 card.
make_card(
    "deep_breath", "Deep Breath", 0, CardType.SKILL, CardRarity.UNCOMMON, CardColor.COLORLESS,
    target=CardTarget.SELF,
    description="Shuffle your discard pile into your draw pile. Draw 1 card.",
    base_magic=1, upgrade_magic=1,
    upgrade_description="Shuffle your discard pile into your draw pile. Draw 2 cards.",
    effects=[
        {"action": "custom", "func": "deep_breath_shuffle"},
        {"action": "draw", "amount": 1},
    ],
)

# Discovery: Choose 1 of 3 random Colorless cards to add to your hand. It costs 0 this turn. Exhaust.
make_card(
    "discovery", "Discovery", 1, CardType.SKILL, CardRarity.UNCOMMON, CardColor.COLORLESS,
    target=CardTarget.SELF,
    description="Choose 1 of 3 random Colorless cards to add to your hand. It costs 0 this turn. Exhaust.",
    exhaust=True,
    upgrade_description="Choose 1 of 3 random Colorless cards to add to your hand. It costs 0 this turn. Exhaust.",
    upgrade_cost=0,
    effects=[{"action": "custom", "func": "discovery_choose"}],
)

# Dramatic Entrance: Deal 8 damage to ALL enemies. Innate. Exhaust.
make_card(
    "dramatic_entrance", "Dramatic Entrance", 0, CardType.ATTACK, CardRarity.UNCOMMON, CardColor.COLORLESS,
    target=CardTarget.ALL_ENEMIES,
    description="Deal 8 damage to ALL enemies. Innate. Exhaust.",
    base_damage=8, upgrade_damage=4,
    innate=True, exhaust=True,
    upgrade_description="Deal 12 damage to ALL enemies. Innate. Exhaust.",
    effects=[{"action": "damage", "amount": 8, "target": "all_enemies"}],
)

# Enlightenment: Reduce the cost of all cards in your hand to 1 for this turn.
make_card(
    "enlightenment", "Enlightenment", 0, CardType.SKILL, CardRarity.UNCOMMON, CardColor.COLORLESS,
    target=CardTarget.SELF,
    description="Reduce the cost of all cards in your hand to 1 this turn.",
    upgrade_description="Reduce the cost of all cards in your hand to 1 for the rest of combat.",
    effects=[{"action": "custom", "func": "enlightenment_reduce"}],
)

# Finesse: Gain 2 Block. Draw 1 card.
make_card(
    "finesse", "Finesse", 0, CardType.SKILL, CardRarity.UNCOMMON, CardColor.COLORLESS,
    target=CardTarget.SELF,
    description="Gain 2 Block. Draw 1 card.",
    base_block=2, upgrade_block=2,
    upgrade_description="Gain 4 Block. Draw 1 card.",
    effects=[
        {"action": "block", "amount": 2},
        {"action": "draw", "amount": 1},
    ],
)

# Flash of Steel: Deal 3 damage. Draw 1 card.
make_card(
    "flash_of_steel", "Flash of Steel", 0, CardType.ATTACK, CardRarity.UNCOMMON, CardColor.COLORLESS,
    target=CardTarget.ENEMY,
    description="Deal 3 damage. Draw 1 card.",
    base_damage=3, upgrade_damage=3,
    upgrade_description="Deal 6 damage. Draw 1 card.",
    effects=[
        {"action": "damage", "amount": 3},
        {"action": "draw", "amount": 1},
    ],
)

# Forethought: Place a card from your hand on the bottom of your draw pile. It costs 0 until played.
make_card(
    "forethought", "Forethought", 0, CardType.SKILL, CardRarity.UNCOMMON, CardColor.COLORLESS,
    target=CardTarget.SELF,
    description="Place a card from your hand on the bottom of your draw pile. It costs 0 until played.",
    upgrade_description="Place any number of cards from your hand on the bottom of your draw pile. They cost 0 until played.",
    effects=[{"action": "custom", "func": "forethought_bottom"}],
)

# Good Instincts: Gain 6 Block.
make_card(
    "good_instincts", "Good Instincts", 0, CardType.SKILL, CardRarity.UNCOMMON, CardColor.COLORLESS,
    target=CardTarget.SELF,
    description="Gain 6 Block.",
    base_block=6, upgrade_block=3,
    upgrade_description="Gain 9 Block.",
    effects=[{"action": "block", "amount": 6}],
)

# Impatience: If you have no Attacks in your hand, draw 2 cards.
make_card(
    "impatience", "Impatience", 0, CardType.SKILL, CardRarity.UNCOMMON, CardColor.COLORLESS,
    target=CardTarget.SELF,
    description="If you have no Attacks in your hand, draw 2 cards.",
    base_magic=2, upgrade_magic=1,
    upgrade_description="If you have no Attacks in your hand, draw 3 cards.",
    effects=[{"action": "custom", "func": "impatience_draw"}],
)

# Jack of All Trades: Add a random Colorless card to your hand. Exhaust.
make_card(
    "jack_of_all_trades", "Jack of All Trades", 0, CardType.SKILL, CardRarity.UNCOMMON, CardColor.COLORLESS,
    target=CardTarget.SELF,
    description="Add a random Colorless card to your hand. Exhaust.",
    exhaust=True,
    upgrade_description="Add 2 random Colorless cards to your hand. Exhaust.",
    effects=[{"action": "custom", "func": "jack_of_all_trades_add"}],
)

# Madness: A random card in your hand costs 0 for the rest of combat. Exhaust.
make_card(
    "madness", "Madness", 1, CardType.SKILL, CardRarity.UNCOMMON, CardColor.COLORLESS,
    target=CardTarget.SELF,
    description="A random card in your hand costs 0 for the rest of combat. Exhaust.",
    exhaust=True,
    upgrade_cost=0,
    upgrade_description="A random card in your hand costs 0 for the rest of combat. Exhaust.",
    effects=[{"action": "custom", "func": "madness_zero_cost"}],
)

# Mind Blast: Innate. Deal damage equal to the size of your draw pile.
make_card(
    "mind_blast", "Mind Blast", 2, CardType.ATTACK, CardRarity.UNCOMMON, CardColor.COLORLESS,
    target=CardTarget.ENEMY,
    description="Innate. Deal damage equal to the number of cards in your draw pile.",
    innate=True,
    upgrade_cost=1,
    upgrade_description="Innate. Deal damage equal to the number of cards in your draw pile.",
    effects=[{"action": "custom", "func": "mind_blast_damage"}],
)

# Panacea: Gain 1 Artifact. Exhaust.
make_card(
    "panacea", "Panacea", 0, CardType.SKILL, CardRarity.UNCOMMON, CardColor.COLORLESS,
    target=CardTarget.SELF,
    description="Gain 1 Artifact. Exhaust.",
    base_magic=1, upgrade_magic=1,
    exhaust=True,
    upgrade_description="Gain 2 Artifact. Exhaust.",
    effects=[{"action": "apply_effect", "effect": "Artifact", "stacks": 1, "target": "self"}],
)

# Panic Button: Gain 30 Block. You cannot gain Block from cards for 2 turns. Exhaust.
make_card(
    "panic_button", "Panic Button", 0, CardType.SKILL, CardRarity.UNCOMMON, CardColor.COLORLESS,
    target=CardTarget.SELF,
    description="Gain 30 Block. You cannot gain Block from cards for 2 turns. Exhaust.",
    base_block=30, upgrade_block=10,
    exhaust=True,
    upgrade_description="Gain 40 Block. You cannot gain Block from cards for 2 turns. Exhaust.",
    effects=[
        {"action": "block", "amount": 30},
        {"action": "apply_effect", "effect": "No Block", "stacks": 2, "target": "self"},
    ],
)

# Purity: Choose and Exhaust up to 3 cards in your hand.
make_card(
    "purity", "Purity", 0, CardType.SKILL, CardRarity.UNCOMMON, CardColor.COLORLESS,
    target=CardTarget.SELF,
    description="Choose and Exhaust up to 3 cards in your hand.",
    base_magic=3, upgrade_magic=2,
    exhaust=True,
    upgrade_description="Choose and Exhaust up to 5 cards in your hand.",
    effects=[{"action": "custom", "func": "purity_exhaust"}],
)

# Swift Strike: Deal 7 damage.
make_card(
    "swift_strike", "Swift Strike", 0, CardType.ATTACK, CardRarity.UNCOMMON, CardColor.COLORLESS,
    target=CardTarget.ENEMY,
    description="Deal 7 damage.",
    base_damage=7, upgrade_damage=3,
    upgrade_description="Deal 10 damage.",
    effects=[{"action": "damage", "amount": 7}],
)

# Trip: Apply 2 Vulnerable to an enemy.
make_card(
    "trip", "Trip", 0, CardType.SKILL, CardRarity.UNCOMMON, CardColor.COLORLESS,
    target=CardTarget.ENEMY,
    description="Apply 2 Vulnerable.",
    base_magic=2,
    upgrade_description="Apply 2 Vulnerable to ALL enemies.",
    effects=[{"action": "apply_effect", "effect": "Vulnerable", "stacks": 2, "target": "enemy"}],
)

# =============================================================================
#  RARE
# =============================================================================

# Apotheosis: Upgrade all cards in your deck for the rest of combat. Exhaust.
make_card(
    "apotheosis", "Apotheosis", 2, CardType.SKILL, CardRarity.RARE, CardColor.COLORLESS,
    target=CardTarget.SELF,
    description="Upgrade ALL cards in your deck for the rest of combat. Exhaust.",
    exhaust=True,
    upgrade_cost=1,
    upgrade_description="Upgrade ALL cards in your deck for the rest of combat. Exhaust.",
    effects=[{"action": "custom", "func": "apotheosis_upgrade_all"}],
)

# Chrysalis: Add 3 random Skills into your draw pile. They cost 0 this combat. Exhaust.
make_card(
    "chrysalis", "Chrysalis", 2, CardType.SKILL, CardRarity.RARE, CardColor.COLORLESS,
    target=CardTarget.SELF,
    description="Add 3 random Skills into your draw pile. They cost 0 this combat. Exhaust.",
    base_magic=3, upgrade_magic=2,
    exhaust=True,
    upgrade_description="Add 5 random Skills into your draw pile. They cost 0 this combat. Exhaust.",
    effects=[{"action": "custom", "func": "chrysalis_add_skills"}],
)

# Hand of Greed: Deal 20 damage. If this kills a non-minion enemy, gain 20 Gold.
make_card(
    "hand_of_greed", "Hand of Greed", 2, CardType.ATTACK, CardRarity.RARE, CardColor.COLORLESS,
    target=CardTarget.ENEMY,
    description="Deal 20 damage. If Fatal, gain 20 Gold.",
    base_damage=20, upgrade_damage=5,
    base_magic=20, upgrade_magic=5,
    upgrade_description="Deal 25 damage. If Fatal, gain 25 Gold.",
    effects=[
        {"action": "damage", "amount": 20},
        {"action": "custom", "func": "hand_of_greed_gold"},
    ],
)

# Magnetism: At the start of each turn, add a random Colorless card to your hand.
make_card(
    "magnetism", "Magnetism", 1, CardType.POWER, CardRarity.RARE, CardColor.COLORLESS,
    target=CardTarget.SELF,
    description="At the start of each turn, add a random Colorless card to your hand.",
    upgrade_cost=0,
    upgrade_description="At the start of each turn, add a random Colorless card to your hand.",
    effects=[{"action": "apply_effect", "effect": "Magnetism", "stacks": 1, "target": "self"}],
)

# Master of Strategy: Draw 3 cards. Exhaust.
make_card(
    "master_of_strategy", "Master of Strategy", 0, CardType.SKILL, CardRarity.RARE, CardColor.COLORLESS,
    target=CardTarget.SELF,
    description="Draw 3 cards. Exhaust.",
    base_magic=3, upgrade_magic=1,
    exhaust=True,
    upgrade_description="Draw 4 cards. Exhaust.",
    effects=[{"action": "draw", "amount": 3}],
)

# Mayhem: At the start of your turn, play the top card of your draw pile.
make_card(
    "mayhem", "Mayhem", 2, CardType.POWER, CardRarity.RARE, CardColor.COLORLESS,
    target=CardTarget.SELF,
    description="At the start of your turn, play the top card of your draw pile.",
    upgrade_cost=1,
    upgrade_description="At the start of your turn, play the top card of your draw pile.",
    effects=[{"action": "apply_effect", "effect": "Mayhem", "stacks": 1, "target": "self"}],
)

# Metamorphosis: Add 3 random Attacks into your draw pile. They cost 0 this combat. Exhaust.
make_card(
    "metamorphosis", "Metamorphosis", 2, CardType.SKILL, CardRarity.RARE, CardColor.COLORLESS,
    target=CardTarget.SELF,
    description="Add 3 random Attacks into your draw pile. They cost 0 this combat. Exhaust.",
    base_magic=3, upgrade_magic=2,
    exhaust=True,
    upgrade_description="Add 5 random Attacks into your draw pile. They cost 0 this combat. Exhaust.",
    effects=[{"action": "custom", "func": "metamorphosis_add_attacks"}],
)

# Panache: Every time you play 5 cards in a single turn, deal 10 damage to ALL enemies.
make_card(
    "panache", "Panache", 0, CardType.POWER, CardRarity.RARE, CardColor.COLORLESS,
    target=CardTarget.SELF,
    description="Every time you play 5 cards in a single turn, deal 10 damage to ALL enemies.",
    base_magic=10, upgrade_magic=4,
    upgrade_description="Every time you play 5 cards in a single turn, deal 14 damage to ALL enemies.",
    effects=[{"action": "apply_effect", "effect": "Panache", "stacks": 10, "target": "self"}],
)

# Sadistic Nature: Whenever you apply a debuff to an enemy, deal 5 damage to them.
make_card(
    "sadistic_nature", "Sadistic Nature", 0, CardType.POWER, CardRarity.RARE, CardColor.COLORLESS,
    target=CardTarget.SELF,
    description="Whenever you apply a debuff to an enemy, deal 5 damage to them.",
    base_magic=5, upgrade_magic=2,
    upgrade_description="Whenever you apply a debuff to an enemy, deal 7 damage to them.",
    effects=[{"action": "apply_effect", "effect": "Sadistic Nature", "stacks": 5, "target": "self"}],
)

# Secret Technique: Search your draw pile for a Skill and put it into your hand. Exhaust.
make_card(
    "secret_technique", "Secret Technique", 0, CardType.SKILL, CardRarity.RARE, CardColor.COLORLESS,
    target=CardTarget.SELF,
    description="Search your draw pile for a Skill and put it into your hand. Exhaust.",
    exhaust=True,
    upgrade_cost=0,
    upgrade_description="Search your draw pile for a Skill and put it into your hand. Exhaust.",
    effects=[{"action": "custom", "func": "secret_technique_search"}],
)

# Secret Weapon: Search your draw pile for an Attack and put it into your hand. Exhaust.
make_card(
    "secret_weapon", "Secret Weapon", 0, CardType.SKILL, CardRarity.RARE, CardColor.COLORLESS,
    target=CardTarget.SELF,
    description="Search your draw pile for an Attack and put it into your hand. Exhaust.",
    exhaust=True,
    upgrade_cost=0,
    upgrade_description="Search your draw pile for an Attack and put it into your hand. Exhaust.",
    effects=[{"action": "custom", "func": "secret_weapon_search"}],
)

# The Bomb: At the end of 3 turns, deal 40 damage to ALL enemies.
make_card(
    "the_bomb", "The Bomb", 2, CardType.SKILL, CardRarity.RARE, CardColor.COLORLESS,
    target=CardTarget.SELF,
    description="At the end of 3 turns, deal 40 damage to ALL enemies.",
    base_magic=40, upgrade_magic=10,
    upgrade_description="At the end of 3 turns, deal 50 damage to ALL enemies.",
    effects=[{"action": "apply_effect", "effect": "The Bomb", "stacks": 40, "target": "self"}],
)

# Thinking Ahead: Draw 2 cards. Place a card from your hand on top of your draw pile.
make_card(
    "thinking_ahead", "Thinking Ahead", 0, CardType.SKILL, CardRarity.RARE, CardColor.COLORLESS,
    target=CardTarget.SELF,
    description="Draw 2 cards. Place a card from your hand on top of your draw pile.",
    upgrade_description="Draw 3 cards. Place a card from your hand on top of your draw pile.",
    base_magic=2, upgrade_magic=1,
    effects=[
        {"action": "draw", "amount": 2},
        {"action": "custom", "func": "thinking_ahead_top"},
    ],
)

# Transmutation: Add X random Colorless cards into your hand. They cost 0 this turn. Exhaust.
make_card(
    "transmutation", "Transmutation", -1, CardType.SKILL, CardRarity.RARE, CardColor.COLORLESS,
    target=CardTarget.SELF,
    description="Add X random Colorless cards into your hand. They cost 0 this turn. Exhaust.",
    exhaust=True,
    upgrade_description="Add X+1 random Colorless cards into your hand. They cost 0 this turn. Exhaust.",
    effects=[{"action": "custom", "func": "transmutation_add"}],
)

# Violence: Add 3 random Attacks from your draw pile into your hand. Exhaust.
make_card(
    "violence", "Violence", 0, CardType.SKILL, CardRarity.RARE, CardColor.COLORLESS,
    target=CardTarget.SELF,
    description="Add 3 random Attacks from your draw pile into your hand. Exhaust.",
    base_magic=3, upgrade_magic=1,
    exhaust=True,
    upgrade_description="Add 4 random Attacks from your draw pile into your hand. Exhaust.",
    effects=[{"action": "custom", "func": "violence_pull_attacks"}],
)
