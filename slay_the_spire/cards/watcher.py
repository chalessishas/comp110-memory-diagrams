"""Watcher card pool - all cards for the Watcher character."""
from slay_the_spire.card import (
    make_card, CardType, CardRarity, CardColor, CardTarget,
)

# =============================================================================
#  BASIC (starter cards)
# =============================================================================

make_card(
    "watcher_strike", "Strike", 1, CardType.ATTACK, CardRarity.BASIC, CardColor.PURPLE,
    target=CardTarget.ENEMY,
    description="Deal 6 damage.",
    base_damage=6, upgrade_damage=3,
    effects=[{"action": "damage"}],
)

make_card(
    "watcher_defend", "Defend", 1, CardType.SKILL, CardRarity.BASIC, CardColor.PURPLE,
    target=CardTarget.SELF,
    description="Gain 5 Block.",
    base_block=5, upgrade_block=3,
    effects=[{"action": "block"}],
)

make_card(
    "eruption", "Eruption", 2, CardType.ATTACK, CardRarity.BASIC, CardColor.PURPLE,
    target=CardTarget.ENEMY,
    description="Deal 9 damage. Enter Wrath.",
    base_damage=9, upgrade_damage=0,
    upgrade_cost=1,
    effects=[
        {"action": "damage"},
        {"action": "enter_stance", "stance": "Wrath"},
    ],
    upgrade_description="Deal 9 damage. Enter Wrath.",
)

make_card(
    "vigilance", "Vigilance", 2, CardType.SKILL, CardRarity.BASIC, CardColor.PURPLE,
    target=CardTarget.SELF,
    description="Gain 8 Block. Enter Calm.",
    base_block=8, upgrade_block=4,
    effects=[
        {"action": "block"},
        {"action": "enter_stance", "stance": "Calm"},
    ],
)

# =============================================================================
#  COMMON ATTACKS
# =============================================================================

make_card(
    "bowling_bash", "Bowling Bash", 1, CardType.ATTACK, CardRarity.COMMON, CardColor.PURPLE,
    target=CardTarget.ENEMY,
    description="Deal 7 damage for each enemy in combat.",
    base_damage=7, upgrade_damage=3,
    effects=[
        {"action": "custom", "func": "bowling_bash_damage"},
    ],
)

make_card(
    "consecrate", "Consecrate", 0, CardType.ATTACK, CardRarity.COMMON, CardColor.PURPLE,
    target=CardTarget.ALL_ENEMIES,
    description="Deal 5 damage to ALL enemies.",
    base_damage=5, upgrade_damage=3,
    effects=[{"action": "damage"}],
)

make_card(
    "crush_joints", "Crush Joints", 1, CardType.ATTACK, CardRarity.COMMON, CardColor.PURPLE,
    target=CardTarget.ENEMY,
    description="Deal 8 damage. If the last card played was a Skill, apply 1 Vulnerable.",
    base_damage=8, upgrade_damage=2,
    base_magic=1, upgrade_magic=1,
    effects=[
        {"action": "damage"},
        {"action": "custom", "func": "crush_joints_vulnerable"},
    ],
)

make_card(
    "cut_through_fate", "Cut Through Fate", 1, CardType.ATTACK, CardRarity.COMMON, CardColor.PURPLE,
    target=CardTarget.ENEMY,
    description="Deal 7 damage. Scry 2. Draw 1 card.",
    base_damage=7, upgrade_damage=2,
    base_magic=2, upgrade_magic=1,
    effects=[
        {"action": "damage"},
        {"action": "scry", "amount": 2},
        {"action": "draw", "amount": 1},
    ],
)

make_card(
    "empty_fist", "Empty Fist", 1, CardType.ATTACK, CardRarity.COMMON, CardColor.PURPLE,
    target=CardTarget.ENEMY,
    description="Deal 9 damage. Exit your Stance.",
    base_damage=9, upgrade_damage=5,
    effects=[
        {"action": "damage"},
        {"action": "exit_stance"},
    ],
)

make_card(
    "flurry_of_blows", "Flurry of Blows", 0, CardType.ATTACK, CardRarity.COMMON, CardColor.PURPLE,
    target=CardTarget.ENEMY,
    description="Deal 4 damage. Whenever you change Stances, return this from the discard pile to your hand.",
    base_damage=4, upgrade_damage=2,
    effects=[
        {"action": "damage"},
        {"action": "custom", "func": "flurry_on_stance_change"},
    ],
)

