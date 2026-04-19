from __future__ import annotations
from dataclasses import dataclass
from .entity import Entity


@dataclass
class Operator(Entity):
    """A deployed operator. Attacks the first enemy it is blocking."""
    attack_type: str = "physical"  # "physical" | "magic" | "heal"

    def attack(self, target: Entity) -> int:
        if self.attack_type == "physical":
            return target.take_physical(self.atk)
        elif self.attack_type == "magic":
            return target.take_magic(self.atk)
        elif self.attack_type == "heal":
            return target.heal(self.atk)
        raise ValueError(f"Unknown attack_type: {self.attack_type}")
