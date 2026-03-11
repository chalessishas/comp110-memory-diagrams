"""Silent card pool - all cards for the Silent character."""
from slay_the_spire.card import (
    make_card, CardType, CardRarity, CardColor, CardTarget,
)

# =============================================================================
#  SPECIAL
# =============================================================================

make_card(
    "shiv", "Shiv", 0, CardType.ATTACK, CardRarity.SPECIAL, CardColor.GREEN,
    target=CardTarget.ENEMY,
    description="Deal 4 damage. Exhaust.",
    base_damage=4, upgrade_damage=2,
    exhaust=True,
    effects=[{"action": "damage", "amount": 4}],
)

# =============================================================================
#  BASIC (starter cards)
# =============================================================================

make_card(
    "silent_strike", "Strike", 1, CardType.ATTACK, CardRarity.BASIC, CardColor.GREEN,
    target=CardTarget.ENEMY,
    description="Deal 6 damage.",
    base_damage=6, upgrade_damage=3,
    effects=[{"action": "damage", "amount": 6}],
)

make_card(
    "silent_defend", "Defend", 1, CardType.SKILL, CardRarity.BASIC, CardColor.GREEN,
    target=CardTarget.SELF,
    description="Gain 5 Block.",
    base_block=5, upgrade_block=3,
    effects=[{"action": "block", "amount": 5}],
)

make_card(
    "survivor", "Survivor", 1, CardType.SKILL, CardRarity.BASIC, CardColor.GREEN,
    target=CardTarget.SELF,
    description="Gain 8 Block. Discard 1 card.",
    base_block=8, upgrade_block=3,
    effects=[
        {"action": "block", "amount": 8},
        {"action": "discard", "amount": 1},
    ],
)

make_card(
    "neutralize", "Neutralize", 0, CardType.ATTACK, CardRarity.BASIC, CardColor.GREEN,
    target=CardTarget.ENEMY,
    description="Deal 3 damage. Apply 1 Weak.",
    base_damage=3, upgrade_damage=1,
    base_magic=1, upgrade_magic=1,
    effects=[
        {"action": "damage", "amount": 3},
        {"action": "apply_effect", "effect": "Weak", "stacks": 1, "target": "enemy"},
    ],
)

# =============================================================================
#  COMMON ATTACKS
# =============================================================================

make_card(
    "bane", "Bane", 1, CardType.ATTACK, CardRarity.COMMON, CardColor.GREEN,
    target=CardTarget.ENEMY,
    description="Deal 7 damage. If the enemy is Poisoned, deal 7 damage again.",
    base_damage=7, upgrade_damage=3,
    effects=[
        {"action": "damage", "amount": 7},
        {"action": "custom", "func": "bane_double_if_poisoned"},
    ],
)

make_card(
    "dagger_spray", "Dagger Spray", 1, CardType.ATTACK, CardRarity.COMMON, CardColor.GREEN,
    target=CardTarget.ALL_ENEMIES,
    description="Deal 4 damage to ALL enemies twice.",
    base_damage=4, upgrade_damage=2,
    effects=[
        {"action": "damage", "amount": 4, "times": 2},
    ],
)

make_card(
    "dagger_throw", "Dagger Throw", 1, CardType.ATTACK, CardRarity.COMMON, CardColor.GREEN,
    target=CardTarget.ENEMY,
    description="Deal 9 damage. Draw 1 card. Discard 1 card.",
    base_damage=9, upgrade_damage=3,
    effects=[
        {"action": "damage", "amount": 9},
        {"action": "draw", "amount": 1},
        {"action": "discard", "amount": 1},
    ],
)

make_card(
    "flying_knee", "Flying Knee", 1, CardType.ATTACK, CardRarity.COMMON, CardColor.GREEN,
    target=CardTarget.ENEMY,
    description="Deal 8 damage. Next turn gain 1 Energy.",
    base_damage=8, upgrade_damage=3,
    effects=[
        {"action": "damage", "amount": 8},
        {"action": "apply_effect", "effect": "Energized", "stacks": 1, "target": "self"},
    ],
)