make_card(
    "flying_sleeves", "Flying Sleeves", 1, CardType.ATTACK, CardRarity.COMMON, CardColor.PURPLE,
    target=CardTarget.ENEMY,
    description="Deal 4 damage twice. Retain.",
    base_damage=4, upgrade_damage=2,
    retain=True,
    effects=[
        {"action": "damage", "times": 2},
    ],
)

make_card(
    "follow_up", "Follow Up", 1, CardType.ATTACK, CardRarity.COMMON, CardColor.PURPLE,
    target=CardTarget.ENEMY,
    description="Deal 7 damage. If the last card played was an Attack, gain 1 Energy.",
    base_damage=7, upgrade_damage=4,
    effects=[
        {"action": "damage"},
        {"action": "custom", "func": "follow_up_energy"},
    ],
)

make_card(
    "halt", "Halt", 0, CardType.SKILL, CardRarity.COMMON, CardColor.PURPLE,
    target=CardTarget.SELF,
    description="Gain 3 Block. If in Wrath, gain 9 additional Block.",
    base_block=3, upgrade_block=1,
    base_magic=9, upgrade_magic=5,
    effects=[
        {"action": "block"},
        {"action": "custom", "func": "halt_wrath_block"},
    ],
)

make_card(
    "just_lucky", "Just Lucky", 0, CardType.ATTACK, CardRarity.COMMON, CardColor.PURPLE,
    target=CardTarget.ENEMY,
    description="Scry 1. Gain 2 Block. Deal 3 damage.",
    base_damage=3, upgrade_damage=1,
    base_block=2, upgrade_block=1,
    base_magic=1, upgrade_magic=1,
    effects=[
        {"action": "scry", "amount": 1},
        {"action": "block"},
        {"action": "damage"},
    ],
)

make_card(
    "sash_whip", "Sash Whip", 1, CardType.ATTACK, CardRarity.COMMON, CardColor.PURPLE,
    target=CardTarget.ENEMY,
    description="Deal 8 damage. If the last card played was an Attack, apply 1 Weak.",
    base_damage=8, upgrade_damage=2,
    base_magic=1, upgrade_magic=1,
    effects=[
        {"action": "damage"},
        {"action": "custom", "func": "sash_whip_weak"},
    ],
)

make_card(
    "reach_heaven", "Reach Heaven", 2, CardType.ATTACK, CardRarity.COMMON, CardColor.PURPLE,
    target=CardTarget.ENEMY,
    description="Deal 10 damage. Shuffle a Through Violence into your draw pile.",
    base_damage=10, upgrade_damage=5,
    effects=[
        {"action": "damage"},
        {"action": "add_card", "card_id": "through_violence", "to": "draw_pile", "count": 1},
    ],
)

# =============================================================================
#  COMMON SKILLS
# =============================================================================

make_card(
    "crescendo", "Crescendo", 1, CardType.SKILL, CardRarity.COMMON, CardColor.PURPLE,
    target=CardTarget.SELF,
    description="Enter Wrath. Exhaust.",
    exhaust=True,
    effects=[
        {"action": "enter_stance", "stance": "Wrath"},
    ],
    upgrade_cost=0,
    upgrade_description="Enter Wrath. Exhaust.",
)

make_card(
    "empty_body", "Empty Body", 1, CardType.SKILL, CardRarity.COMMON, CardColor.PURPLE,
    target=CardTarget.SELF,
    description="Gain 7 Block. Exit your Stance.",
    base_block=7, upgrade_block=3,
    effects=[
        {"action": "block"},
        {"action": "exit_stance"},
    ],
)

make_card(
    "empty_mind", "Empty Mind", 1, CardType.SKILL, CardRarity.COMMON, CardColor.PURPLE,
    target=CardTarget.SELF,
    description="Draw 2 cards. Exit your Stance.",
    base_magic=2, upgrade_magic=1,
    effects=[
        {"action": "draw", "amount": 2},
        {"action": "exit_stance"},
    ],
)

make_card(
    "evaluate", "Evaluate", 1, CardType.SKILL, CardRarity.COMMON, CardColor.PURPLE,
    target=CardTarget.SELF,
    description="Gain 6 Block. Shuffle an Insight into your draw pile.",
    base_block=6, upgrade_block=4,
    effects=[
        {"action": "block"},
        {"action": "add_card", "card_id": "insight", "to": "draw_pile", "count": 1},
    ],
)

