"""GlobalState — 所有与单个单位无关的战斗状态.

包含资源（DP/lives）、时间、RNG、累计统计（伤害总量等）。
"""
from __future__ import annotations
import random
from dataclasses import dataclass, field


@dataclass
class GlobalState:
    # 时间
    elapsed: float = 0.0                 # game seconds since battle start
    tick_count: int = 0

    # 资源
    dp: int = 0                          # 部署费用 (cost points)
    dp_cap: int = 99
    dp_gain_rate: float = 1.0            # DP/s 自然回复 (实际游戏略低)
    _dp_fractional: float = 0.0          # sub-integer DP accumulator

    lives: int = 3
    max_lives: int = 3

    # 随机
    rng_seed: int = 0
    rng: random.Random = field(init=False)

    # 累计统计 (for tests & achievements)
    total_damage_dealt: int = 0
    total_damage_taken: int = 0
    total_healing_done: int = 0
    enemies_defeated: int = 0
    enemies_leaked: int = 0

    def __post_init__(self) -> None:
        self.rng = random.Random(self.rng_seed)

    # ---- DP ---------------------------------------------------------------

    def tick_dp(self, dt: float) -> None:
        """Accumulate DP at `dp_gain_rate` per second, clamped to dp_cap."""
        if self.dp >= self.dp_cap:
            return
        self._dp_fractional += self.dp_gain_rate * dt
        while self._dp_fractional >= 1.0 and self.dp < self.dp_cap:
            self.dp += 1
            self._dp_fractional -= 1.0

    def try_spend_dp(self, cost: int) -> bool:
        if self.dp < cost:
            return False
        self.dp -= cost
        return True

    def refund_dp(self, amount: int) -> None:
        self.dp = min(self.dp + amount, self.dp_cap)

    # ---- Lives ------------------------------------------------------------

    def lose_life(self) -> None:
        self.lives = max(0, self.lives - 1)
        self.enemies_leaked += 1

    @property
    def is_defeat(self) -> bool:
        return self.lives <= 0
