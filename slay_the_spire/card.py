"""Card system for Slay the Spire."""
import copy
from enum import Enum, auto


class CardType(Enum):
    ATTACK = auto()
    SKILL = auto()
    POWER = auto()
    STATUS = auto()
    CURSE = auto()


class CardRarity(Enum):
    BASIC = auto()
    COMMON = auto()
    UNCOMMON = auto()
    RARE = auto()
    SPECIAL = auto()  # for generated cards like Shiv


class CardTarget(Enum):
    ENEMY = auto()       # single enemy target
    ALL_ENEMIES = auto() # hits all enemies
    SELF = auto()        # targets player only
    NONE = auto()        # no target needed


class CardColor(Enum):
    RED = auto()      # Ironclad
    GREEN = auto()    # Silent
    BLUE = auto()     # Defect
    PURPLE = auto()   # Watcher
    COLORLESS = auto()
    CURSE = auto()


class Card:
    """Represents a single card."""

    def __init__(self, card_id, name, cost, card_type, rarity, color,
                 target=CardTarget.ENEMY, description="",
                 upgraded=False, exhaust=False, ethereal=False,
                 innate=False, retain=False, unplayable=False,
                 base_damage=0, base_block=0, base_magic=0,
                 upgrade_damage=0, upgrade_block=0, upgrade_magic=0,
                 upgrade_cost=None, upgrade_description=None,
                 keywords=None, effects=None):
        self.card_id = card_id
        self.name = name
        self.cost = cost
        self.card_type = card_type
        self.rarity = rarity
        self.color = color
        self.target = target
        self.description = description
        self.upgraded = upgraded
        self.exhaust = exhaust
        self.ethereal = ethereal
        self.innate = innate
        self.retain = retain
        self.unplayable = unplayable

        # Base values
        self.base_damage = base_damage
        self.base_block = base_block
        self.base_magic = base_magic  # misc value (poison stacks, draw count, etc.)

        # Upgrade deltas
        self.upgrade_damage = upgrade_damage
        self.upgrade_block = upgrade_block
        self.upgrade_magic = upgrade_magic
        self.upgrade_cost = upgrade_cost  # None means no cost change
        self.upgrade_description = upgrade_description

        self.keywords = keywords or []
        self.effects = effects or []  # list of effect dicts for custom logic

        # Current values (modified by upgrades)
        self.damage = base_damage
        self.block = base_block
        self.magic = base_magic

        # Track cost modifications in combat
        self.cost_for_turn = cost
        self.base_cost = cost

    def upgrade(self):
        """Upgrade this card."""
        if self.upgraded:
            return
        self.upgraded = True
        self.name = self.name + "+"
        self.damage = self.base_damage + self.upgrade_damage
        self.block = self.base_block + self.upgrade_block
        self.magic = self.base_magic + self.upgrade_magic
        if self.upgrade_cost is not None:
            self.cost = self.upgrade_cost
            self.base_cost = self.upgrade_cost
            self.cost_for_turn = self.upgrade_cost
        if self.upgrade_description:
            self.description = self.upgrade_description
        # Apply any keyword changes from upgrade
        for eff in self.effects:
            if eff.get("on_upgrade"):
                eff["on_upgrade"](self)

    def can_play(self, player, combat):
        """Check if this card can be played."""
        if self.unplayable:
            return False
        if self.card_type == CardType.STATUS or self.card_type == CardType.CURSE:
            if not any(e.get("playable") for e in self.effects):
                return False
        effective_cost = self.get_effective_cost(player)
        if effective_cost < 0:  # X cost cards
            return player.energy >= 0
        return player.energy >= effective_cost

    def get_effective_cost(self, player=None):
        """Get the current effective cost of the card."""
        if self.cost == -1:  # X cost
            return -1
        cost = self.cost_for_turn
        # Check for Corruption (skills cost 0)
        if player and self.card_type == CardType.SKILL:
            if player.effects.has("Corruption"):
                return 0
        return max(0, cost)

    def reset_cost(self):
        """Reset cost for new turn."""
        self.cost_for_turn = self.cost if self.cost >= 0 else self.cost

    def copy(self):
        """Create a copy of this card."""
        return copy.deepcopy(self)

    def get_display_cost(self):
        if self.cost == -1:
            return "X"
        elif self.cost == -2:
            return ""  # unplayable
        return str(self.cost_for_turn)

    def short_desc(self):
        """Short display string."""
        cost_str = self.get_display_cost()
        type_str = self.card_type.name[0]  # A/S/P/C
        ug_str = "+" if self.upgraded else ""
        parts = []
        if self.damage > 0:
            parts.append(f"DMG:{self.damage}")
        if self.block > 0:
            parts.append(f"BLK:{self.block}")
        if self.exhaust:
            parts.append("Exhaust")
        if self.ethereal:
            parts.append("Ethereal")
        extra = f" ({', '.join(parts)})" if parts else ""
        return f"[{cost_str}] {self.name}{extra}"

    def __repr__(self):
        return self.short_desc()


# === Card Registry ===
_card_registry = {}


def register_card(card_id, card_factory):
    """Register a card factory function."""
    _card_registry[card_id] = card_factory


def create_card(card_id):
    """Create a new instance of a card by ID."""
    if card_id not in _card_registry:
        raise ValueError(f"Unknown card: {card_id}")
    return _card_registry[card_id]()


def get_all_card_ids():
    return list(_card_registry.keys())


def get_cards_by_color(color):
    """Get all card IDs of a specific color."""
    result = []
    for cid, factory in _card_registry.items():
        c = factory()
        if c.color == color:
            result.append(cid)
    return result


def get_cards_by_rarity(color, rarity):
    """Get card IDs by color and rarity."""
    result = []
    for cid, factory in _card_registry.items():
        c = factory()
        if c.color == color and c.rarity == rarity:
            result.append(cid)
    return result


# === Helper to quickly define cards ===
def make_card(card_id, name, cost, card_type, rarity, color, **kwargs):
    """Helper: register and return a factory for a card."""
    def factory():
        return Card(card_id, name, cost, card_type, rarity, color, **kwargs)
    register_card(card_id, factory)
    return factory