make_card(
    "inner_peace", "Inner Peace", 1, CardType.SKILL, CardRarity.COMMON, CardColor.PURPLE,
    target=CardTarget.SELF,
    description="If in Calm, draw 3 cards. Otherwise, enter Calm.",
    base_magic=3, upgrade_magic=1,
    effects=[
        {"action": "custom", "func": "inner_peace"},
    ],
)

make_card(
    "perseverance", "Perseverance", 1, CardType.SKILL, CardRarity.COMMON, CardColor.PURPLE,
    target=CardTarget.SELF,
    description="Gain 5 Block. Retain. Each time this is Retained, increase its Block by 2.",
    base_block=5, upgrade_block=2,
    base_magic=2, upgrade_magic=1,
    retain=True,
    effects=[
        {"action": "block"},
        {"action": "custom", "func": "perseverance_retain_buff"},
    ],
)

make_card(
    "protect", "Protect", 2, CardType.SKILL, CardRarity.COMMON, CardColor.PURPLE,
    target=CardTarget.SELF,
    description="Gain 12 Block. Retain.",
    base_block=12, upgrade_block=4,
    retain=True,
    effects=[
        {"action": "block"},
    ],
)

make_card(
    "third_eye", "Third Eye", 1, CardType.SKILL, CardRarity.COMMON, CardColor.PURPLE,
    target=CardTarget.SELF,
    description="Gain 7 Block. Scry 3.",
    base_block=7, upgrade_block=2,
    base_magic=3, upgrade_magic=2,
    effects=[
        {"action": "block"},
        {"action": "scry", "amount": 3},
    ],
)

make_card(
    "tranquility", "Tranquility", 1, CardType.SKILL, CardRarity.COMMON, CardColor.PURPLE,
    target=CardTarget.SELF,
    description="Enter Calm. Exhaust. Retain.",
    exhaust=True,
    retain=True,
    effects=[
        {"action": "enter_stance", "stance": "Calm"},
    ],
    upgrade_cost=0,
    upgrade_description="Enter Calm. Exhaust. Retain.",
)

make_card(
    "prostrate", "Prostrate", 0, CardType.SKILL, CardRarity.COMMON, CardColor.PURPLE,
    target=CardTarget.SELF,
    description="Gain 2 Mantra. Gain 4 Block.",
    base_block=4, upgrade_block=0,
    base_magic=2, upgrade_magic=3,
    effects=[
        {"action": "apply_effect", "effect": "Mantra", "stacks": 2, "target": "self"},
        {"action": "block"},
    ],
)

make_card(
    "pray", "Pray", 1, CardType.SKILL, CardRarity.COMMON, CardColor.PURPLE,
    target=CardTarget.SELF,
    description="Gain 3 Mantra. Shuffle an Insight into your draw pile.",
    base_magic=3, upgrade_magic=2,
    effects=[
        {"action": "apply_effect", "effect": "Mantra", "stacks": 3, "target": "self"},
        {"action": "add_card", "card_id": "insight", "to": "draw_pile", "count": 1},
    ],
)

# =============================================================================
#  UNCOMMON ATTACKS
# =============================================================================

make_card(
    "carve_reality", "Carve Reality", 1, CardType.ATTACK, CardRarity.UNCOMMON, CardColor.PURPLE,
    target=CardTarget.ENEMY,
    description="Deal 6 damage. Add a Smite to your hand.",
    base_damage=6, upgrade_damage=4,
    effects=[
        {"action": "damage"},
        {"action": "add_card", "card_id": "smite", "to": "hand", "count": 1},
    ],
)

make_card(
    "conclude", "Conclude", 1, CardType.ATTACK, CardRarity.UNCOMMON, CardColor.PURPLE,
    target=CardTarget.ALL_ENEMIES,
    description="Deal 12 damage to ALL enemies. End your turn.",
    base_damage=12, upgrade_damage=4,
    effects=[
        {"action": "damage"},
        {"action": "custom", "func": "conclude_end_turn"},
    ],
)

make_card(
    "fear_no_evil", "Fear No Evil", 1, CardType.ATTACK, CardRarity.UNCOMMON, CardColor.PURPLE,
    target=CardTarget.ENEMY,
    description="Deal 8 damage. If the enemy intends to Attack, enter Calm.",
    base_damage=8, upgrade_damage=3,
    effects=[
        {"action": "damage"},
        {"action": "custom", "func": "fear_no_evil_calm"},
    ],
)

