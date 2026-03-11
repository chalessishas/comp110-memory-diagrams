"""Ironclad card pool - all cards for the Ironclad character."""
from slay_the_spire.card import (
    make_card, CardType, CardRarity, CardColor, CardTarget,
)

# =============================================================================
#  BASIC (starter cards)
# =============================================================================

make_card(
    "ironclad_strike", "Strike", 1, CardType.ATTACK, CardRarity.BASIC, CardColor.RED,
    target=CardTarget.ENEMY,
    description="Deal 6 damage.",
    base_damage=6, upgrade_damage=3,
    effects=[{"action": "damage", "amount": 6}],
)

make_card(
    "ironclad_defend", "Defend", 1, CardType.SKILL, CardRarity.BASIC, CardColor.RED,
    target=CardTarget.SELF,
    description="Gain 5 Block.",
    base_block=5, upgrade_block=3,
    effects=[{"action": "block", "amount": 5}],
)

make_card(
    "bash", "Bash", 2, CardType.ATTACK, CardRarity.BASIC, CardColor.RED,
    target=CardTarget.ENEMY,
    description="Deal 8 damage. Apply 2 Vulnerable.",
    base_damage=8, upgrade_damage=2,
    base_magic=2, upgrade_magic=1,
    effects=[
        {"action": "damage", "amount": 8},
        {"action": "apply_effect", "effect": "Vulnerable", "stacks": 2, "target": "enemy"},
    ],
)

# =============================================================================
#  COMMON ATTACKS
# =============================================================================

make_card(
    "anger", "Anger", 0, CardType.ATTACK, CardRarity.COMMON, CardColor.RED,
    target=CardTarget.ENEMY,
    description="Deal 6 damage. Add a copy of this card to your discard pile.",
    base_damage=6, upgrade_damage=2,
    effects=[
        {"action": "damage", "amount": 6},
        {"action": "add_card", "card_id": "anger", "to": "discard", "count": 1},
    ],
)

make_card(
    "body_slam", "Body Slam", 1, CardType.ATTACK, CardRarity.COMMON, CardColor.RED,
    target=CardTarget.ENEMY,
    description="Deal damage equal to your current Block.",
    upgrade_cost=0,
    effects=[{"action": "custom", "func": "body_slam"}],
)

make_card(
    "clash", "Clash", 0, CardType.ATTACK, CardRarity.COMMON, CardColor.RED,
    target=CardTarget.ENEMY,
    description="Can only be played if every card in your hand is an Attack. Deal 14 damage.",
    base_damage=14, upgrade_damage=4,
    effects=[{"action": "damage", "amount": 14}],
)

make_card(
    "cleave", "Cleave", 1, CardType.ATTACK, CardRarity.COMMON, CardColor.RED,
    target=CardTarget.ALL_ENEMIES,
    description="Deal 8 damage to ALL enemies.",
    base_damage=8, upgrade_damage=3,
    effects=[{"action": "damage", "amount": 8, "target": "all_enemies"}],
)

make_card(
    "clothesline", "Clothesline", 2, CardType.ATTACK, CardRarity.COMMON, CardColor.RED,
    target=CardTarget.ENEMY,
    description="Deal 12 damage. Apply 2 Weak.",
    base_damage=12, upgrade_damage=2,
    base_magic=2, upgrade_magic=1,
    effects=[
        {"action": "damage", "amount": 12},
        {"action": "apply_effect", "effect": "Weak", "stacks": 2, "target": "enemy"},
    ],
)

make_card(
    "headbutt", "Headbutt", 1, CardType.ATTACK, CardRarity.COMMON, CardColor.RED,
    target=CardTarget.ENEMY,
    description="Deal 9 damage. Put a card from your discard pile on top of your draw pile.",
    base_damage=9, upgrade_damage=3,
    effects=[
        {"action": "damage", "amount": 9},
        {"action": "custom", "func": "headbutt"},
    ],
)

