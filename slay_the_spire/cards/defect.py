"""Defect card pool - all cards for the Defect character."""
from slay_the_spire.card import (
    make_card, CardType, CardRarity, CardColor, CardTarget,
)

# Shorthand aliases
_ATK = CardType.ATTACK
_SKL = CardType.SKILL
_PWR = CardType.POWER
_B = CardRarity.BASIC
_C = CardRarity.COMMON
_U = CardRarity.UNCOMMON
_R = CardRarity.RARE
_BLUE = CardColor.BLUE
_ENEMY = CardTarget.ENEMY
_ALL = CardTarget.ALL_ENEMIES
_SELF = CardTarget.SELF
_NONE = CardTarget.NONE


# ===========================================================================
#  BASIC cards (4)
# ===========================================================================

make_card(
    "defect_strike", "Strike", 1, _ATK, _B, _BLUE,
    target=_ENEMY,
    description="Deal 6 damage.",
    base_damage=6, upgrade_damage=3,
    upgrade_description="Deal 9 damage.",
    effects=[{"action": "damage", "times": 1}],
)

make_card(
    "defect_defend", "Defend", 1, _SKL, _B, _BLUE,
    target=_SELF,
    description="Gain 5 Block.",
    base_block=5, upgrade_block=3,
    upgrade_description="Gain 8 Block.",
    effects=[{"action": "block"}],
)

make_card(
    "zap", "Zap", 1, _SKL, _B, _BLUE,
    target=_SELF,
    description="Channel 1 Lightning orb.",
    upgrade_cost=0,
    upgrade_description="Channel 1 Lightning orb.",
    effects=[{"action": "channel_orb", "orb": "Lightning"}],
)

make_card(
    "dualcast", "Dualcast", 1, _SKL, _B, _BLUE,
    target=_SELF,
    description="Evoke your next orb twice.",
    upgrade_cost=0,
    upgrade_description="Evoke your next orb twice.",
    effects=[{"action": "evoke", "count": 2}],
)


# ===========================================================================
#  COMMON ATTACKS (9)
# ===========================================================================

make_card(
    "ball_lightning", "Ball Lightning", 1, _ATK, _C, _BLUE,
    target=_ENEMY,
    description="Deal 7 damage. Channel 1 Lightning orb.",
    base_damage=7, upgrade_damage=3,
    upgrade_description="Deal 10 damage. Channel 1 Lightning orb.",
    effects=[
        {"action": "damage", "times": 1},
        {"action": "channel_orb", "orb": "Lightning"},
    ],
)

make_card(
    "barrage", "Barrage", 1, _ATK, _C, _BLUE,
    target=_ENEMY,
    description="Deal 4 damage for each channeled orb.",
    base_damage=4, upgrade_damage=2,
    upgrade_description="Deal 6 damage for each channeled orb.",
    effects=[{"action": "damage", "times": 0, "per_orb": True}],
)

make_card(
    "beam_cell", "Beam Cell", 0, _ATK, _C, _BLUE,
    target=_ENEMY,
    description="Deal 3 damage. Apply 1 Vulnerable.",
    base_damage=3, upgrade_damage=1,
    base_magic=1, upgrade_magic=1,
    upgrade_description="Deal 4 damage. Apply 2 Vulnerable.",
    effects=[
        {"action": "damage", "times": 1},
        {"action": "apply_effect", "effect": "Vulnerable", "stacks": 1, "target": "enemy"},
    ],
)

make_card(
    "cold_snap", "Cold Snap", 1, _ATK, _C, _BLUE,
    target=_ENEMY,
    description="Deal 6 damage. Channel 1 Frost orb.",
    base_damage=6, upgrade_damage=3,
    upgrade_description="Deal 9 damage. Channel 1 Frost orb.",
    effects=[
        {"action": "damage", "times": 1},
        {"action": "channel_orb", "orb": "Frost"},
    ],
)

make_card(
    "compile_driver", "Compile Driver", 1, _ATK, _C, _BLUE,
    target=_ENEMY,
    description="Deal 7 damage. Draw 1 card for each unique orb type channeled.",
    base_damage=7, upgrade_damage=3,
    upgrade_description="Deal 10 damage. Draw 1 card for each unique orb type channeled.",
    effects=[
        {"action": "damage", "times": 1},
        {"action": "custom", "func": "draw_per_unique_orb"},
    ],
)