make_card(
    "indignation", "Indignation", 1, CardType.SKILL, CardRarity.UNCOMMON, CardColor.PURPLE,
    target=CardTarget.SELF,
    description="If in Wrath, apply 3 Vulnerable to ALL enemies. Otherwise, enter Wrath.",
    base_magic=3, upgrade_magic=2,
    effects=[
        {"action": "custom", "func": "indignation"},
    ],
)

make_card(
    "sands_of_time", "Sands of Time", 4, CardType.ATTACK, CardRarity.UNCOMMON, CardColor.PURPLE,
    target=CardTarget.ENEMY,
    description="Deal 20 damage. Retain. Whenever this is Retained, reduce its cost by 1.",
    base_damage=20, upgrade_damage=6,
    retain=True,
    effects=[
        {"action": "damage"},
        {"action": "custom", "func": "sands_of_time_retain_reduce"},
    ],
)

make_card(
    "signature_move", "Signature Move", 2, CardType.ATTACK, CardRarity.UNCOMMON, CardColor.PURPLE,
    target=CardTarget.ENEMY,
    description="Can only be played if this is the only Attack in your hand. Deal 30 damage.",
    base_damage=30, upgrade_damage=10,
    effects=[
        {"action": "custom", "func": "signature_move_check_and_damage"},
    ],
)

make_card(
    "talk_to_the_hand", "Talk to the Hand", 1, CardType.ATTACK, CardRarity.UNCOMMON, CardColor.PURPLE,
    target=CardTarget.ENEMY,
    description="Deal 5 damage. Whenever you deal Attack damage to this enemy, gain 2 Block. Exhaust.",
    base_damage=5, upgrade_damage=2,
    base_magic=2, upgrade_magic=1,
    exhaust=True,
    effects=[
        {"action": "damage"},
        {"action": "apply_effect", "effect": "TalkToTheHand", "stacks": 2, "target": "enemy"},
    ],
)

make_card(
    "tantrum", "Tantrum", 1, CardType.ATTACK, CardRarity.UNCOMMON, CardColor.PURPLE,
    target=CardTarget.ENEMY,
    description="Deal 3 damage 3 times. Enter Wrath. Shuffle this card into your draw pile.",
    base_damage=3, upgrade_damage=0,
    effects=[
        {"action": "damage", "times": 3},
        {"action": "enter_stance", "stance": "Wrath"},
        {"action": "custom", "func": "tantrum_shuffle_back"},
    ],
    upgrade_description="Deal 3 damage 4 times. Enter Wrath. Shuffle this card into your draw pile.",
)

make_card(
    "wallop", "Wallop", 2, CardType.ATTACK, CardRarity.UNCOMMON, CardColor.PURPLE,
    target=CardTarget.ENEMY,
    description="Deal 9 damage. Gain Block equal to unblocked damage dealt.",
    base_damage=9, upgrade_damage=3,
    effects=[
        {"action": "custom", "func": "wallop_damage_and_block"},
    ],
)

make_card(
    "weave", "Weave", 0, CardType.ATTACK, CardRarity.UNCOMMON, CardColor.PURPLE,
    target=CardTarget.ENEMY,
    description="Deal 4 damage. Whenever you Scry, return this from the discard pile to your hand.",
    base_damage=4, upgrade_damage=2,
    effects=[
        {"action": "damage"},
        {"action": "custom", "func": "weave_on_scry"},
    ],
)

make_card(
    "wheel_kick", "Wheel Kick", 2, CardType.ATTACK, CardRarity.UNCOMMON, CardColor.PURPLE,
    target=CardTarget.ENEMY,
    description="Deal 15 damage. Draw 2 cards.",
    base_damage=15, upgrade_damage=5,
    effects=[
        {"action": "damage"},
        {"action": "draw", "amount": 2},
    ],
)

make_card(
    "windmill_strike", "Windmill Strike", 2, CardType.ATTACK, CardRarity.UNCOMMON, CardColor.PURPLE,
    target=CardTarget.ENEMY,
    description="Deal 7 damage. Retain. Each time this is Retained, increase its damage by 4.",
    base_damage=7, upgrade_damage=3,
    base_magic=4, upgrade_magic=1,
    retain=True,
    effects=[
        {"action": "damage"},
        {"action": "custom", "func": "windmill_strike_retain_buff"},
    ],
)

# =============================================================================
#  UNCOMMON SKILLS
# =============================================================================

make_card(
    "collect", "Collect", -1, CardType.SKILL, CardRarity.UNCOMMON, CardColor.PURPLE,
    target=CardTarget.SELF,
    description="Put a Miracle+ into your hand at the start of your next X turns.",
    effects=[
        {"action": "custom", "func": "collect_x_miracles"},
    ],
)