make_card(
    "heavy_blade", "Heavy Blade", 2, CardType.ATTACK, CardRarity.COMMON, CardColor.RED,
    target=CardTarget.ENEMY,
    description="Deal 14 damage. Strength affects this card 3 times.",
    base_damage=14,
    base_magic=3, upgrade_magic=2,
    effects=[{"action": "custom", "func": "heavy_blade"}],
)

make_card(
    "iron_wave", "Iron Wave", 1, CardType.ATTACK, CardRarity.COMMON, CardColor.RED,
    target=CardTarget.ENEMY,
    description="Gain 5 Block. Deal 5 damage.",
    base_damage=5, upgrade_damage=2,
    base_block=5, upgrade_block=2,
    effects=[
        {"action": "block", "amount": 5},
        {"action": "damage", "amount": 5},
    ],
)

make_card(
    "perfected_strike", "Perfected Strike", 2, CardType.ATTACK, CardRarity.COMMON, CardColor.RED,
    target=CardTarget.ENEMY,
    description="Deal 6 damage. Deals 2 additional damage for ALL cards containing 'Strike'.",
    base_damage=6,
    base_magic=2, upgrade_magic=1,
    effects=[{"action": "custom", "func": "perfected_strike"}],
)

make_card(
    "pommel_strike", "Pommel Strike", 1, CardType.ATTACK, CardRarity.COMMON, CardColor.RED,
    target=CardTarget.ENEMY,
    description="Deal 9 damage. Draw 1 card.",
    base_damage=9, upgrade_damage=1,
    base_magic=1, upgrade_magic=1,
    effects=[
        {"action": "damage", "amount": 9},
        {"action": "draw", "amount": 1},
    ],
)

make_card(
    "sword_boomerang", "Sword Boomerang", 1, CardType.ATTACK, CardRarity.COMMON, CardColor.RED,
    target=CardTarget.ALL_ENEMIES,
    description="Deal 3 damage to a random enemy 3 times.",
    base_damage=3,
    base_magic=3, upgrade_magic=1,
    effects=[{"action": "damage", "amount": 3, "times": 3, "target": "random"}],
)

make_card(
    "thunderclap", "Thunderclap", 1, CardType.ATTACK, CardRarity.COMMON, CardColor.RED,
    target=CardTarget.ALL_ENEMIES,
    description="Deal 4 damage and apply 1 Vulnerable to ALL enemies.",
    base_damage=4, upgrade_damage=3,
    effects=[
        {"action": "damage", "amount": 4, "target": "all_enemies"},
        {"action": "apply_effect", "effect": "Vulnerable", "stacks": 1, "target": "all_enemies"},
    ],
)

make_card(
    "twin_strike", "Twin Strike", 1, CardType.ATTACK, CardRarity.COMMON, CardColor.RED,
    target=CardTarget.ENEMY,
    description="Deal 5 damage twice.",
    base_damage=5, upgrade_damage=2,
    effects=[{"action": "damage", "amount": 5, "times": 2}],
)

make_card(
    "wild_strike", "Wild Strike", 1, CardType.ATTACK, CardRarity.COMMON, CardColor.RED,
    target=CardTarget.ENEMY,
    description="Deal 12 damage. Shuffle a Wound into your draw pile.",
    base_damage=12, upgrade_damage=5,
    effects=[
        {"action": "damage", "amount": 12},
        {"action": "add_card", "card_id": "wound", "to": "draw", "count": 1},
    ],
)

# =============================================================================
#  COMMON SKILLS
# =============================================================================

make_card(
    "armaments", "Armaments", 1, CardType.SKILL, CardRarity.COMMON, CardColor.RED,
    target=CardTarget.SELF,
    description="Gain 5 Block. Upgrade a card in your hand for the rest of combat.",
    base_block=5,
    upgrade_description="Gain 5 Block. Upgrade ALL cards in your hand for the rest of combat.",
    effects=[
        {"action": "block", "amount": 5},
        {"action": "custom", "func": "armaments"},
    ],
)