make_card(
    "go_for_the_eyes", "Go for the Eyes", 0, _ATK, _C, _BLUE,
    target=_ENEMY,
    description="Deal 3 damage. If the enemy intends to attack, apply 1 Weak.",
    base_damage=3, upgrade_damage=1,
    base_magic=1, upgrade_magic=1,
    upgrade_description="Deal 4 damage. If the enemy intends to attack, apply 2 Weak.",
    effects=[
        {"action": "damage", "times": 1},
        {"action": "apply_effect", "effect": "Weak", "stacks": 1, "target": "enemy",
         "condition": "enemy_attacking"},
    ],
)

make_card(
    "rebound", "Rebound", 1, _ATK, _C, _BLUE,
    target=_ENEMY,
    description="Deal 9 damage. The next card you play this turn is placed on top of your draw pile.",
    base_damage=9, upgrade_damage=3,
    upgrade_description="Deal 12 damage. The next card you play this turn is placed on top of your draw pile.",
    effects=[
        {"action": "damage", "times": 1},
        {"action": "apply_effect", "effect": "Rebound", "stacks": 1, "target": "self"},
    ],
)

make_card(
    "streamline", "Streamline", 2, _ATK, _C, _BLUE,
    target=_ENEMY,
    description="Deal 15 damage. Costs 1 less this combat each time it is played.",
    base_damage=15, upgrade_damage=5,
    upgrade_description="Deal 20 damage. Costs 1 less this combat each time it is played.",
    effects=[
        {"action": "damage", "times": 1},
        {"action": "custom", "func": "reduce_cost_permanently", "amount": 1},
    ],
)

make_card(
    "sweeping_beam", "Sweeping Beam", 1, _ATK, _C, _BLUE,
    target=_ALL,
    description="Deal 6 damage to ALL enemies. Draw 1 card.",
    base_damage=6, upgrade_damage=3,
    upgrade_description="Deal 9 damage to ALL enemies. Draw 1 card.",
    effects=[
        {"action": "damage", "times": 1},
        {"action": "draw", "amount": 1},
    ],
)


# ===========================================================================
#  COMMON SKILLS (9)
# ===========================================================================

make_card(
    "charge_battery", "Charge Battery", 1, _SKL, _C, _BLUE,
    target=_SELF,
    description="Gain 7 Block. Next turn gain 1 Energy.",
    base_block=7, upgrade_block=3,
    upgrade_description="Gain 10 Block. Next turn gain 1 Energy.",
    effects=[
        {"action": "block"},
        {"action": "apply_effect", "effect": "Energized", "stacks": 1, "target": "self"},
    ],
)

make_card(
    "chill", "Chill", 0, _SKL, _C, _BLUE,
    target=_SELF,
    exhaust=True,
    description="Channel 1 Frost orb for each enemy in combat. Exhaust.",
    upgrade_description="Channel 1 Frost orb for each enemy in combat. Exhaust.",
    innate=True,
    effects=[{"action": "custom", "func": "channel_frost_per_enemy"}],
)

make_card(
    "coolheaded", "Coolheaded", 1, _SKL, _C, _BLUE,
    target=_SELF,
    description="Channel 1 Frost orb. Draw 1 card.",
    base_magic=1, upgrade_magic=1,
    upgrade_description="Channel 1 Frost orb. Draw 2 cards.",
    effects=[
        {"action": "channel_orb", "orb": "Frost"},
        {"action": "draw", "amount": 1},
    ],
)

make_card(
    "hologram", "Hologram", 1, _SKL, _C, _BLUE,
    target=_SELF,
    description="Gain 3 Block. Put a card from your discard pile on top of your draw pile.",
    base_block=3, upgrade_block=2,
    upgrade_description="Gain 5 Block. Put a card from your discard pile on top of your draw pile.",
    effects=[
        {"action": "block"},
        {"action": "custom", "func": "retrieve_from_discard"},
    ],
)