make_card(
    "deceive_reality", "Deceive Reality", 1, CardType.SKILL, CardRarity.UNCOMMON, CardColor.PURPLE,
    target=CardTarget.SELF,
    description="Gain 4 Block. Add a Safety to your hand.",
    base_block=4, upgrade_block=3,
    effects=[
        {"action": "block"},
        {"action": "add_card", "card_id": "safety", "to": "hand", "count": 1},
    ],
)

make_card(
    "fasting", "Fasting", 2, CardType.POWER, CardRarity.UNCOMMON, CardColor.PURPLE,
    target=CardTarget.SELF,
    description="Gain 3 Strength. Gain 3 Dexterity. Gain 1 less Energy each turn.",
    base_magic=3, upgrade_magic=1,
    effects=[
        {"action": "apply_effect", "effect": "Strength", "stacks": 3, "target": "self"},
        {"action": "apply_effect", "effect": "Dexterity", "stacks": 3, "target": "self"},
        {"action": "apply_effect", "effect": "Fasting", "stacks": 1, "target": "self"},
    ],
)

make_card(
    "foreign_influence", "Foreign Influence", 0, CardType.SKILL, CardRarity.UNCOMMON, CardColor.PURPLE,
    target=CardTarget.SELF,
    description="Choose 1 of 3 Attack cards from any color to add to your hand. Exhaust.",
    exhaust=True,
    effects=[
        {"action": "custom", "func": "foreign_influence"},
    ],
    upgrade_description="Choose 1 of 3 Attack cards from any color to add to your hand. It costs 0 this turn. Exhaust.",
)

make_card(
    "meditate", "Meditate", 1, CardType.SKILL, CardRarity.UNCOMMON, CardColor.PURPLE,
    target=CardTarget.SELF,
    description="Put up to 1 card from your discard pile into your hand. Retain it. Enter Calm. End your turn.",
    base_magic=1, upgrade_magic=1,
    effects=[
        {"action": "custom", "func": "meditate_retrieve"},
        {"action": "enter_stance", "stance": "Calm"},
        {"action": "custom", "func": "meditate_end_turn"},
    ],
)

make_card(
    "sanctity", "Sanctity", 1, CardType.SKILL, CardRarity.UNCOMMON, CardColor.PURPLE,
    target=CardTarget.SELF,
    description="Gain 6 Block. If you have any Mantra, draw 2 cards.",
    base_block=6, upgrade_block=3,
    effects=[
        {"action": "block"},
        {"action": "custom", "func": "sanctity_draw_if_mantra"},
    ],
)

make_card(
    "swivel", "Swivel", 2, CardType.SKILL, CardRarity.UNCOMMON, CardColor.PURPLE,
    target=CardTarget.SELF,
    description="Gain 8 Block. The next Attack you play costs 0.",
    base_block=8, upgrade_block=3,
    effects=[
        {"action": "block"},
        {"action": "apply_effect", "effect": "FreeAttackPower", "stacks": 1, "target": "self"},
    ],
)

make_card(
    "wave_of_the_hand", "Wave of the Hand", 1, CardType.POWER, CardRarity.UNCOMMON, CardColor.PURPLE,
    target=CardTarget.SELF,
    description="Whenever you gain Block this turn, apply 1 Weak to ALL enemies.",
    base_magic=1, upgrade_magic=1,
    effects=[
        {"action": "apply_effect", "effect": "WaveOfTheHand", "stacks": 1, "target": "self"},
    ],
)

make_card(
    "wish", "Wish", 3, CardType.SKILL, CardRarity.UNCOMMON, CardColor.PURPLE,
    target=CardTarget.SELF,
    description="Choose one: gain 6 Plated Armor, deal 24 damage to ALL enemies, or gain 3 Strength.",
    exhaust=True,
    effects=[
        {"action": "custom", "func": "wish_choose"},
    ],
    upgrade_description="Choose one: gain 8 Plated Armor, deal 32 damage to ALL enemies, or gain 4 Strength.",
)

make_card(
    "wreath_of_flame", "Wreath of Flame", 1, CardType.SKILL, CardRarity.UNCOMMON, CardColor.PURPLE,
    target=CardTarget.SELF,
    description="Your next Attack deals 5 additional damage.",
    base_magic=5, upgrade_magic=3,
    effects=[
        {"action": "apply_effect", "effect": "WreathOfFlame", "stacks": 5, "target": "self"},
    ],
)