make_card(
    "battle_trance", "Battle Trance", 0, CardType.SKILL, CardRarity.COMMON, CardColor.RED,
    target=CardTarget.SELF,
    description="Draw 3 cards. You can not draw additional cards this turn.",
    base_magic=3, upgrade_magic=1,
    effects=[
        {"action": "draw", "amount": 3},
        {"action": "apply_effect", "effect": "No Draw", "stacks": 1, "target": "self"},
    ],
)

make_card(
    "blood_for_blood", "Blood for Blood", 4, CardType.SKILL, CardRarity.COMMON, CardColor.RED,
    target=CardTarget.ENEMY,
    description="Costs 1 less Energy for each time you lose HP in combat. Deal 18 damage.",
    base_damage=18, upgrade_damage=4,
    effects=[{"action": "damage", "amount": 18}],
)

make_card(
    "burning_pact", "Burning Pact", 1, CardType.SKILL, CardRarity.COMMON, CardColor.RED,
    target=CardTarget.SELF,
    description="Exhaust 1 card. Draw 2 cards.",
    base_magic=2, upgrade_magic=1,
    effects=[
        {"action": "custom", "func": "burning_pact_exhaust"},
        {"action": "draw", "amount": 2},
    ],
)

make_card(
    "flex", "Flex", 0, CardType.SKILL, CardRarity.COMMON, CardColor.RED,
    target=CardTarget.SELF,
    description="Gain 2 Strength. At the end of this turn, lose 2 Strength.",
    base_magic=2, upgrade_magic=2,
    effects=[
        {"action": "apply_effect", "effect": "Strength", "stacks": 2, "target": "self"},
        {"action": "apply_effect", "effect": "Lose Strength", "stacks": 2, "target": "self"},
    ],
)

make_card(
    "havoc", "Havoc", 1, CardType.SKILL, CardRarity.COMMON, CardColor.RED,
    target=CardTarget.NONE,
    description="Play the top card of your draw pile and Exhaust it.",
    upgrade_cost=0,
    effects=[{"action": "custom", "func": "havoc"}],
)

make_card(
    "intimidate", "Intimidate", 0, CardType.SKILL, CardRarity.COMMON, CardColor.RED,
    target=CardTarget.ALL_ENEMIES,
    description="Apply 1 Weak to ALL enemies. Exhaust.",
    base_magic=1, upgrade_magic=1,
    exhaust=True,
    effects=[
        {"action": "apply_effect", "effect": "Weak", "stacks": 1, "target": "all_enemies"},
    ],
)

make_card(
    "power_through", "Power Through", 1, CardType.SKILL, CardRarity.COMMON, CardColor.RED,
    target=CardTarget.SELF,
    description="Add 2 Wounds to your hand. Gain 15 Block.",
    base_block=15, upgrade_block=5,
    effects=[
        {"action": "add_card", "card_id": "wound", "to": "hand", "count": 2},
        {"action": "block", "amount": 15},
    ],
)

make_card(
    "shrug_it_off", "Shrug It Off", 1, CardType.SKILL, CardRarity.COMMON, CardColor.RED,
    target=CardTarget.SELF,
    description="Gain 8 Block. Draw 1 card.",
    base_block=8, upgrade_block=3,
    effects=[
        {"action": "block", "amount": 8},
        {"action": "draw", "amount": 1},
    ],
)

make_card(
    "true_grit", "True Grit", 1, CardType.SKILL, CardRarity.COMMON, CardColor.RED,
    target=CardTarget.SELF,
    description="Gain 7 Block. Exhaust a random card from your hand.",
    base_block=7, upgrade_block=2,
    upgrade_description="Gain 9 Block. Exhaust a card from your hand.",
    effects=[
        {"action": "block", "amount": 7},
        {"action": "custom", "func": "true_grit"},
    ],
)

make_card(
    "warcry", "Warcry", 0, CardType.SKILL, CardRarity.COMMON, CardColor.RED,
    target=CardTarget.SELF,
    description="Draw 1 card. Put a card from your hand on top of your draw pile. Exhaust.",
    base_magic=1, upgrade_magic=1,
    exhaust=True,
    effects=[
        {"action": "draw", "amount": 1},
        {"action": "custom", "func": "warcry"},
    ],
)