make_card(
    "poisoned_stab", "Poisoned Stab", 1, CardType.ATTACK, CardRarity.COMMON, CardColor.GREEN,
    target=CardTarget.ENEMY,
    description="Deal 6 damage. Apply 3 Poison.",
    base_damage=6, upgrade_damage=2,
    base_magic=3, upgrade_magic=1,
    effects=[
        {"action": "damage", "amount": 6},
        {"action": "apply_effect", "effect": "Poison", "stacks": 3, "target": "enemy"},
    ],
)

make_card(
    "quick_slash", "Quick Slash", 1, CardType.ATTACK, CardRarity.COMMON, CardColor.GREEN,
    target=CardTarget.ENEMY,
    description="Deal 8 damage. Draw 1 card.",
    base_damage=8, upgrade_damage=4,
    effects=[
        {"action": "damage", "amount": 8},
        {"action": "draw", "amount": 1},
    ],
)

make_card(
    "slice", "Slice", 0, CardType.ATTACK, CardRarity.COMMON, CardColor.GREEN,
    target=CardTarget.ENEMY,
    description="Deal 6 damage.",
    base_damage=6, upgrade_damage=3,
    effects=[{"action": "damage", "amount": 6}],
)

make_card(
    "sneaky_strike", "Sneaky Strike", 2, CardType.ATTACK, CardRarity.COMMON, CardColor.GREEN,
    target=CardTarget.ENEMY,
    description="Deal 12 damage. If you have discarded a card this turn, gain 2 Energy.",
    base_damage=12, upgrade_damage=4,
    effects=[
        {"action": "damage", "amount": 12},
        {"action": "custom", "func": "sneaky_strike_refund"},
    ],
)

make_card(
    "sucker_punch", "Sucker Punch", 1, CardType.ATTACK, CardRarity.COMMON, CardColor.GREEN,
    target=CardTarget.ENEMY,
    description="Deal 7 damage. Apply 1 Weak.",
    base_damage=7, upgrade_damage=2,
    base_magic=1, upgrade_magic=1,
    effects=[
        {"action": "damage", "amount": 7},
        {"action": "apply_effect", "effect": "Weak", "stacks": 1, "target": "enemy"},
    ],
)

# =============================================================================
#  COMMON SKILLS
# =============================================================================

make_card(
    "acrobatics", "Acrobatics", 1, CardType.SKILL, CardRarity.COMMON, CardColor.GREEN,
    target=CardTarget.SELF,
    description="Draw 3 cards. Discard 1 card.",
    base_magic=3, upgrade_magic=1,
    effects=[
        {"action": "draw", "amount": 3},
        {"action": "discard", "amount": 1},
    ],
)

make_card(
    "backflip", "Backflip", 1, CardType.SKILL, CardRarity.COMMON, CardColor.GREEN,
    target=CardTarget.SELF,
    description="Gain 5 Block. Draw 2 cards.",
    base_block=5, upgrade_block=3,
    effects=[
        {"action": "block", "amount": 5},
        {"action": "draw", "amount": 2},
    ],
)

make_card(
    "blade_dance", "Blade Dance", 1, CardType.SKILL, CardRarity.COMMON, CardColor.GREEN,
    target=CardTarget.SELF,
    description="Add 3 Shivs to your hand.",
    base_magic=3, upgrade_magic=1,
    effects=[
        {"action": "add_card", "card_id": "shiv", "to": "hand", "count": 3},
    ],
)

make_card(
    "cloak_and_dagger", "Cloak and Dagger", 1, CardType.SKILL, CardRarity.COMMON, CardColor.GREEN,
    target=CardTarget.SELF,
    description="Gain 6 Block. Add 1 Shiv to your hand.",
    base_block=6, upgrade_block=0,
    base_magic=1, upgrade_magic=1,
    effects=[
        {"action": "block", "amount": 6},
        {"action": "add_card", "card_id": "shiv", "to": "hand", "count": 1},
    ],
)

