from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
from .entity import Entity
from .skill import Skill


@dataclass
class Operator(Entity):
    """A deployed operator. Attacks the first enemy it is blocking."""
    attack_type: str = "physical"  # "physical" | "magic" | "heal"

    skill: Optional[Skill] = None
    sp: float = 0.0
    sp_gain_rate: float = 1.0        # SP per second for auto_time
    sp_gain_per_attack: float = 1.0  # SP per hit for auto_attack

    _skill_remaining: float = field(init=False, default=0.0)
    _atk_bonus: int = field(init=False, default=0)
    _skill_just_fired: bool = field(init=False, default=False)
    _skill_just_ended: bool = field(init=False, default=False)

    def effective_atk(self) -> int:
        return self.atk + self._atk_bonus

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

    def update_skill(self, dt: float) -> None:
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
            self.sp = 0.0
            self._skill_remaining = self.skill.duration
            if self.skill.on_start:
                self.skill.on_start(self)
            self._skill_just_fired = True

    @property
    def skill_active(self) -> bool:
        return self._skill_remaining > 1e-9