# =============================================================================
#  UNCOMMON ATTACKS
# =============================================================================

make_card(
    "carnage", "Carnage", 2, CardType.ATTACK, CardRarity.UNCOMMON, CardColor.RED,
    target=CardTarget.ENEMY,
    description="Ethereal. Deal 20 damage.",
    base_damage=20, upgrade_damage=8,
    ethereal=True,
    effects=[{"action": "damage", "amount": 20}],
)

make_card(
    "dropkick", "Dropkick", 1, CardType.ATTACK, CardRarity.UNCOMMON, CardColor.RED,
    target=CardTarget.ENEMY,
    description="Deal 5 damage. If the enemy is Vulnerable, gain 1 Energy and draw 1 card.",
    base_damage=5, upgrade_damage=3,
    effects=[
        {"action": "damage", "amount": 5},
        {"action": "custom", "func": "dropkick"},
    ],
)

make_card(
    "hemokinesis", "Hemokinesis", 1, CardType.ATTACK, CardRarity.UNCOMMON, CardColor.RED,
    target=CardTarget.ENEMY,
    description="Lose 2 HP. Deal 15 damage.",
    base_damage=15, upgrade_damage=5,
    effects=[
        {"action": "lose_hp", "amount": 2},
        {"action": "damage", "amount": 15},
    ],
)

make_card(
    "pummel", "Pummel", 1, CardType.ATTACK, CardRarity.UNCOMMON, CardColor.RED,
    target=CardTarget.ENEMY,
    description="Deal 2 damage 4 times. Exhaust.",
    base_damage=2,
    base_magic=4, upgrade_magic=1,
    exhaust=True,
    effects=[{"action": "damage", "amount": 2, "times": 4}],
)

make_card(
    "rampage", "Rampage", 1, CardType.ATTACK, CardRarity.UNCOMMON, CardColor.RED,
    target=CardTarget.ENEMY,
    description="Deal 8 damage. Increase this card's damage by 5 each time it is played.",
    base_damage=8,
    base_magic=5, upgrade_magic=3,
    effects=[{"action": "custom", "func": "rampage"}],
)

make_card(
    "reckless_charge", "Reckless Charge", 0, CardType.ATTACK, CardRarity.UNCOMMON, CardColor.RED,
    target=CardTarget.ENEMY,
    description="Deal 7 damage. Shuffle a Dazed into your draw pile.",
    base_damage=7, upgrade_damage=3,
    effects=[
        {"action": "damage", "amount": 7},
        {"action": "add_card", "card_id": "dazed", "to": "draw", "count": 1},
    ],
)

make_card(
    "searing_blow", "Searing Blow", 2, CardType.ATTACK, CardRarity.UNCOMMON, CardColor.RED,
    target=CardTarget.ENEMY,
    description="Deal 12 damage. Can be upgraded any number of times.",
    base_damage=12, upgrade_damage=4,
    effects=[{"action": "custom", "func": "searing_blow"}],
)

make_card(
    "sever_soul", "Sever Soul", 2, CardType.ATTACK, CardRarity.UNCOMMON, CardColor.RED,
    target=CardTarget.ENEMY,
    description="Exhaust all non-Attack cards in your hand. Deal 16 damage.",
    base_damage=16, upgrade_damage=6,
    effects=[
        {"action": "custom", "func": "sever_soul"},
        {"action": "damage", "amount": 16},
    ],
)

make_card(
    "uppercut", "Uppercut", 2, CardType.ATTACK, CardRarity.UNCOMMON, CardColor.RED,
    target=CardTarget.ENEMY,
    description="Deal 13 damage. Apply 1 Weak. Apply 1 Vulnerable.",
    base_damage=13,
    base_magic=1, upgrade_magic=1,
    effects=[
        {"action": "damage", "amount": 13},
        {"action": "apply_effect", "effect": "Weak", "stacks": 1, "target": "enemy"},
        {"action": "apply_effect", "effect": "Vulnerable", "stacks": 1, "target": "enemy"},
    ],
)

