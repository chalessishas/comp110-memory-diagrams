from __future__ import annotations
from dataclasses import dataclass
from .entity import Entity


@dataclass
class Enemy(Entity):
    """An enemy unit that attacks the operator blocking it."""
    attack_type: str = "physical"  # "physical" | "magic"

    def attack(self, target: Entity) -> int:
        if self.attack_type == "physical":
            return target.take_physical(self.atk)
        elif self.attack_type == "magic":
            return target.take_magic(self.atk)
        raise ValueError(f"Unknown attack_type: {self.attack_type}")