make_card(
    "leap", "Leap", 1, _SKL, _C, _BLUE,
    target=_SELF,
    description="Gain 9 Block.",
    base_block=9, upgrade_block=3,
    upgrade_description="Gain 12 Block.",
    effects=[{"action": "block"}],
)

make_card(
    "recursion", "Recursion", 1, _SKL, _C, _BLUE,
    target=_SELF,
    description="Evoke your next orb. Channel the orb in your rightmost slot.",
    upgrade_cost=0,
    upgrade_description="Evoke your next orb. Channel the orb in your rightmost slot.",
    effects=[
        {"action": "evoke", "count": 1},
        {"action": "custom", "func": "channel_orb_copy_rightmost"},
    ],
)

make_card(
    "stack", "Stack", 1, _SKL, _C, _BLUE,
    target=_SELF,
    description="Gain Block equal to the number of cards in your discard pile.",
    base_block=0,
    upgrade_description="Gain Block equal to the number of cards in your discard pile.",
    effects=[{"action": "custom", "func": "block_from_discard"}],
)

make_card(
    "steam_barrier", "Steam Barrier", 0, _SKL, _C, _BLUE,
    target=_SELF,
    description="Gain 6 Block. This card's Block is reduced by 1 this combat each time it is played.",
    base_block=6, upgrade_block=2,
    upgrade_description="Gain 8 Block. This card's Block is reduced by 1 this combat each time it is played.",
    effects=[
        {"action": "block"},
        {"action": "custom", "func": "reduce_block_permanent", "amount": 1},
    ],
)

make_card(
    "turbo", "Turbo", 0, _SKL, _C, _BLUE,
    target=_SELF,
    description="Gain 2 Energy. Add a Void card to your discard pile.",
    base_magic=2,
    upgrade_description="Gain 2 Energy. Add a Void card to your discard pile.",
    effects=[
        {"action": "energy", "amount": 2},
        {"action": "custom", "func": "add_card_to_discard", "card_id": "void"},
    ],
)


# ===========================================================================
#  UNCOMMON ATTACKS (9)
# ===========================================================================

make_card(
    "blizzard", "Blizzard", 1, _ATK, _U, _BLUE,
    target=_ALL,
    description="Deal damage to ALL enemies equal to 2 x the number of Frost channeled this combat.",
    base_damage=2, upgrade_damage=2,
    upgrade_description="Deal damage to ALL enemies equal to 4 x the number of Frost channeled this combat.",
    effects=[{"action": "custom", "func": "damage_per_frost_channeled", "multiplier": 2}],
)

make_card(
    "claw", "Claw", 0, _ATK, _U, _BLUE,
    target=_ENEMY,
    description="Deal 3 damage. Increase the damage of ALL Claw cards by 2 this combat.",
    base_damage=3, upgrade_damage=2,
    upgrade_description="Deal 5 damage. Increase the damage of ALL Claw cards by 2 this combat.",
    effects=[
        {"action": "damage", "times": 1},
        {"action": "custom", "func": "claw_bonus", "amount": 2},
    ],
)

make_card(
    "doom_and_gloom", "Doom and Gloom", 2, _ATK, _U, _BLUE,
    target=_ALL,
    description="Deal 10 damage to ALL enemies. Channel 1 Dark orb.",
    base_damage=10, upgrade_damage=4,
    upgrade_description="Deal 14 damage to ALL enemies. Channel 1 Dark orb.",
    effects=[
        {"action": "damage", "times": 1},
        {"action": "channel_orb", "orb": "Dark"},
    ],
)

make_card(
    "ftl", "FTL", 0, _ATK, _U, _BLUE,
    target=_ENEMY,
    description="Deal 5 damage. If you have played fewer than 3 cards this turn, draw 1 card.",
    base_damage=5, upgrade_damage=1,
    base_magic=3, upgrade_magic=1,
    upgrade_description="Deal 6 damage. If you have played fewer than 4 cards this turn, draw 1 card.",
    effects=[
        {"action": "damage", "times": 1},
        {"action": "draw", "amount": 1, "condition": "cards_played_less_than", "threshold": 3},
    ],
)