make_card(
    "whirlwind", "Whirlwind", -1, CardType.ATTACK, CardRarity.UNCOMMON, CardColor.RED,
    target=CardTarget.ALL_ENEMIES,
    description="Deal 5 damage to ALL enemies X times.",
    base_damage=5, upgrade_damage=3,
    effects=[{"action": "custom", "func": "whirlwind"}],
)

# =============================================================================
#  UNCOMMON SKILLS
# =============================================================================

make_card(
    "bloodletting", "Bloodletting", 0, CardType.SKILL, CardRarity.UNCOMMON, CardColor.RED,
    target=CardTarget.SELF,
    description="Lose 3 HP. Gain 2 Energy.",
    base_magic=2, upgrade_magic=1,
    effects=[
        {"action": "lose_hp", "amount": 3},
        {"action": "energy", "amount": 2},
    ],
)

make_card(
    "disarm", "Disarm", 1, CardType.SKILL, CardRarity.UNCOMMON, CardColor.RED,
    target=CardTarget.ENEMY,
    description="Enemy loses 2 Strength. Exhaust.",
    base_magic=2, upgrade_magic=1,
    exhaust=True,
    effects=[
        {"action": "apply_effect", "effect": "Strength", "stacks": -2, "target": "enemy"},
    ],
)

make_card(
    "dual_wield", "Dual Wield", 1, CardType.SKILL, CardRarity.UNCOMMON, CardColor.RED,
    target=CardTarget.SELF,
    description="Create a copy of an Attack or Power card in your hand.",
    base_magic=1, upgrade_magic=1,
    upgrade_description="Create 2 copies of an Attack or Power card in your hand.",
    effects=[{"action": "custom", "func": "dual_wield"}],
)

make_card(
    "entrench", "Entrench", 2, CardType.SKILL, CardRarity.UNCOMMON, CardColor.RED,
    target=CardTarget.SELF,
    description="Double your current Block.",
    upgrade_cost=1,
    effects=[{"action": "custom", "func": "entrench"}],
)

make_card(
    "flame_barrier", "Flame Barrier", 2, CardType.SKILL, CardRarity.UNCOMMON, CardColor.RED,
    target=CardTarget.SELF,
    description="Gain 12 Block. Whenever you are attacked this turn, deal 4 damage back.",
    base_block=12, upgrade_block=4,
    base_magic=4, upgrade_magic=2,
    effects=[
        {"action": "block", "amount": 12},
        {"action": "apply_effect", "effect": "Flame Barrier", "stacks": 4, "target": "self"},
    ],
)

make_card(
    "ghostly_armor", "Ghostly Armor", 1, CardType.SKILL, CardRarity.UNCOMMON, CardColor.RED,
    target=CardTarget.SELF,
    description="Ethereal. Gain 10 Block.",
    base_block=10, upgrade_block=3,
    ethereal=True,
    effects=[{"action": "block", "amount": 10}],
)

make_card(
    "infernal_blade", "Infernal Blade", 1, CardType.SKILL, CardRarity.UNCOMMON, CardColor.RED,
    target=CardTarget.SELF,
    description="Add a random Attack into your hand. It costs 0 this turn. Exhaust.",
    upgrade_cost=0,
    exhaust=True,
    effects=[{"action": "custom", "func": "infernal_blade"}],
)

make_card(
    "second_wind", "Second Wind", 1, CardType.SKILL, CardRarity.UNCOMMON, CardColor.RED,
    target=CardTarget.SELF,
    description="Exhaust all non-Attack cards in your hand and gain 5 Block for each card Exhausted.",
    base_magic=5, upgrade_magic=2,
    effects=[{"action": "custom", "func": "second_wind"}],
)

make_card(
    "seeing_red", "Seeing Red", 1, CardType.SKILL, CardRarity.UNCOMMON, CardColor.RED,
    target=CardTarget.SELF,
    description="Gain 2 Energy. Exhaust.",
    upgrade_cost=0,
    exhaust=True,
    effects=[{"action": "energy", "amount": 2}],
)

