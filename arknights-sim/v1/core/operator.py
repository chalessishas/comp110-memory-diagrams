from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
from .entity import Entity
from .skill import Skill


@dataclass
class Operator(Entity):
    """A deployed operator. Attacks the first enemy it is blocking."""
    attack_type: str = "physical"   # "physical" | "magic" | "heal"
    attack_range: str = "melee"     # "melee" | "ranged"
    splash_radius: float = 0.0      # Euclidean tile radius; 0 = no AOE
    has_true_sight: bool = False    # True = can target invisible enemies
    cost: int = 0                   # DP cost to deploy

    skill: Optional[Skill] = None
    sp: float = 0.0
    sp_gain_rate: float = 1.0        # SP per second for auto_time
    sp_gain_per_attack: float = 1.0  # SP per hit for auto_attack

    _skill_remaining: float = field(init=False, default=0.0)
    # Two-stage buff pipeline: ratio buffs sum additively; multiplier buffs multiply
    _atk_ratio_buffs: List[float] = field(init=False, default_factory=list)
    _atk_multiplier_buffs: List[float] = field(init=False, default_factory=list)
    _sp_locked: bool = field(init=False, default=False)   # True = SP full, no target (orange meter)
    _skill_just_fired: bool = field(init=False, default=False)
    _skill_just_ended: bool = field(init=False, default=False)

    def effective_atk(self) -> int:
        intermediate = self.atk * (1.0 + sum(self._atk_ratio_buffs))
        mult = 1.0
        for m in self._atk_multiplier_buffs:
            mult *= m
        return int(intermediate * mult)

    def attack(self, target: Entity) -> int:
        raw = self.effective_atk()
        if self.attack_type == "physical":
            dmg = target.take_physical(raw)
        elif self.attack_type == "magic":
            dmg = target.take_magic(raw)
        elif self.attack_type == "heal":
            dmg = target.heal(raw)
        else:
            raise ValueError(f"Unknown attack_type: {self.attack_type}")

        if self.skill and self._skill_remaining <= 0 and self.skill.sp_gain_mode == "auto_attack":
            self.sp = min(self.sp + self.sp_gain_per_attack, self.skill.sp_cost)
        return dmg

    def update_skill(self, dt: float, has_target: bool = True) -> None:
        self._skill_just_fired = False
        self._skill_just_ended = False
        if not self.skill or not self.alive:
            return

        # 1e-9 absorbs float accumulation error from repeated DT subtraction
        if self._skill_remaining > 1e-9:
            self._skill_remaining -= dt
            if self._skill_remaining <= 1e-9:
                self._skill_remaining = 0.0
                if self.skill.on_end:
                    self.skill.on_end(self)
                self._skill_just_ended = True
            return

        if self.skill.sp_gain_mode == "auto_time":
            self.sp = min(self.sp + self.sp_gain_rate * dt, self.skill.sp_cost)

        if self.sp >= self.skill.sp_cost:
            if not has_target:
                self._sp_locked = True   # orange meter: SP full, no target, hold fire
                return
            self._sp_locked = False
            self.sp = 0.0
            self._skill_remaining = self.skill.duration
            if self.skill.on_start:
                self.skill.on_start(self)
            self._skill_just_fired = True

    @property
    def skill_active(self) -> bool:
        return self._skill_remaining > 1e-9