make_card(
    "deadly_poison", "Deadly Poison", 1, CardType.SKILL, CardRarity.COMMON, CardColor.GREEN,
    target=CardTarget.ENEMY,
    description="Apply 5 Poison.",
    base_magic=5, upgrade_magic=2,
    effects=[
        {"action": "apply_effect", "effect": "Poison", "stacks": 5, "target": "enemy"},
    ],
)

make_card(
    "deflect", "Deflect", 0, CardType.SKILL, CardRarity.COMMON, CardColor.GREEN,
    target=CardTarget.SELF,
    description="Gain 4 Block.",
    base_block=4, upgrade_block=3,
    effects=[{"action": "block", "amount": 4}],
)

make_card(
    "dodge_and_roll", "Dodge and Roll", 1, CardType.SKILL, CardRarity.COMMON, CardColor.GREEN,
    target=CardTarget.SELF,
    description="Gain 4 Block. Next turn, gain 4 Block.",
    base_block=4, upgrade_block=2,
    effects=[
        {"action": "block", "amount": 4},
        {"action": "apply_effect", "effect": "NextTurnBlock", "stacks": 4, "target": "self"},
    ],
)

make_card(
    "outmaneuver", "Outmaneuver", 1, CardType.SKILL, CardRarity.COMMON, CardColor.GREEN,
    target=CardTarget.SELF,
    description="Next turn gain 2 Energy.",
    base_magic=2, upgrade_magic=1,
    effects=[
        {"action": "apply_effect", "effect": "Energized", "stacks": 2, "target": "self"},
    ],
)

make_card(
    "piercing_wail", "Piercing Wail", 1, CardType.SKILL, CardRarity.COMMON, CardColor.GREEN,
    target=CardTarget.ALL_ENEMIES,
    description="Apply 6 Strength Down to ALL enemies. Exhaust.",
    base_magic=6, upgrade_magic=2,
    exhaust=True,
    effects=[
        {"action": "apply_effect", "effect": "StrengthDown", "stacks": 6, "target": "all_enemies"},
    ],
)

make_card(
    "prepared", "Prepared", 0, CardType.SKILL, CardRarity.COMMON, CardColor.GREEN,
    target=CardTarget.SELF,
    description="Draw 1 card. Discard 1 card.",
    base_magic=1, upgrade_magic=1,
    effects=[
        {"action": "draw", "amount": 1},
        {"action": "discard", "amount": 1},
    ],
)

# =============================================================================
#  UNCOMMON ATTACKS
# =============================================================================

make_card(
    "all_out_attack", "All-Out Attack", 1, CardType.ATTACK, CardRarity.UNCOMMON, CardColor.GREEN,
    target=CardTarget.ALL_ENEMIES,
    description="Deal 10 damage to ALL enemies. Discard 1 card at random.",
    base_damage=10, upgrade_damage=4,
    effects=[
        {"action": "damage", "amount": 10},
        {"action": "custom", "func": "random_discard"},
    ],
)

make_card(
    "choke", "Choke", 2, CardType.ATTACK, CardRarity.UNCOMMON, CardColor.GREEN,
    target=CardTarget.ENEMY,
    description="Deal 12 damage. Whenever you play a card this turn, the enemy loses 3 HP.",
    base_damage=12, upgrade_damage=0,
    base_magic=3, upgrade_magic=2,
    effects=[
        {"action": "damage", "amount": 12},
        {"action": "apply_effect", "effect": "Choke", "stacks": 3, "target": "enemy"},
    ],
)

make_card(
    "dash", "Dash", 2, CardType.ATTACK, CardRarity.UNCOMMON, CardColor.GREEN,
    target=CardTarget.ENEMY,
    description="Gain 10 Block. Deal 10 damage.",
    base_damage=10, upgrade_damage=3,
    base_block=10, upgrade_block=3,
    effects=[
        {"action": "block", "amount": 10},
        {"action": "damage", "amount": 10},
    ],
)