make_card(
    "sentinel", "Sentinel", 1, CardType.SKILL, CardRarity.UNCOMMON, CardColor.RED,
    target=CardTarget.SELF,
    description="Gain 5 Block. If this card is Exhausted, gain 2 Energy.",
    base_block=5, upgrade_block=3,
    base_magic=2, upgrade_magic=1,
    effects=[
        {"action": "block", "amount": 5},
        {"action": "custom", "func": "sentinel"},
    ],
)

make_card(
    "shockwave", "Shockwave", 2, CardType.SKILL, CardRarity.UNCOMMON, CardColor.RED,
    target=CardTarget.ALL_ENEMIES,
    description="Apply 3 Weak and 3 Vulnerable to ALL enemies. Exhaust.",
    base_magic=3, upgrade_magic=2,
    exhaust=True,
    effects=[
        {"action": "apply_effect", "effect": "Weak", "stacks": 3, "target": "all_enemies"},
        {"action": "apply_effect", "effect": "Vulnerable", "stacks": 3, "target": "all_enemies"},
    ],
)

make_card(
    "spot_weakness", "Spot Weakness", 1, CardType.SKILL, CardRarity.UNCOMMON, CardColor.RED,
    target=CardTarget.ENEMY,
    description="If the enemy intends to attack, gain 3 Strength.",
    base_magic=3, upgrade_magic=1,
    effects=[{"action": "custom", "func": "spot_weakness"}],
)

# =============================================================================
#  UNCOMMON POWERS
# =============================================================================

make_card(
    "combust", "Combust", 1, CardType.POWER, CardRarity.UNCOMMON, CardColor.RED,
    target=CardTarget.NONE,
    description="At the end of your turn, lose 1 HP and deal 5 damage to ALL enemies.",
    base_magic=5, upgrade_magic=2,
    effects=[
        {"action": "apply_effect", "effect": "Combust", "stacks": 5, "target": "self"},
    ],
)

make_card(
    "dark_embrace", "Dark Embrace", 2, CardType.POWER, CardRarity.UNCOMMON, CardColor.RED,
    target=CardTarget.NONE,
    description="Whenever a card is Exhausted, draw 1 card.",
    upgrade_cost=1,
    effects=[
        {"action": "apply_effect", "effect": "Dark Embrace", "stacks": 1, "target": "self"},
    ],
)

make_card(
    "evolve", "Evolve", 1, CardType.POWER, CardRarity.UNCOMMON, CardColor.RED,
    target=CardTarget.NONE,
    description="Whenever you draw a Status card, draw 1 card.",
    base_magic=1, upgrade_magic=1,
    effects=[
        {"action": "apply_effect", "effect": "Evolve", "stacks": 1, "target": "self"},
    ],
)

make_card(
    "feel_no_pain", "Feel No Pain", 1, CardType.POWER, CardRarity.UNCOMMON, CardColor.RED,
    target=CardTarget.NONE,
    description="Whenever a card is Exhausted, gain 3 Block.",
    base_magic=3, upgrade_magic=1,
    effects=[
        {"action": "apply_effect", "effect": "Feel No Pain", "stacks": 3, "target": "self"},
    ],
)

make_card(
    "fire_breathing", "Fire Breathing", 1, CardType.POWER, CardRarity.UNCOMMON, CardColor.RED,
    target=CardTarget.NONE,
    description="Whenever you draw a Status or Curse card, deal 6 damage to ALL enemies.",
    base_magic=6, upgrade_magic=4,
    effects=[
        {"action": "apply_effect", "effect": "Fire Breathing", "stacks": 6, "target": "self"},
    ],
)

make_card(
    "inflame", "Inflame", 1, CardType.POWER, CardRarity.UNCOMMON, CardColor.RED,
    target=CardTarget.NONE,
    description="Gain 2 Strength.",
    base_magic=2, upgrade_magic=1,
    effects=[
        {"action": "apply_effect", "effect": "Strength", "stacks": 2, "target": "self"},
    ],
)