make_card(
    "lockon", "Lock-On", 1, _ATK, _U, _BLUE,
    target=_ENEMY,
    description="Deal 12 damage. Apply 1 Lock-On. (Orbs deal 50% more damage to this enemy.)",
    base_damage=12, upgrade_damage=2,
    base_magic=1, upgrade_magic=1,
    upgrade_description="Deal 14 damage. Apply 2 Lock-On.",
    effects=[
        {"action": "damage", "times": 1},
        {"action": "apply_effect", "effect": "LockOn", "stacks": 1, "target": "enemy"},
    ],
)

make_card(
    "melter", "Melter", 1, _ATK, _U, _BLUE,
    target=_ENEMY,
    description="Remove all Block from an enemy. Deal 10 damage.",
    base_damage=10, upgrade_damage=4,
    upgrade_description="Remove all Block from an enemy. Deal 14 damage.",
    effects=[
        {"action": "custom", "func": "remove_enemy_block"},
        {"action": "damage", "times": 1},
    ],
)

make_card(
    "rip_and_tear", "Rip and Tear", 1, _ATK, _U, _BLUE,
    target=_ENEMY,
    description="Deal 7 damage twice to a random enemy.",
    base_damage=7, upgrade_damage=2,
    upgrade_description="Deal 9 damage twice to a random enemy.",
    effects=[{"action": "damage", "times": 2, "random_target": True}],
)

make_card(
    "scrape", "Scrape", 1, _ATK, _U, _BLUE,
    target=_ENEMY,
    description="Deal 7 damage. Draw 4 cards. Discard all drawn cards that cost more than 0.",
    base_damage=7, upgrade_damage=3,
    base_magic=4, upgrade_magic=1,
    upgrade_description="Deal 10 damage. Draw 5 cards. Discard all drawn cards that cost more than 0.",
    effects=[
        {"action": "damage", "times": 1},
        {"action": "custom", "func": "draw_and_discard_nonzero", "amount": 4},
    ],
)

make_card(
    "sunder", "Sunder", 3, _ATK, _U, _BLUE,
    target=_ENEMY,
    description="Deal 24 damage. If this kills the enemy, gain 3 Energy.",
    base_damage=24, upgrade_damage=8,
    upgrade_description="Deal 32 damage. If this kills the enemy, gain 3 Energy.",
    effects=[
        {"action": "damage", "times": 1},
        {"action": "custom", "func": "energy_on_kill", "amount": 3},
    ],
)


# ===========================================================================
#  UNCOMMON SKILLS (18)
# ===========================================================================

make_card(
    "aggregate", "Aggregate", 1, _SKL, _U, _BLUE,
    target=_SELF,
    description="Gain Energy for every 4 cards in your draw pile.",
    base_magic=4, upgrade_magic=-1,
    upgrade_description="Gain Energy for every 3 cards in your draw pile.",
    effects=[{"action": "custom", "func": "energy_per_cards_in_draw", "divisor": 4}],
)

make_card(
    "auto_shields", "Auto-Shields", 1, _SKL, _U, _BLUE,
    target=_SELF,
    description="If you have no Block, gain 11 Block.",
    base_block=11, upgrade_block=4,
    upgrade_description="If you have no Block, gain 15 Block.",
    effects=[{"action": "block", "condition": "no_block"}],
)

make_card(
    "boot_sequence", "Boot Sequence", 0, _SKL, _U, _BLUE,
    target=_SELF,
    innate=True,
    description="Innate. Gain 10 Block. Exhaust.",
    base_block=10, upgrade_block=3,
    exhaust=True,
    upgrade_description="Innate. Gain 13 Block. Exhaust.",
    effects=[{"action": "block"}],
)

make_card(
    "chaos", "Chaos", 1, _SKL, _U, _BLUE,
    target=_SELF,
    description="Channel 1 random orb.",
    base_magic=1, upgrade_magic=1,
    upgrade_description="Channel 2 random orbs.",
    effects=[{"action": "channel_orb", "orb": "Random"}],
)

make_card(
    "consume", "Consume", 2, _SKL, _U, _BLUE,
    target=_SELF,
    description="Gain 2 Focus. Lose 1 orb slot.",
    base_magic=2, upgrade_magic=1,
    upgrade_description="Gain 3 Focus. Lose 1 orb slot.",
    effects=[
        {"action": "apply_effect", "effect": "Focus", "stacks": 2, "target": "self"},
        {"action": "custom", "func": "increase_orb_slots", "amount": -1},
    ],
)