make_card(
    "die_die_die", "Die Die Die", 1, CardType.ATTACK, CardRarity.UNCOMMON, CardColor.GREEN,
    target=CardTarget.ALL_ENEMIES,
    description="Deal 13 damage to ALL enemies. Exhaust.",
    base_damage=13, upgrade_damage=4,
    exhaust=True,
    effects=[
        {"action": "damage", "amount": 13},
    ],
)

make_card(
    "endless_agony", "Endless Agony", 0, CardType.ATTACK, CardRarity.UNCOMMON, CardColor.GREEN,
    target=CardTarget.ENEMY,
    description="Deal 4 damage. Exhaust. When drawn, add a copy to your hand.",
    base_damage=4, upgrade_damage=2,
    exhaust=True,
    effects=[
        {"action": "damage", "amount": 4},
        {"action": "custom", "func": "endless_agony_on_draw"},
    ],
)

make_card(
    "eviscerate", "Eviscerate", 3, CardType.ATTACK, CardRarity.UNCOMMON, CardColor.GREEN,
    target=CardTarget.ENEMY,
    description="Costs 1 less Energy for each card discarded this turn. Deal 7 damage 3 times.",
    base_damage=7, upgrade_damage=2,
    effects=[
        {"action": "damage", "amount": 7, "times": 3},
    ],
)

make_card(
    "finisher", "Finisher", 1, CardType.ATTACK, CardRarity.UNCOMMON, CardColor.GREEN,
    target=CardTarget.ENEMY,
    description="Deal 6 damage for each Attack played this turn.",
    base_damage=6, upgrade_damage=2,
    effects=[
        {"action": "custom", "func": "finisher_damage"},
    ],
)

make_card(
    "flechettes", "Flechettes", 1, CardType.ATTACK, CardRarity.UNCOMMON, CardColor.GREEN,
    target=CardTarget.ENEMY,
    description="Deal 4 damage for each Skill in your hand.",
    base_damage=4, upgrade_damage=2,
    effects=[
        {"action": "custom", "func": "flechettes_damage"},
    ],
)

make_card(
    "predator", "Predator", 2, CardType.ATTACK, CardRarity.UNCOMMON, CardColor.GREEN,
    target=CardTarget.ENEMY,
    description="Deal 15 damage. Next turn draw 2 extra cards.",
    base_damage=15, upgrade_damage=5,
    base_magic=2, upgrade_magic=0,
    effects=[
        {"action": "damage", "amount": 15},
        {"action": "apply_effect", "effect": "DrawCard", "stacks": 2, "target": "self"},
    ],
)

make_card(
    "riddle_with_holes", "Riddle with Holes", 2, CardType.ATTACK, CardRarity.UNCOMMON, CardColor.GREEN,
    target=CardTarget.ENEMY,
    description="Deal 3 damage 5 times.",
    base_damage=3, upgrade_damage=1,
    effects=[
        {"action": "damage", "amount": 3, "times": 5},
    ],
)

make_card(
    "skewer", "Skewer", -1, CardType.ATTACK, CardRarity.UNCOMMON, CardColor.GREEN,
    target=CardTarget.ENEMY,
    description="Deal 7 damage X times.",
    base_damage=7, upgrade_damage=3,
    effects=[
        {"action": "custom", "func": "skewer_x_damage"},
    ],
)

# =============================================================================
#  UNCOMMON SKILLS
# =============================================================================

make_card(
    "blur", "Blur", 1, CardType.SKILL, CardRarity.UNCOMMON, CardColor.GREEN,
    target=CardTarget.SELF,
    description="Gain 5 Block. Block is not removed at the start of your next turn.",
    base_block=5, upgrade_block=3,
    effects=[
        {"action": "block", "amount": 5},
        {"action": "apply_effect", "effect": "Blur", "stacks": 1, "target": "self"},
    ],
)

