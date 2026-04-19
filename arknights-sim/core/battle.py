from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
from .operator import Operator
from .enemy import Enemy

TICK_RATE = 10       # ticks per simulated second
DT = 1.0 / TICK_RATE


@dataclass
class BattleLog:
    entries: List[str] = field(default_factory=list)

    def record(self, msg: str) -> None:
        self.entries.append(msg)

    def dump(self) -> str:
        return "\n".join(self.entries)


@dataclass
class Battle:
    operators: List[Operator]
    enemies: List[Enemy]
    max_lives: int = 3

    lives: int = field(init=False)
    elapsed: float = field(init=False, default=0.0)
    log: BattleLog = field(default_factory=BattleLog)

    def __post_init__(self) -> None:
        self.lives = self.max_lives

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(self, max_seconds: float = 300.0) -> str:
        """Simulate until win/loss or timeout. Returns 'win', 'loss', 'timeout'."""
        max_ticks = int(max_seconds * TICK_RATE)
        for _ in range(max_ticks):
            self._tick()
            if self._is_won():
                return "win"
            if self._is_lost():
                return "loss"
        return "timeout"

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _tick(self) -> None:
        self.elapsed += DT
        self._resolve_operators()
        self._resolve_enemies()
        self._cleanup_dead()

    def _resolve_operators(self) -> None:
        for op in self.operators:
            if not op.alive:
                continue
            target = self._blocked_enemy(op)
            if target and op.tick(DT):
                dmg = op.attack(target)
                self.log.record(
                    f"t={self.elapsed:.1f}  {op.name} → {target.name}  -{dmg}hp  "
                    f"({target.hp}/{target.max_hp})"
                )

    def _resolve_enemies(self) -> None:
        for enemy in self.enemies:
            if not enemy.alive:
                continue
            target = self._blocking_operator(enemy)
            if target:
                if enemy.tick(DT):
                    dmg = enemy.attack(target)
                    self.log.record(
                        f"t={self.elapsed:.1f}  {enemy.name} → {target.name}  -{dmg}hp  "
                        f"({target.hp}/{target.max_hp})"
                    )
            else:
                # No blocker — enemy reaches goal, lose a life
                enemy.alive = False
                self.lives -= 1
                self.log.record(
                    f"t={self.elapsed:.1f}  {enemy.name} reached goal  "
                    f"lives={self.lives}/{self.max_lives}"
                )

    def _cleanup_dead(self) -> None:
        for entity in list(self.operators) + list(self.enemies):
            if not entity.alive and entity in self.enemies:
                self.log.record(
                    f"t={self.elapsed:.1f}  {entity.name} defeated"
                )

    def _blocked_enemy(self, op: Operator) -> Optional[Enemy]:
        """Return the first live enemy that this operator is blocking."""
        for enemy in self.enemies:
            if enemy.alive:
                return enemy  # P1: single-lane, first enemy
        return None

    def _blocking_operator(self, enemy: Enemy) -> Optional[Operator]:
        """Return the first live operator blocking this enemy."""
        for op in self.operators:
            if op.alive and op.block > 0:
                return op
        return None

    def _is_won(self) -> bool:
        return all(not e.alive for e in self.enemies)

    def _is_lost(self) -> bool:
        return self.lives <= 0 or all(not op.alive for op in self.operators)