make_card(
    "darkness", "Darkness", 1, _SKL, _U, _BLUE,
    target=_SELF,
    description="Channel 1 Dark orb.",
    upgrade_cost=0,
    upgrade_description="Channel 1 Dark orb.",
    effects=[{"action": "channel_orb", "orb": "Dark"}],
)

make_card(
    "equilibrium", "Equilibrium", 2, _SKL, _U, _BLUE,
    target=_SELF,
    description="Gain 13 Block. Retain your hand this turn.",
    base_block=13, upgrade_block=3,
    upgrade_description="Gain 16 Block. Retain your hand this turn.",
    effects=[
        {"action": "block"},
        {"action": "custom", "func": "retain_hand"},
    ],
)

make_card(
    "force_field", "Force Field", 4, _SKL, _U, _BLUE,
    target=_SELF,
    description="Costs 1 less for each Power you have in play. Gain 12 Block.",
    base_block=12, upgrade_block=4,
    upgrade_description="Costs 1 less for each Power you have in play. Gain 16 Block.",
    effects=[
        {"action": "custom", "func": "cost_reduction_per_power"},
        {"action": "block"},
    ],
)

make_card(
    "fusion", "Fusion", 2, _SKL, _U, _BLUE,
    target=_SELF,
    description="Channel 1 Plasma orb.",
    upgrade_cost=1,
    upgrade_description="Channel 1 Plasma orb.",
    effects=[{"action": "channel_orb", "orb": "Plasma"}],
)

make_card(
    "genetic_algorithm", "Genetic Algorithm", 1, _SKL, _U, _BLUE,
    target=_SELF,
    exhaust=True,
    description="Gain 1 Block. Permanently increase this card's Block by 2. Exhaust.",
    base_block=1, upgrade_block=0,
    base_magic=2, upgrade_magic=1,
    upgrade_description="Gain 1 Block. Permanently increase this card's Block by 3. Exhaust.",
    effects=[
        {"action": "block"},
        {"action": "custom", "func": "permanent_block_increase", "amount": 2},
    ],
)

make_card(
    "glacier", "Glacier", 2, _SKL, _U, _BLUE,
    target=_SELF,
    description="Gain 7 Block. Channel 2 Frost orbs.",
    base_block=7, upgrade_block=3,
    upgrade_description="Gain 10 Block. Channel 2 Frost orbs.",
    effects=[
        {"action": "block"},
        {"action": "channel_orb", "orb": "Frost"},
        {"action": "channel_orb", "orb": "Frost"},
    ],
)

make_card(
    "overclock", "Overclock", 0, _SKL, _U, _BLUE,
    target=_SELF,
    description="Draw 2 cards. Add a Burn card to your discard pile.",
    base_magic=2, upgrade_magic=1,
    upgrade_description="Draw 3 cards. Add a Burn card to your discard pile.",
    effects=[
        {"action": "draw", "amount": 2},
        {"action": "custom", "func": "add_card_to_discard", "card_id": "burn"},
    ],
)

make_card(
    "recycle", "Recycle", 1, _SKL, _U, _BLUE,
    target=_SELF,
    exhaust=False,
    description="Exhaust a card from your hand. Gain Energy equal to its cost.",
    upgrade_cost=0,
    upgrade_description="Exhaust a card from your hand. Gain Energy equal to its cost.",
    effects=[{"action": "custom", "func": "exhaust_for_energy"}],
)

make_card(
    "reinforced_body", "Reinforced Body", -1, _SKL, _U, _BLUE,
    target=_SELF,
    description="Gain 7 Block X times.",
    base_block=7, upgrade_block=2,
    upgrade_description="Gain 9 Block X times.",
    effects=[{"action": "custom", "func": "block_x_times", "amount": 7}],
)