make_card(
    "bouncing_flask", "Bouncing Flask", 2, CardType.SKILL, CardRarity.UNCOMMON, CardColor.GREEN,
    target=CardTarget.ALL_ENEMIES,
    description="Apply 3 Poison to a random enemy 3 times.",
    base_magic=3, upgrade_magic=0,
    effects=[
        {"action": "custom", "func": "bouncing_flask_poison"},
    ],
    upgrade_description="Apply 3 Poison to a random enemy 4 times.",
)

make_card(
    "calculated_gamble", "Calculated Gamble", 0, CardType.SKILL, CardRarity.UNCOMMON, CardColor.GREEN,
    target=CardTarget.SELF,
    description="Discard your hand, then draw that many cards. Exhaust.",
    exhaust=True,
    effects=[
        {"action": "custom", "func": "calculated_gamble"},
    ],
    upgrade_description="Discard your hand, then draw that many cards.",
)

make_card(
    "catalyst", "Catalyst", 1, CardType.SKILL, CardRarity.UNCOMMON, CardColor.GREEN,
    target=CardTarget.ENEMY,
    description="Double an enemy's Poison. Exhaust.",
    base_magic=2, upgrade_magic=1,
    exhaust=True,
    effects=[
        {"action": "custom", "func": "catalyst_double_poison"},
    ],
    upgrade_description="Triple an enemy's Poison. Exhaust.",
)

make_card(
    "concentrate", "Concentrate", 0, CardType.SKILL, CardRarity.UNCOMMON, CardColor.GREEN,
    target=CardTarget.SELF,
    description="Discard 3 cards. Gain 2 Energy.",
    base_magic=2, upgrade_magic=1,
    effects=[
        {"action": "discard", "amount": 3},
        {"action": "energy", "amount": 2},
    ],
    upgrade_description="Discard 3 cards. Gain 3 Energy.",
)

make_card(
    "crippling_cloud", "Crippling Cloud", 2, CardType.SKILL, CardRarity.UNCOMMON, CardColor.GREEN,
    target=CardTarget.ALL_ENEMIES,
    description="Apply 4 Poison and 2 Weak to ALL enemies. Exhaust.",
    base_magic=4, upgrade_magic=3,
    exhaust=True,
    effects=[
        {"action": "apply_effect", "effect": "Poison", "stacks": 4, "target": "all_enemies"},
        {"action": "apply_effect", "effect": "Weak", "stacks": 2, "target": "all_enemies"},
    ],
)

make_card(
    "distraction", "Distraction", 1, CardType.SKILL, CardRarity.UNCOMMON, CardColor.GREEN,
    target=CardTarget.SELF,
    description="Add a random Colorless card to your hand. It costs 0 this turn. Exhaust.",
    exhaust=True,
    effects=[
        {"action": "custom", "func": "distraction_add_colorless"},
    ],
    upgrade_cost=0,
    upgrade_description="Add a random Colorless card to your hand. It costs 0 this turn. Exhaust.",
)

make_card(
    "escape_plan", "Escape Plan", 0, CardType.SKILL, CardRarity.UNCOMMON, CardColor.GREEN,
    target=CardTarget.SELF,
    description="Draw 1 card. If you draw a Skill, gain 3 Block.",
    base_block=3, upgrade_block=2,
    effects=[
        {"action": "custom", "func": "escape_plan"},
    ],
)

make_card(
    "expertise", "Expertise", 1, CardType.SKILL, CardRarity.UNCOMMON, CardColor.GREEN,
    target=CardTarget.SELF,
    description="Draw cards until you have 6 cards in hand.",
    base_magic=6, upgrade_magic=1,
    effects=[
        {"action": "custom", "func": "expertise_draw"},
    ],
)

make_card(
    "leg_sweep", "Leg Sweep", 2, CardType.SKILL, CardRarity.UNCOMMON, CardColor.GREEN,
    target=CardTarget.ENEMY,
    description="Apply 2 Weak. Gain 11 Block.",
    base_block=11, upgrade_block=3,
    base_magic=2, upgrade_magic=1,
    effects=[
        {"action": "apply_effect", "effect": "Weak", "stacks": 2, "target": "enemy"},
        {"action": "block", "amount": 11},
    ],
)

