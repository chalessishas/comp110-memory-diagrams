"""Status cards - negative cards generated during combat."""
from slay_the_spire.card import (
    make_card, CardType, CardRarity, CardColor, CardTarget,
)

# =============================================================================
#  STATUS CARDS
#
#  All status cards use CardColor.COLORLESS, CardType.STATUS, CardRarity.SPECIAL.
#  Unplayable statuses use cost=-2.
# =============================================================================

# Burn: Unplayable. At the end of your turn, take 2 damage.
make_card(
    "burn", "Burn", -2, CardType.STATUS, CardRarity.SPECIAL, CardColor.COLORLESS,
    target=CardTarget.NONE,
    description="Unplayable. At the end of your turn, take 2 damage.",
    unplayable=True,
    effects=[{"action": "custom", "func": "burn_end_turn"}],
)

# Dazed: Unplayable. Ethereal.
make_card(
    "dazed", "Dazed", -2, CardType.STATUS, CardRarity.SPECIAL, CardColor.COLORLESS,
    target=CardTarget.NONE,
    description="Unplayable. Ethereal.",
    unplayable=True,
    ethereal=True,
    effects=[],
)

# Slimed: Exhaust.
make_card(
    "slimed", "Slimed", 1, CardType.STATUS, CardRarity.SPECIAL, CardColor.COLORLESS,
    target=CardTarget.SELF,
    description="Exhaust.",
    exhaust=True,
    effects=[{"action": "custom", "func": "slimed_play", "playable": True}],
)

# Void: Unplayable. Ethereal. When this card is drawn, lose 1 Energy.
make_card(
    "void", "Void", -2, CardType.STATUS, CardRarity.SPECIAL, CardColor.COLORLESS,
    target=CardTarget.NONE,
    description="Unplayable. Ethereal. When this card is drawn, lose 1 Energy.",
    unplayable=True,
    ethereal=True,
    effects=[{"action": "custom", "func": "void_on_draw"}],
)

# Wound: Unplayable.
make_card(
    "wound", "Wound", -2, CardType.STATUS, CardRarity.SPECIAL, CardColor.COLORLESS,
    target=CardTarget.NONE,
    description="Unplayable.",
    unplayable=True,
    effects=[],
)