make_card(
    "reprogram", "Reprogram", 1, _SKL, _U, _BLUE,
    target=_SELF,
    description="Lose 1 Focus. Gain 1 Strength. Gain 1 Dexterity.",
    base_magic=1, upgrade_magic=1,
    upgrade_description="Lose 2 Focus. Gain 2 Strength. Gain 2 Dexterity.",
    effects=[
        {"action": "apply_effect", "effect": "Focus", "stacks": -1, "target": "self"},
        {"action": "apply_effect", "effect": "Strength", "stacks": 1, "target": "self"},
        {"action": "apply_effect", "effect": "Dexterity", "stacks": 1, "target": "self"},
    ],
)

make_card(
    "skim", "Skim", 1, _SKL, _U, _BLUE,
    target=_SELF,
    description="Draw 3 cards.",
    base_magic=3, upgrade_magic=1,
    upgrade_description="Draw 4 cards.",
    effects=[{"action": "draw", "amount": 3}],
)

make_card(
    "tempest", "Tempest", -1, _SKL, _U, _BLUE,
    target=_SELF,
    exhaust=True,
    description="Channel X Lightning orbs. Exhaust.",
    upgrade_description="Channel X+1 Lightning orbs. Exhaust.",
    effects=[{"action": "custom", "func": "channel_lightning_x"}],
)

make_card(
    "white_noise", "White Noise", 1, _SKL, _U, _BLUE,
    target=_SELF,
    exhaust=True,
    description="Add a random Power card to your hand. It costs 0 this turn. Exhaust.",
    upgrade_cost=0,
    upgrade_description="Add a random Power card to your hand. It costs 0 this turn. Exhaust.",
    effects=[{"action": "custom", "func": "add_random_power_to_hand", "cost_override": 0}],
)


# ===========================================================================
#  UNCOMMON POWERS (8)
# ===========================================================================

make_card(
    "capacitor", "Capacitor", 1, _PWR, _U, _BLUE,
    target=_SELF,
    description="Gain 2 orb slots.",
    base_magic=2, upgrade_magic=1,
    upgrade_description="Gain 3 orb slots.",
    effects=[{"action": "custom", "func": "increase_orb_slots", "amount": 2}],
)

make_card(
    "defragment", "Defragment", 1, _PWR, _U, _BLUE,
    target=_SELF,
    description="Gain 1 Focus.",
    base_magic=1, upgrade_magic=1,
    upgrade_description="Gain 2 Focus.",
    effects=[{"action": "apply_effect", "effect": "Focus", "stacks": 1, "target": "self"}],
)

make_card(
    "heatsinks", "Heatsinks", 1, _PWR, _U, _BLUE,
    target=_SELF,
    description="Whenever you play a Power card, draw 1 card.",
    base_magic=1, upgrade_magic=1,
    upgrade_description="Whenever you play a Power card, draw 2 cards.",
    effects=[{"action": "apply_effect", "effect": "Heatsinks", "stacks": 1, "target": "self"}],
)

make_card(
    "hello_world", "Hello World", 1, _PWR, _U, _BLUE,
    target=_SELF,
    description="At the start of each turn, add a random Common card to your hand.",
    upgrade_cost=0,
    upgrade_description="At the start of each turn, add a random Common card to your hand.",
    effects=[{"action": "apply_effect", "effect": "HelloWorld", "stacks": 1, "target": "self"}],
)

make_card(
    "loop", "Loop", 1, _PWR, _U, _BLUE,
    target=_SELF,
    description="At the start of each turn, trigger the passive of your next orb.",
    base_magic=1, upgrade_magic=1,
    upgrade_description="At the start of each turn, trigger the passive of your next orb 2 times.",
    effects=[{"action": "apply_effect", "effect": "Loop", "stacks": 1, "target": "self"}],
)

make_card(
    "self_repair", "Self Repair", 1, _PWR, _U, _BLUE,
    target=_SELF,
    description="At the end of combat, heal 7 HP.",
    base_magic=7, upgrade_magic=3,
    upgrade_description="At the end of combat, heal 10 HP.",
    effects=[{"action": "apply_effect", "effect": "SelfRepair", "stacks": 7, "target": "self"}],
)

make_card(
    "static_discharge", "Static Discharge", 1, _PWR, _U, _BLUE,
    target=_SELF,
    description="Whenever you receive unblocked attack damage, channel 1 Lightning orb.",
    base_magic=1, upgrade_magic=1,
    upgrade_description="Whenever you receive unblocked attack damage, channel 2 Lightning orbs.",
    effects=[{"action": "apply_effect", "effect": "StaticDischarge", "stacks": 1, "target": "self"}],
)