make_card(
    "malaise", "Malaise", -1, CardType.SKILL, CardRarity.UNCOMMON, CardColor.GREEN,
    target=CardTarget.ENEMY,
    description="Apply X Weak. Apply X Strength Down. Exhaust.",
    exhaust=True,
    effects=[
        {"action": "custom", "func": "malaise_x"},
    ],
)

make_card(
    "reflex", "Reflex", -2, CardType.SKILL, CardRarity.UNCOMMON, CardColor.GREEN,
    target=CardTarget.NONE,
    description="Unplayable. When this card is discarded from your hand, draw 2 cards.",
    base_magic=2, upgrade_magic=1,
    unplayable=True,
    effects=[
        {"action": "custom", "func": "reflex_on_discard"},
    ],
)

make_card(
    "setup", "Setup", 1, CardType.SKILL, CardRarity.UNCOMMON, CardColor.GREEN,
    target=CardTarget.SELF,
    description="Put a card from your hand on top of your draw pile. It costs 0 until played.",
    effects=[
        {"action": "custom", "func": "setup_card"},
    ],
    upgrade_cost=0,
    upgrade_description="Put a card from your hand on top of your draw pile. It costs 0 until played.",
)

make_card(
    "tactician", "Tactician", -2, CardType.SKILL, CardRarity.UNCOMMON, CardColor.GREEN,
    target=CardTarget.NONE,
    description="Unplayable. When this card is discarded from your hand, gain 1 Energy.",
    base_magic=1, upgrade_magic=1,
    unplayable=True,
    effects=[
        {"action": "custom", "func": "tactician_on_discard"},
    ],
)

make_card(
    "terror", "Terror", 1, CardType.SKILL, CardRarity.UNCOMMON, CardColor.GREEN,
    target=CardTarget.ENEMY,
    description="Apply 99 Vulnerable. Exhaust.",
    base_magic=99,
    exhaust=True,
    effects=[
        {"action": "apply_effect", "effect": "Vulnerable", "stacks": 99, "target": "enemy"},
    ],
    upgrade_cost=0,
    upgrade_description="Apply 99 Vulnerable. Exhaust.",
)

make_card(
    "well_laid_plans", "Well-Laid Plans", 1, CardType.SKILL, CardRarity.UNCOMMON, CardColor.GREEN,
    target=CardTarget.SELF,
    description="Retain up to 1 card each turn. Gain 0 Block.",
    base_magic=1, upgrade_magic=1,
    effects=[
        {"action": "apply_effect", "effect": "Retain", "stacks": 1, "target": "self"},
    ],
    upgrade_description="Retain up to 2 cards each turn.",
)

# =============================================================================
#  UNCOMMON POWERS
# =============================================================================

make_card(
    "a_thousand_cuts", "A Thousand Cuts", 2, CardType.POWER, CardRarity.UNCOMMON, CardColor.GREEN,
    target=CardTarget.SELF,
    description="Whenever you play a card, deal 1 damage to ALL enemies.",
    base_magic=1, upgrade_magic=1,
    effects=[
        {"action": "apply_effect", "effect": "ThousandCuts", "stacks": 1, "target": "self"},
    ],
)

make_card(
    "accuracy", "Accuracy", 1, CardType.POWER, CardRarity.UNCOMMON, CardColor.GREEN,
    target=CardTarget.SELF,
    description="Shivs deal 4 additional damage.",
    base_magic=4, upgrade_magic=2,
    effects=[
        {"action": "apply_effect", "effect": "Accuracy", "stacks": 4, "target": "self"},
    ],
)

