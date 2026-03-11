"""Curse cards - negative cards added to the deck."""
from slay_the_spire.card import (
    make_card, CardType, CardRarity, CardColor, CardTarget,
)

# =============================================================================
#  CURSES
#
#  All curses use CardColor.CURSE, CardType.CURSE, CardRarity.SPECIAL.
#  Unplayable curses use cost=-2.
# =============================================================================

# Ascender's Bane: Unplayable. Cannot be removed from your deck. Ethereal.
make_card(
    "ascenders_bane", "Ascender's Bane", -2, CardType.CURSE, CardRarity.SPECIAL, CardColor.CURSE,
    target=CardTarget.NONE,
    description="Unplayable. Cannot be removed from your deck. Ethereal.",
    unplayable=True,
    ethereal=True,
    effects=[{"action": "custom", "func": "ascenders_bane_no_remove"}],
)

# Clumsy: Unplayable. Ethereal.
make_card(
    "clumsy", "Clumsy", -2, CardType.CURSE, CardRarity.SPECIAL, CardColor.CURSE,
    target=CardTarget.NONE,
    description="Unplayable. Ethereal.",
    unplayable=True,
    ethereal=True,
    effects=[],
)

# Curse of the Bell: Unplayable. Cannot be removed from your deck.
make_card(
    "curse_of_the_bell", "Curse of the Bell", -2, CardType.CURSE, CardRarity.SPECIAL, CardColor.CURSE,
    target=CardTarget.NONE,
    description="Unplayable. Cannot be removed from your deck.",
    unplayable=True,
    effects=[{"action": "custom", "func": "curse_bell_no_remove"}],
)

# Decay: At the end of your turn, take 1 damage.
make_card(
    "decay", "Decay", -2, CardType.CURSE, CardRarity.SPECIAL, CardColor.CURSE,
    target=CardTarget.NONE,
    description="Unplayable. At the end of your turn, take 1 damage.",
    unplayable=True,
    effects=[{"action": "custom", "func": "decay_end_turn"}],
)

# Doubt: At the end of your turn, gain 1 Weak.
make_card(
    "doubt", "Doubt", -2, CardType.CURSE, CardRarity.SPECIAL, CardColor.CURSE,
    target=CardTarget.NONE,
    description="Unplayable. At the end of your turn, gain 1 Weak.",
    unplayable=True,
    effects=[{"action": "custom", "func": "doubt_end_turn"}],
)

# Injury: Unplayable.
make_card(
    "injury", "Injury", -2, CardType.CURSE, CardRarity.SPECIAL, CardColor.CURSE,
    target=CardTarget.NONE,
    description="Unplayable.",
    unplayable=True,
    effects=[],
)

# Normality: You cannot play more than 3 cards this turn.
make_card(
    "normality", "Normality", -2, CardType.CURSE, CardRarity.SPECIAL, CardColor.CURSE,
    target=CardTarget.NONE,
    description="Unplayable. You cannot play more than 3 cards this turn.",
    unplayable=True,
    effects=[{"action": "custom", "func": "normality_limit"}],
)

# Pain: Whenever this card is drawn, lose 1 HP.
make_card(
    "pain", "Pain", -2, CardType.CURSE, CardRarity.SPECIAL, CardColor.CURSE,
    target=CardTarget.NONE,
    description="Unplayable. Whenever this card is drawn, lose 1 HP.",
    unplayable=True,
    effects=[{"action": "custom", "func": "pain_on_draw"}],
)

# Parasite: If removed from your deck, lose 3 Max HP.
make_card(
    "parasite", "Parasite", -2, CardType.CURSE, CardRarity.SPECIAL, CardColor.CURSE,
    target=CardTarget.NONE,
    description="Unplayable. If removed from your deck, lose 3 Max HP.",
    unplayable=True,
    effects=[{"action": "custom", "func": "parasite_on_remove"}],
)

# Regret: At the end of your turn, lose HP equal to the number of cards in your hand.
make_card(
    "regret", "Regret", -2, CardType.CURSE, CardRarity.SPECIAL, CardColor.CURSE,
    target=CardTarget.NONE,
    description="Unplayable. At the end of your turn, lose HP equal to the number of cards in your hand.",
    unplayable=True,
    effects=[{"action": "custom", "func": "regret_end_turn"}],
)

# Shame: At the end of your turn, gain 1 Frail.
make_card(
    "shame", "Shame", -2, CardType.CURSE, CardRarity.SPECIAL, CardColor.CURSE,
    target=CardTarget.NONE,
    description="Unplayable. At the end of your turn, gain 1 Frail.",
    unplayable=True,
    effects=[{"action": "custom", "func": "shame_end_turn"}],
)

# Writhe: Unplayable. Innate.
make_card(
    "writhe", "Writhe", -2, CardType.CURSE, CardRarity.SPECIAL, CardColor.CURSE,
    target=CardTarget.NONE,
    description="Unplayable. Innate.",
    unplayable=True,
    innate=True,
    effects=[],
)
