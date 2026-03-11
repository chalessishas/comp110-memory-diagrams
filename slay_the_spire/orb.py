"""Orb system for the Defect character."""
import random
from enum import Enum, auto


class OrbType(Enum):
    LIGHTNING = auto()
    FROST = auto()
    DARK = auto()
    PLASMA = auto()


class Orb:
    """Represents a channeled orb."""

    def __init__(self, orb_type):
        self.orb_type = orb_type
        self.name = orb_type.name.capitalize()
        # Dark orbs accumulate damage
        self.dark_damage = 6 if orb_type == OrbType.DARK else 0

    def passive(self, focus):
        """Return passive effect value. Focus modifies passive."""
        base_focus = max(0, focus)
        if self.orb_type == OrbType.LIGHTNING:
            return 3 + base_focus  # deal damage to random enemy
        elif self.orb_type == OrbType.FROST:
            return 2 + base_focus  # gain block
        elif self.orb_type == OrbType.DARK:
            self.dark_damage += 6 + base_focus  # accumulate damage
            return 0  # no passive effect, just accumulates
        elif self.orb_type == OrbType.PLASMA:
            return 1  # gain 1 energy (not affected by focus)
        return 0

    def evoke(self, focus):
        """Return evoke effect value."""
        if self.orb_type == OrbType.LIGHTNING:
            return 8 + max(0, focus)  # deal damage to random enemy
        elif self.orb_type == OrbType.FROST:
            return 5 + max(0, focus)  # gain block
        elif self.orb_type == OrbType.DARK:
            return self.dark_damage  # deal accumulated damage to lowest HP enemy
        elif self.orb_type == OrbType.PLASMA:
            return 2  # gain 2 energy
        return 0

    def __repr__(self):
        if self.orb_type == OrbType.DARK:
            return f"Dark({self.dark_damage})"
        return self.name


class OrbManager:
    """Manages the Defect's orb slots."""

    def __init__(self, max_orbs=3):
        self.orbs = []
        self.max_orbs = max_orbs

    def channel(self, orb_type):
        """Channel a new orb. If full, evoke the oldest orb first.
        Returns (evoked_orb, new_orb) or (None, new_orb)."""
        new_orb = Orb(orb_type)
        evoked = None
        if len(self.orbs) >= self.max_orbs:
            if self.max_orbs > 0:
                evoked = self.orbs.pop(0)
        if self.max_orbs > 0:
            self.orbs.append(new_orb)
        return evoked, new_orb

    def evoke_first(self):
        """Evoke (remove) the first orb. Returns the evoked orb or None."""
        if self.orbs:
            return self.orbs.pop(0)
        return None

    def evoke_all(self):
        """Evoke all orbs. Returns list of evoked orbs."""
        evoked = list(self.orbs)
        self.orbs.clear()
        return evoked

    def trigger_passives(self, focus):
        """Trigger all orb passives at end of turn. Returns list of (orb, value)."""
        results = []
        for orb in self.orbs:
            val = orb.passive(focus)
            results.append((orb, val))
        return results

    def increase_max(self, amount=1):
        self.max_orbs += amount

    def clear(self):
        self.orbs.clear()

    def __repr__(self):
        if not self.orbs:
            return "No orbs"
        return " | ".join(str(o) for o in self.orbs) + f" [{len(self.orbs)}/{self.max_orbs}]"
