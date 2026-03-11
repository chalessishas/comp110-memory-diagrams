"""Stance system for the Watcher character."""
from enum import Enum, auto


class StanceType(Enum):
    NONE = auto()
    WRATH = auto()
    CALM = auto()
    DIVINITY = auto()


class StanceManager:
    """Manages the Watcher's stance."""

    def __init__(self):
        self.current = StanceType.NONE

    def enter(self, stance_type):
        """Enter a stance. Returns (old_stance, new_stance) for trigger processing.
        If already in this stance, no change."""
        if self.current == stance_type:
            return None, None
        old = self.current
        self.current = stance_type
        return old, stance_type

    def exit_current(self):
        """Exit current stance (go to NONE). Returns old stance."""
        old = self.current
        self.current = StanceType.NONE
        return old

    def get_damage_multiplier(self):
        """Get outgoing damage multiplier from current stance."""
        if self.current == StanceType.WRATH:
            return 2.0
        elif self.current == StanceType.DIVINITY:
            return 3.0
        return 1.0

    def get_damage_taken_multiplier(self):
        """Get incoming damage multiplier from current stance."""
        if self.current == StanceType.WRATH:
            return 2.0
        return 1.0

    def get_exit_energy(self):
        """Get energy gained from exiting current stance."""
        if self.current == StanceType.CALM:
            return 2
        return 0

    def is_in(self, stance_type):
        return self.current == stance_type

    def clear(self):
        self.current = StanceType.NONE

    def __repr__(self):
        if self.current == StanceType.NONE:
            return "No Stance"
        return self.current.name.capitalize()
