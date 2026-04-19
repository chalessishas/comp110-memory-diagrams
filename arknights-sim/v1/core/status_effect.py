from __future__ import annotations
from dataclasses import dataclass


@dataclass
class StatusEffect:
    kind: str          # "stun" | "slow"
    duration: float    # remaining seconds
    slow_factor: float = 1.0  # attack-interval multiplier when kind=="slow" (>1 = slower)

    @property
    def expired(self) -> bool:
        return self.duration <= 1e-9

    def tick(self, dt: float) -> None:
        self.duration = max(0.0, self.duration - dt)