make_card(
    "storm", "Storm", 1, _PWR, _U, _BLUE,
    target=_SELF,
    description="Whenever you play a Power card, channel 1 Lightning orb.",
    upgrade_cost=0,
    upgrade_description="Whenever you play a Power card, channel 1 Lightning orb.",
    effects=[{"action": "apply_effect", "effect": "Storm", "stacks": 1, "target": "self"}],
)


# ===========================================================================
#  RARE ATTACKS (5)
# ===========================================================================

make_card(
    "all_for_one", "All for One", 2, _ATK, _R, _BLUE,
    target=_ENEMY,
    description="Deal 10 damage. Put all cost 0 cards from your discard pile into your hand.",
    base_damage=10, upgrade_damage=4,
    upgrade_description="Deal 14 damage. Put all cost 0 cards from your discard pile into your hand.",
    effects=[
        {"action": "damage", "times": 1},
        {"action": "custom", "func": "retrieve_zero_cost_from_discard"},
    ],
)

make_card(
    "core_surge", "Core Surge", 1, _ATK, _R, _BLUE,
    target=_ENEMY,
    exhaust=True,
    description="Deal 11 damage. Gain 1 Artifact. Exhaust.",
    base_damage=11, upgrade_damage=4,
    upgrade_description="Deal 15 damage. Gain 1 Artifact. Exhaust.",
    effects=[
        {"action": "damage", "times": 1},
        {"action": "apply_effect", "effect": "Artifact", "stacks": 1, "target": "self"},
    ],
)

make_card(
    "hyperbeam", "Hyperbeam", 2, _ATK, _R, _BLUE,
    target=_ALL,
    description="Deal 26 damage to ALL enemies. Lose 3 Focus.",
    base_damage=26, upgrade_damage=8,
    upgrade_description="Deal 34 damage to ALL enemies. Lose 3 Focus.",
    effects=[
        {"action": "damage", "times": 1},
        {"action": "apply_effect", "effect": "Focus", "stacks": -3, "target": "self"},
    ],
)

make_card(
    "meteor_strike", "Meteor Strike", 5, _ATK, _R, _BLUE,
    target=_ENEMY,
    description="Deal 24 damage. Channel 3 Plasma orbs.",
    base_damage=24, upgrade_damage=6,
    upgrade_description="Deal 30 damage. Channel 3 Plasma orbs.",
    effects=[
        {"action": "damage", "times": 1},
        {"action": "channel_orb", "orb": "Plasma"},
        {"action": "channel_orb", "orb": "Plasma"},
        {"action": "channel_orb", "orb": "Plasma"},
    ],
)

make_card(
    "thunder_strike", "Thunder Strike", 3, _ATK, _R, _BLUE,
    target=_ALL,
    description="Deal 7 damage to a random enemy for each Lightning channeled this combat.",
    base_damage=7, upgrade_damage=2,
    upgrade_description="Deal 9 damage to a random enemy for each Lightning channeled this combat.",
    effects=[{"action": "custom", "func": "damage_per_lightning_channeled", "amount": 7}],
)


# ===========================================================================
#  RARE SKILLS (5)
# ===========================================================================

make_card(
    "amplify", "Amplify", 1, _SKL, _R, _BLUE,
    target=_SELF,
    exhaust=True,
    description="This turn, your next Power is played twice. Exhaust.",
    upgrade_cost=0,
    upgrade_description="This turn, your next 2 Powers are played twice. Exhaust.",
    effects=[{"action": "apply_effect", "effect": "Amplify", "stacks": 1, "target": "self"}],
)

make_card(
    "fission", "Fission", 0, _SKL, _R, _BLUE,
    target=_SELF,
    exhaust=True,
    description="Remove all channeled orbs (without evoking). Gain 1 Energy and draw 1 card per orb removed. Exhaust.",
    upgrade_description="Evoke all channeled orbs. Gain 1 Energy and draw 1 card per orb removed. Exhaust.",
    effects=[{"action": "custom", "func": "fission", "evoke_on_remove": False}],
)