# =============================================================================
#  UNCOMMON POWERS
# =============================================================================

make_card(
    "battle_hymn", "Battle Hymn", 1, CardType.POWER, CardRarity.UNCOMMON, CardColor.PURPLE,
    target=CardTarget.SELF,
    description="At the start of each turn, add a Smite to your hand.",
    effects=[
        {"action": "apply_effect", "effect": "BattleHymn", "stacks": 1, "target": "self"},
    ],
    upgrade_cost=0,
    upgrade_description="At the start of each turn, add a Smite to your hand.",
)

make_card(
    "devotion", "Devotion", 1, CardType.POWER, CardRarity.UNCOMMON, CardColor.PURPLE,
    target=CardTarget.SELF,
    description="At the start of your turn, gain 2 Mantra.",
    base_magic=2, upgrade_magic=1,
    effects=[
        {"action": "apply_effect", "effect": "Devotion", "stacks": 2, "target": "self"},
    ],
)

make_card(
    "establishment", "Establishment", 1, CardType.POWER, CardRarity.UNCOMMON, CardColor.PURPLE,
    target=CardTarget.SELF,
    description="Whenever a card is Retained, reduce its cost by 1.",
    base_magic=1, upgrade_magic=0,
    effects=[
        {"action": "apply_effect", "effect": "Establishment", "stacks": 1, "target": "self"},
    ],
    upgrade_cost=0,
    upgrade_description="Whenever a card is Retained, reduce its cost by 1.",
)

make_card(
    "foresight", "Foresight", 1, CardType.POWER, CardRarity.UNCOMMON, CardColor.PURPLE,
    target=CardTarget.SELF,
    description="At the start of your turn, Scry 3.",
    base_magic=3, upgrade_magic=1,
    effects=[
        {"action": "apply_effect", "effect": "Foresight", "stacks": 3, "target": "self"},
    ],
)

make_card(
    "like_water", "Like Water", 1, CardType.POWER, CardRarity.UNCOMMON, CardColor.PURPLE,
    target=CardTarget.SELF,
    description="At the end of your turn, if you are in Calm, gain 5 Block.",
    base_magic=5, upgrade_magic=2,
    effects=[
        {"action": "apply_effect", "effect": "LikeWater", "stacks": 5, "target": "self"},
    ],
)

make_card(
    "mental_fortress", "Mental Fortress", 1, CardType.POWER, CardRarity.UNCOMMON, CardColor.PURPLE,
    target=CardTarget.SELF,
    description="Whenever you change Stances, gain 4 Block.",
    base_magic=4, upgrade_magic=2,
    effects=[
        {"action": "apply_effect", "effect": "MentalFortress", "stacks": 4, "target": "self"},
    ],
)

make_card(
    "nirvana", "Nirvana", 1, CardType.POWER, CardRarity.UNCOMMON, CardColor.PURPLE,
    target=CardTarget.SELF,
    description="Whenever you Scry, gain 3 Block.",
    base_magic=3, upgrade_magic=1,
    effects=[
        {"action": "apply_effect", "effect": "Nirvana", "stacks": 3, "target": "self"},
    ],
)

make_card(
    "study", "Study", 2, CardType.POWER, CardRarity.UNCOMMON, CardColor.PURPLE,
    target=CardTarget.SELF,
    description="At the end of your turn, shuffle an Insight into your draw pile.",
    effects=[
        {"action": "apply_effect", "effect": "Study", "stacks": 1, "target": "self"},
    ],
    upgrade_cost=1,
    upgrade_description="At the end of your turn, shuffle an Insight into your draw pile.",
)

make_card(
    "worship", "Worship", 2, CardType.SKILL, CardRarity.UNCOMMON, CardColor.PURPLE,
    target=CardTarget.SELF,
    description="Gain 5 Mantra. Retain.",
    base_magic=5, upgrade_magic=2,
    retain=True,
    effects=[
        {"action": "apply_effect", "effect": "Mantra", "stacks": 5, "target": "self"},
    ],
)

# =============================================================================
#  RARE ATTACKS
# =============================================================================

make_card(
    "brilliance", "Brilliance", 1, CardType.ATTACK, CardRarity.RARE, CardColor.PURPLE,
    target=CardTarget.ENEMY,
    description="Deal 12 damage. Deals additional damage equal to Mantra gained this combat.",
    base_damage=12, upgrade_damage=4,
    effects=[
        {"action": "custom", "func": "brilliance_damage"},
    ],
)

