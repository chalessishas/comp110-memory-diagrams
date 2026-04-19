from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
from .status_effect import StatusEffect


@dataclass
class Entity:
    name: str
    max_hp: int
    atk: int
    defence: int   # "def" is a keyword
    res: float     # magic resistance 0–100
    atk_interval: float  # seconds between attacks
    block: int = 0

    hp: int = field(init=False)
    _atk_cd: float = field(init=False, default=0.0)
    alive: bool = field(init=False, default=True)
    status_effects: List[StatusEffect] = field(init=False, default_factory=list)

    def __post_init__(self) -> None:
        self.hp = self.max_hp

    # ------------------------------------------------------------------
    # Status effects
    # ------------------------------------------------------------------

    def apply_status(self, effect: StatusEffect) -> None:
        self.status_effects.append(effect)

    def tick_status(self, dt: float) -> None:
        for se in self.status_effects:
            se.tick(dt)
        self.status_effects = [se for se in self.status_effects if not se.expired]

    @property
    def is_stunned(self) -> bool:
        return any(se.kind == "stun" for se in self.status_effects)

    @property
    def slow_factor(self) -> float:
        """Return the largest attack-interval multiplier from active slow effects."""
        factors = [se.slow_factor for se in self.status_effects if se.kind == "slow"]
        return max(factors) if factors else 1.0

    # ------------------------------------------------------------------
    # Damage / heal
    # ------------------------------------------------------------------

    def take_damage(self, damage: int) -> int:
        actual = max(1, damage)
        self.hp = max(0, self.hp - actual)
        if self.hp == 0:
            self.alive = False
        return actual

    def take_physical(self, raw_atk: int) -> int:
        dmg = max(int(raw_atk * 0.05), raw_atk - self.defence)
        return self.take_damage(dmg)

    def take_magic(self, raw_atk: int) -> int:
        dmg = max(1, int(raw_atk * (1 - self.res / 100)))
        return self.take_damage(dmg)

    def heal(self, amount: int) -> int:
        healed = min(amount, self.max_hp - self.hp)
        self.hp += healed
        return healed

    def tick(self, dt: float) -> bool:
        """Advance cooldown. Returns True when an attack fires. Respects stun/slow."""
        if not self.alive or self.is_stunned:
            return False
        effective_dt = dt / self.slow_factor  # slow_factor > 1 means slower drain
        self._atk_cd -= effective_dt
        if self._atk_cd <= 0:
            self._atk_cd += self.atk_interval
            return True
        return False