make_card(
    "envenom", "Envenom", 2, CardType.POWER, CardRarity.UNCOMMON, CardColor.GREEN,
    target=CardTarget.SELF,
    description="Whenever an Attack deals unblocked damage, apply 1 Poison.",
    base_magic=1, upgrade_magic=0,
    effects=[
        {"action": "apply_effect", "effect": "Envenom", "stacks": 1, "target": "self"},
    ],
    upgrade_cost=1,
    upgrade_description="Whenever an Attack deals unblocked damage, apply 1 Poison.",
)

make_card(
    "infinite_blades", "Infinite Blades", 1, CardType.POWER, CardRarity.UNCOMMON, CardColor.GREEN,
    target=CardTarget.SELF,
    description="At the start of your turn, add a Shiv to your hand.",
    base_magic=1, upgrade_magic=0,
    effects=[
        {"action": "apply_effect", "effect": "InfiniteBlades", "stacks": 1, "target": "self"},
    ],
)

make_card(
    "noxious_fumes", "Noxious Fumes", 1, CardType.POWER, CardRarity.UNCOMMON, CardColor.GREEN,
    target=CardTarget.SELF,
    description="At the start of your turn, apply 2 Poison to ALL enemies.",
    base_magic=2, upgrade_magic=1,
    effects=[
        {"action": "apply_effect", "effect": "NoxiousFumes", "stacks": 2, "target": "self"},
    ],
)

make_card(
    "tools_of_the_trade", "Tools of the Trade", 1, CardType.POWER, CardRarity.UNCOMMON, CardColor.GREEN,
    target=CardTarget.SELF,
    description="At the start of your turn, draw 1 card and discard 1 card.",
    base_magic=1, upgrade_magic=0,
    effects=[
        {"action": "apply_effect", "effect": "ToolsOfTheTrade", "stacks": 1, "target": "self"},
    ],
    upgrade_cost=0,
    upgrade_description="At the start of your turn, draw 1 card and discard 1 card.",
)

# =============================================================================
#  RARE ATTACKS
# =============================================================================

make_card(
    "glass_knife", "Glass Knife", 1, CardType.ATTACK, CardRarity.RARE, CardColor.GREEN,
    target=CardTarget.ENEMY,
    description="Deal 8 damage twice. Decrease this card's damage by 2 this combat.",
    base_damage=8, upgrade_damage=4,
    effects=[
        {"action": "damage", "amount": 8, "times": 2},
        {"action": "custom", "func": "glass_knife_reduce"},
    ],
)

make_card(
    "grand_finale", "Grand Finale", 0, CardType.ATTACK, CardRarity.RARE, CardColor.GREEN,
    target=CardTarget.ALL_ENEMIES,
    description="Can only be played if there are no cards in your draw pile. Deal 50 damage to ALL enemies.",
    base_damage=50, upgrade_damage=10,
    effects=[
        {"action": "custom", "func": "grand_finale_check_and_damage"},
    ],
)

make_card(
    "unloaded", "Unloaded", 1, CardType.ATTACK, CardRarity.RARE, CardColor.GREEN,
    target=CardTarget.ENEMY,
    description="Deal 32 damage. Remove all your Poison from the target.",
    base_damage=32, upgrade_damage=0,
    effects=[
        {"action": "damage", "amount": 32},
        {"action": "custom", "func": "unloaded_remove_poison"},
    ],
)

# =============================================================================
#  RARE SKILLS
# =============================================================================

make_card(
    "adrenaline", "Adrenaline", 0, CardType.SKILL, CardRarity.RARE, CardColor.GREEN,
    target=CardTarget.SELF,
    description="Gain 1 Energy. Draw 2 cards. Exhaust.",
    base_magic=1, upgrade_magic=1,
    exhaust=True,
    effects=[
        {"action": "energy", "amount": 1},
        {"action": "draw", "amount": 2},
    ],
)

make_card(
    "bullet_time", "Bullet Time", 3, CardType.SKILL, CardRarity.RARE, CardColor.GREEN,
    target=CardTarget.SELF,
    description="You cannot draw any more cards this turn. Reduce the cost of all cards in your hand to 0 this turn.",
    effects=[
        {"action": "custom", "func": "bullet_time"},
    ],
    upgrade_cost=2,
    upgrade_description="You cannot draw any more cards this turn. Reduce the cost of all cards in your hand to 0 this turn.",
)