make_card(
    "multi_cast", "Multi-Cast", -1, _SKL, _R, _BLUE,
    target=_SELF,
    description="Evoke your next orb X times.",
    upgrade_description="Evoke your next orb X+1 times.",
    effects=[{"action": "evoke", "count": "X"}],
)

make_card(
    "rainbow", "Rainbow", 2, _SKL, _R, _BLUE,
    target=_SELF,
    exhaust=True,
    description="Channel 1 Lightning, 1 Frost, and 1 Dark orb. Exhaust.",
    upgrade_cost=1,
    upgrade_description="Channel 1 Lightning, 1 Frost, and 1 Dark orb. Exhaust.",
    effects=[
        {"action": "channel_orb", "orb": "Lightning"},
        {"action": "channel_orb", "orb": "Frost"},
        {"action": "channel_orb", "orb": "Dark"},
    ],
)

make_card(
    "seek", "Seek", 0, _SKL, _R, _BLUE,
    target=_SELF,
    exhaust=True,
    description="Choose 1 card from your draw pile and put it into your hand. Exhaust.",
    base_magic=1, upgrade_magic=1,
    upgrade_description="Choose 2 cards from your draw pile and put them into your hand. Exhaust.",
    effects=[{"action": "custom", "func": "seek_from_draw_pile", "count": 1}],
)


# ===========================================================================
#  RARE POWERS (6)
# ===========================================================================

make_card(
    "biased_cognition", "Biased Cognition", 1, _PWR, _R, _BLUE,
    target=_SELF,
    description="Gain 4 Focus. At the start of each turn, lose 1 Focus.",
    base_magic=4, upgrade_magic=1,
    upgrade_description="Gain 5 Focus. At the start of each turn, lose 1 Focus.",
    effects=[
        {"action": "apply_effect", "effect": "Focus", "stacks": 4, "target": "self"},
        {"action": "apply_effect", "effect": "BiasedCognition", "stacks": 1, "target": "self"},
    ],
)

make_card(
    "buffer", "Buffer", 2, _PWR, _R, _BLUE,
    target=_SELF,
    description="Gain 1 Buffer. (Prevent the next time you would lose HP.)",
    base_magic=1, upgrade_magic=1,
    upgrade_description="Gain 2 Buffer. (Prevent the next time you would lose HP.)",
    effects=[{"action": "apply_effect", "effect": "Buffer", "stacks": 1, "target": "self"}],
)

make_card(
    "creative_ai", "Creative AI", 3, _PWR, _R, _BLUE,
    target=_SELF,
    description="At the start of each turn, add a random Power card to your hand.",
    upgrade_cost=2,
    upgrade_description="At the start of each turn, add a random Power card to your hand.",
    effects=[{"action": "apply_effect", "effect": "CreativeAI", "stacks": 1, "target": "self"}],
)

make_card(
    "echo_form", "Echo Form", 3, _PWR, _R, _BLUE,
    target=_SELF,
    ethereal=True,
    description="Ethereal. The first card you play each turn is played twice.",
    upgrade_description="The first card you play each turn is played twice.",
    effects=[{"action": "apply_effect", "effect": "EchoForm", "stacks": 1, "target": "self"}],
)

make_card(
    "electrodynamics", "Electrodynamics", 2, _PWR, _R, _BLUE,
    target=_SELF,
    description="Lightning now hits ALL enemies. Channel 2 Lightning orbs.",
    base_magic=2, upgrade_magic=1,
    upgrade_description="Lightning now hits ALL enemies. Channel 3 Lightning orbs.",
    effects=[
        {"action": "apply_effect", "effect": "Electrodynamics", "stacks": 1, "target": "self"},
        {"action": "channel_orb", "orb": "Lightning"},
        {"action": "channel_orb", "orb": "Lightning"},
    ],
)

make_card(
    "machine_learning", "Machine Learning", 1, _PWR, _R, _BLUE,
    target=_SELF,
    description="At the start of each turn, draw 1 additional card.",
    base_magic=1, upgrade_magic=1,
    upgrade_description="At the start of each turn, draw 2 additional cards.",
    effects=[{"action": "apply_effect", "effect": "MachineLearning", "stacks": 1, "target": "self"}],
)