make_card(
    "metallicize", "Metallicize", 1, CardType.POWER, CardRarity.UNCOMMON, CardColor.RED,
    target=CardTarget.NONE,
    description="At the end of your turn, gain 3 Block.",
    base_magic=3, upgrade_magic=1,
    effects=[
        {"action": "apply_effect", "effect": "Metallicize", "stacks": 3, "target": "self"},
    ],
)

make_card(
    "rage", "Rage", 0, CardType.POWER, CardRarity.UNCOMMON, CardColor.RED,
    target=CardTarget.NONE,
    description="Whenever you play an Attack this turn, gain 3 Block.",
    base_magic=3, upgrade_magic=2,
    effects=[
        {"action": "apply_effect", "effect": "Rage", "stacks": 3, "target": "self"},
    ],
)

make_card(
    "rupture", "Rupture", 1, CardType.POWER, CardRarity.UNCOMMON, CardColor.RED,
    target=CardTarget.NONE,
    description="Whenever you lose HP from a card, gain 1 Strength.",
    base_magic=1, upgrade_magic=1,
    effects=[
        {"action": "apply_effect", "effect": "Rupture", "stacks": 1, "target": "self"},
    ],
)

# =============================================================================
#  RARE ATTACKS
# =============================================================================

make_card(
    "bludgeon", "Bludgeon", 3, CardType.ATTACK, CardRarity.RARE, CardColor.RED,
    target=CardTarget.ENEMY,
    description="Deal 32 damage.",
    base_damage=32, upgrade_damage=10,
    effects=[{"action": "damage", "amount": 32}],
)

make_card(
    "feed", "Feed", 1, CardType.ATTACK, CardRarity.RARE, CardColor.RED,
    target=CardTarget.ENEMY,
    description="Deal 10 damage. If this kills a non-minion enemy, gain 3 permanent Max HP. Exhaust.",
    base_damage=10, upgrade_damage=2,
    base_magic=3, upgrade_magic=1,
    exhaust=True,
    effects=[{"action": "custom", "func": "feed"}],
)

make_card(
    "fiend_fire", "Fiend Fire", 2, CardType.ATTACK, CardRarity.RARE, CardColor.RED,
    target=CardTarget.ENEMY,
    description="Exhaust your hand. Deal 7 damage for each card Exhausted. Exhaust.",
    base_damage=7, upgrade_damage=3,
    exhaust=True,
    effects=[{"action": "custom", "func": "fiend_fire"}],
)

make_card(
    "immolate", "Immolate", 2, CardType.ATTACK, CardRarity.RARE, CardColor.RED,
    target=CardTarget.ALL_ENEMIES,
    description="Deal 21 damage to ALL enemies. Add a Burn into your discard pile.",
    base_damage=21, upgrade_damage=7,
    effects=[
        {"action": "damage", "amount": 21, "target": "all_enemies"},
        {"action": "add_card", "card_id": "burn", "to": "discard", "count": 1},
    ],
)

make_card(
    "reaper", "Reaper", 2, CardType.ATTACK, CardRarity.RARE, CardColor.RED,
    target=CardTarget.ALL_ENEMIES,
    description="Deal 4 damage to ALL enemies. Heal HP equal to unblocked damage. Exhaust.",
    base_damage=4, upgrade_damage=4,
    exhaust=True,
    effects=[{"action": "custom", "func": "reaper"}],
)

# =============================================================================
#  RARE SKILLS
# =============================================================================

make_card(
    "double_tap", "Double Tap", 1, CardType.SKILL, CardRarity.RARE, CardColor.RED,
    target=CardTarget.SELF,
    description="This turn, your next Attack is played twice.",
    upgrade_description="This turn, your next 2 Attacks are played twice.",
    base_magic=1, upgrade_magic=1,
    effects=[
        {"action": "apply_effect", "effect": "Double Tap", "stacks": 1, "target": "self"},
    ],
)