make_card(
    "burst", "Burst", 1, CardType.SKILL, CardRarity.RARE, CardColor.GREEN,
    target=CardTarget.SELF,
    description="This turn, your next Skill is played twice.",
    base_magic=1, upgrade_magic=1,
    effects=[
        {"action": "apply_effect", "effect": "Burst", "stacks": 1, "target": "self"},
    ],
    upgrade_description="This turn, your next 2 Skills are played twice.",
)

make_card(
    "corpse_explosion", "Corpse Explosion", 2, CardType.SKILL, CardRarity.RARE, CardColor.GREEN,
    target=CardTarget.ENEMY,
    description="Apply 6 Poison. When the enemy dies, deal damage equal to its max HP to ALL enemies.",
    base_magic=6, upgrade_magic=3,
    effects=[
        {"action": "apply_effect", "effect": "Poison", "stacks": 6, "target": "enemy"},
        {"action": "apply_effect", "effect": "CorpseExplosion", "stacks": 1, "target": "enemy"},
    ],
)

make_card(
    "doppelganger", "Doppelganger", -1, CardType.SKILL, CardRarity.RARE, CardColor.GREEN,
    target=CardTarget.SELF,
    description="Next turn, draw X cards and gain X Energy.",
    effects=[
        {"action": "custom", "func": "doppelganger_x"},
    ],
)

make_card(
    "nightmare", "Nightmare", 3, CardType.SKILL, CardRarity.RARE, CardColor.GREEN,
    target=CardTarget.SELF,
    description="Choose a card. Next turn, add 3 copies of that card to your hand. Exhaust.",
    base_magic=3, upgrade_magic=0,
    exhaust=True,
    effects=[
        {"action": "custom", "func": "nightmare_copy"},
    ],
    upgrade_cost=2,
    upgrade_description="Choose a card. Next turn, add 3 copies of that card to your hand. Exhaust.",
)

make_card(
    "phantasmal_killer", "Phantasmal Killer", 1, CardType.SKILL, CardRarity.RARE, CardColor.GREEN,
    target=CardTarget.SELF,
    description="Next turn, your attacks deal double damage.",
    effects=[
        {"action": "apply_effect", "effect": "PhantasmalKiller", "stacks": 1, "target": "self"},
    ],
    upgrade_cost=0,
    upgrade_description="Next turn, your attacks deal double damage.",
)

make_card(
    "storm_of_steel", "Storm of Steel", 1, CardType.SKILL, CardRarity.RARE, CardColor.GREEN,
    target=CardTarget.SELF,
    description="Discard your hand. Add 1 Shiv to your hand for each card discarded.",
    effects=[
        {"action": "custom", "func": "storm_of_steel"},
    ],
    upgrade_description="Discard your hand. Add 1 Shiv+ to your hand for each card discarded.",
)

# =============================================================================
#  RARE POWERS
# =============================================================================

make_card(
    "after_image", "After Image", 1, CardType.POWER, CardRarity.RARE, CardColor.GREEN,
    target=CardTarget.SELF,
    description="Whenever you play a card, gain 1 Block.",
    base_magic=1, upgrade_magic=0,
    effects=[
        {"action": "apply_effect", "effect": "AfterImage", "stacks": 1, "target": "self"},
    ],
)

make_card(
    "wraith_form", "Wraith Form", 3, CardType.POWER, CardRarity.RARE, CardColor.GREEN,
    target=CardTarget.SELF,
    description="Gain 2 Intangible. At the end of each turn, lose 1 Dexterity.",
    base_magic=2, upgrade_magic=1,
    effects=[
        {"action": "apply_effect", "effect": "Intangible", "stacks": 2, "target": "self"},
        {"action": "apply_effect", "effect": "WraithForm", "stacks": 1, "target": "self"},
    ],
)