make_card(
    "lesson_learned", "Lesson Learned", 2, CardType.ATTACK, CardRarity.RARE, CardColor.PURPLE,
    target=CardTarget.ENEMY,
    description="Deal 13 damage. If this kills the enemy, Upgrade a random card in your deck. Exhaust.",
    base_damage=13, upgrade_damage=4,
    exhaust=True,
    effects=[
        {"action": "custom", "func": "lesson_learned_kill_upgrade"},
    ],
)

make_card(
    "ragnarok", "Ragnarok", 3, CardType.ATTACK, CardRarity.RARE, CardColor.PURPLE,
    target=CardTarget.ALL_ENEMIES,
    description="Deal 5 damage to a random enemy 5 times.",
    base_damage=5, upgrade_damage=1,
    effects=[
        {"action": "custom", "func": "ragnarok_random_hits"},
    ],
    upgrade_description="Deal 6 damage to a random enemy 5 times.",
)

make_card(
    "through_violence", "Through Violence", 0, CardType.ATTACK, CardRarity.RARE, CardColor.PURPLE,
    target=CardTarget.ENEMY,
    description="Retain. Deal 20 damage.",
    base_damage=20, upgrade_damage=10,
    retain=True,
    effects=[
        {"action": "damage"},
    ],
)

# =============================================================================
#  RARE SKILLS
# =============================================================================

make_card(
    "alpha", "Alpha", 1, CardType.SKILL, CardRarity.RARE, CardColor.PURPLE,
    target=CardTarget.SELF,
    description="Shuffle a Beta into your draw pile. Exhaust.",
    exhaust=True,
    effects=[
        {"action": "add_card", "card_id": "beta", "to": "draw_pile", "count": 1},
    ],
    upgrade_cost=0,
    upgrade_description="Shuffle a Beta into your draw pile. Exhaust.",
)

make_card(
    "blasphemy", "Blasphemy", 1, CardType.SKILL, CardRarity.RARE, CardColor.PURPLE,
    target=CardTarget.SELF,
    description="Enter Divinity. Die next turn. Exhaust.",
    exhaust=True,
    effects=[
        {"action": "enter_stance", "stance": "Divinity"},
        {"action": "apply_effect", "effect": "Blasphemer", "stacks": 1, "target": "self"},
    ],
)

make_card(
    "conjure_blade", "Conjure Blade", -1, CardType.SKILL, CardRarity.RARE, CardColor.PURPLE,
    target=CardTarget.SELF,
    description="Shuffle an Expunger with X damage into your draw pile.",
    effects=[
        {"action": "custom", "func": "conjure_blade_x"},
    ],
)

make_card(
    "deus_ex_machina", "Deus Ex Machina", -2, CardType.SKILL, CardRarity.RARE, CardColor.PURPLE,
    target=CardTarget.NONE,
    description="Unplayable. When this card is drawn, add 2 Miracles to your hand. Exhaust.",
    unplayable=True,
    exhaust=True,
    base_magic=2, upgrade_magic=1,
    effects=[
        {"action": "custom", "func": "deus_ex_machina_on_draw"},
    ],
)

make_card(
    "judgement", "Judgement", 1, CardType.SKILL, CardRarity.RARE, CardColor.PURPLE,
    target=CardTarget.ENEMY,
    description="If the enemy has 30 or less HP, set their HP to 0.",
    base_magic=30, upgrade_magic=10,
    effects=[
        {"action": "custom", "func": "judgement_kill"},
    ],
)

make_card(
    "omniscience", "Omniscience", 4, CardType.SKILL, CardRarity.RARE, CardColor.PURPLE,
    target=CardTarget.SELF,
    description="Choose a card in your draw pile. Play it twice and Exhaust it. Exhaust.",
    exhaust=True,
    effects=[
        {"action": "custom", "func": "omniscience_play_twice"},
    ],
    upgrade_cost=3,
    upgrade_description="Choose a card in your draw pile. Play it twice and Exhaust it. Exhaust.",
)

make_card(
    "scrawl", "Scrawl", 1, CardType.SKILL, CardRarity.RARE, CardColor.PURPLE,
    target=CardTarget.SELF,
    description="Draw cards until you have 10 cards in your hand.",
    base_magic=10, upgrade_magic=0,
    effects=[
        {"action": "custom", "func": "scrawl_draw"},
    ],
    upgrade_cost=0,
    upgrade_description="Draw cards until you have 10 cards in your hand.",
)