make_card(
    "exhume", "Exhume", 2, CardType.SKILL, CardRarity.RARE, CardColor.RED,
    target=CardTarget.SELF,
    description="Put a card from your Exhaust pile into your hand. Exhaust.",
    upgrade_cost=1,
    exhaust=True,
    effects=[{"action": "custom", "func": "exhume"}],
)

make_card(
    "impervious", "Impervious", 2, CardType.SKILL, CardRarity.RARE, CardColor.RED,
    target=CardTarget.SELF,
    description="Gain 30 Block. Exhaust.",
    base_block=30, upgrade_block=10,
    exhaust=True,
    effects=[{"action": "block", "amount": 30}],
)

make_card(
    "limit_break", "Limit Break", 1, CardType.SKILL, CardRarity.RARE, CardColor.RED,
    target=CardTarget.SELF,
    description="Double your Strength. Exhaust.",
    exhaust=True,
    upgrade_description="Double your Strength.",
    effects=[{"action": "custom", "func": "limit_break"}],
)

make_card(
    "offering", "Offering", 0, CardType.SKILL, CardRarity.RARE, CardColor.RED,
    target=CardTarget.SELF,
    description="Lose 6 HP. Gain 2 Energy. Draw 3 cards. Exhaust.",
    base_magic=3, upgrade_magic=2,
    exhaust=True,
    effects=[
        {"action": "lose_hp", "amount": 6},
        {"action": "energy", "amount": 2},
        {"action": "draw", "amount": 3},
    ],
)

# =============================================================================
#  RARE POWERS
# =============================================================================

make_card(
    "barricade", "Barricade", 3, CardType.POWER, CardRarity.RARE, CardColor.RED,
    target=CardTarget.NONE,
    description="Block is not removed at the start of your turn.",
    upgrade_cost=2,
    effects=[
        {"action": "apply_effect", "effect": "Barricade", "stacks": 1, "target": "self"},
    ],
)

make_card(
    "berserk", "Berserk", 0, CardType.POWER, CardRarity.RARE, CardColor.RED,
    target=CardTarget.NONE,
    description="Gain 2 Vulnerable. At the start of your turn, gain 1 Energy.",
    base_magic=2, upgrade_magic=-1,
    effects=[
        {"action": "apply_effect", "effect": "Vulnerable", "stacks": 2, "target": "self"},
        {"action": "apply_effect", "effect": "Berserk", "stacks": 1, "target": "self"},
    ],
)

make_card(
    "brutality", "Brutality", 0, CardType.POWER, CardRarity.RARE, CardColor.RED,
    target=CardTarget.NONE,
    description="At the start of your turn, lose 1 HP and draw 1 card.",
    innate=False,
    upgrade_description="Innate. At the start of your turn, lose 1 HP and draw 1 card.",
    effects=[
        {"action": "apply_effect", "effect": "Brutality", "stacks": 1, "target": "self"},
    ],
)

make_card(
    "corruption", "Corruption", 3, CardType.POWER, CardRarity.RARE, CardColor.RED,
    target=CardTarget.NONE,
    description="Skills cost 0. Whenever you play a Skill, Exhaust it.",
    upgrade_cost=2,
    effects=[
        {"action": "apply_effect", "effect": "Corruption", "stacks": 1, "target": "self"},
    ],
)

make_card(
    "demon_form", "Demon Form", 3, CardType.POWER, CardRarity.RARE, CardColor.RED,
    target=CardTarget.NONE,
    description="At the start of your turn, gain 2 Strength.",
    base_magic=2, upgrade_magic=1,
    effects=[
        {"action": "apply_effect", "effect": "Demon Form", "stacks": 2, "target": "self"},
    ],
)

make_card(
    "juggernaut", "Juggernaut", 2, CardType.POWER, CardRarity.RARE, CardColor.RED,
    target=CardTarget.NONE,
    description="Whenever you gain Block, deal 5 damage to a random enemy.",
    base_magic=5, upgrade_magic=2,
    effects=[
        {"action": "apply_effect", "effect": "Juggernaut", "stacks": 5, "target": "self"},
    ],
)