make_card(
    "spirit_shield", "Spirit Shield", 2, CardType.SKILL, CardRarity.RARE, CardColor.PURPLE,
    target=CardTarget.SELF,
    description="Gain 3 Block for each card in your hand.",
    base_magic=3, upgrade_magic=1,
    effects=[
        {"action": "custom", "func": "spirit_shield_block"},
    ],
)

make_card(
    "vault", "Vault", 3, CardType.SKILL, CardRarity.RARE, CardColor.PURPLE,
    target=CardTarget.SELF,
    description="Take an extra turn. End your turn. Exhaust.",
    exhaust=True,
    effects=[
        {"action": "custom", "func": "vault_extra_turn"},
    ],
    upgrade_cost=2,
    upgrade_description="Take an extra turn. End your turn. Exhaust.",
)

# =============================================================================
#  RARE POWERS
# =============================================================================

make_card(
    "deva_form", "Deva Form", 3, CardType.POWER, CardRarity.RARE, CardColor.PURPLE,
    target=CardTarget.SELF,
    description="At the start of your turn, gain 1 Energy. This increases by 1 each turn.",
    innate=False,
    effects=[
        {"action": "apply_effect", "effect": "DevaForm", "stacks": 1, "target": "self"},
    ],
    upgrade_description="At the start of your turn, gain 1 Energy. This increases by 1 each turn. Innate.",
)

make_card(
    "master_reality", "Master Reality", 1, CardType.POWER, CardRarity.RARE, CardColor.PURPLE,
    target=CardTarget.SELF,
    description="Whenever a card is created during combat, Upgrade it.",
    effects=[
        {"action": "apply_effect", "effect": "MasterReality", "stacks": 1, "target": "self"},
    ],
    upgrade_cost=0,
    upgrade_description="Whenever a card is created during combat, Upgrade it.",
)

# =============================================================================
#  SPECIAL / GENERATED CARDS
# =============================================================================

make_card(
    "smite", "Smite", 1, CardType.ATTACK, CardRarity.SPECIAL, CardColor.PURPLE,
    target=CardTarget.ENEMY,
    description="Retain. Deal 12 damage. Exhaust.",
    base_damage=12, upgrade_damage=4,
    retain=True,
    exhaust=True,
    effects=[{"action": "damage"}],
)

make_card(
    "safety", "Safety", 1, CardType.SKILL, CardRarity.SPECIAL, CardColor.PURPLE,
    target=CardTarget.SELF,
    description="Retain. Gain 12 Block. Exhaust.",
    base_block=12, upgrade_block=2,
    retain=True,
    exhaust=True,
    effects=[{"action": "block"}],
)

make_card(
    "miracle", "Miracle", 0, CardType.SKILL, CardRarity.SPECIAL, CardColor.PURPLE,
    target=CardTarget.SELF,
    description="Retain. Gain 1 Energy. Exhaust.",
    retain=True,
    exhaust=True,
    effects=[{"action": "energy", "amount": 1}],
)

make_card(
    "insight", "Insight", 0, CardType.SKILL, CardRarity.SPECIAL, CardColor.PURPLE,
    target=CardTarget.SELF,
    description="Retain. Draw 2 cards. Exhaust.",
    retain=True,
    exhaust=True,
    effects=[{"action": "draw", "amount": 2}],
    upgrade_description="Retain. Draw 3 cards. Exhaust.",
)

make_card(
    "beta", "Beta", 2, CardType.SKILL, CardRarity.SPECIAL, CardColor.PURPLE,
    target=CardTarget.SELF,
    description="Shuffle an Omega into your draw pile. Exhaust.",
    exhaust=True,
    effects=[
        {"action": "add_card", "card_id": "omega", "to": "draw_pile", "count": 1},
    ],
    upgrade_cost=1,
    upgrade_description="Shuffle an Omega into your draw pile. Exhaust.",
)

make_card(
    "omega", "Omega", 3, CardType.POWER, CardRarity.SPECIAL, CardColor.PURPLE,
    target=CardTarget.SELF,
    description="At the end of your turn, deal 50 damage to ALL enemies.",
    base_magic=50, upgrade_magic=0,
    effects=[
        {"action": "apply_effect", "effect": "Omega", "stacks": 50, "target": "self"},
    ],
)

make_card(
    "expunger", "Expunger", 1, CardType.ATTACK, CardRarity.SPECIAL, CardColor.PURPLE,
    target=CardTarget.ENEMY,
    description="Deal 9 damage X times.",
    base_damage=9, upgrade_damage=0,
    effects=[
        {"action": "custom", "func": "expunger_x_damage"},
    ],
)
