from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Set
from .operator import Operator
from .enemy import Enemy


@dataclass
class SpawnEvent:
    time: float
    enemy: Enemy

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
    spawn_queue: List[SpawnEvent] = field(default_factory=list)

    lives: int = field(init=False)
    elapsed: float = field(init=False, default=0.0)
    log: BattleLog = field(default_factory=BattleLog)
    _goal_reachers: Set[int] = field(init=False, default_factory=set)  # id(enemy)

    def __post_init__(self) -> None:
        self.lives = self.max_lives
        self.spawn_queue = sorted(self.spawn_queue, key=lambda e: e.time)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(self, max_seconds: float = 300.0) -> str:
        """Simulate until win/loss or timeout. Returns 'win', 'loss', 'timeout'."""
        max_ticks = int(max_seconds * TICK_RATE)
        for _ in range(max_ticks):
            self._tick()
            if self._is_lost():
                return "loss"
            if self._is_won():
                return "win"
        return "timeout"

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _tick(self) -> None:
        self.elapsed += DT
        self._spawn_waves()
        self._resolve_operators()
        self._resolve_enemies()
        self._cleanup_dead()

    def _spawn_waves(self) -> None:
        while self.spawn_queue and self.spawn_queue[0].time <= self.elapsed:
            self.enemies.append(self.spawn_queue.pop(0).enemy)

    def _resolve_operators(self) -> None:
        for op in self.operators:
            if not op.alive:
                continue
            op.update_skill(DT)
            if op._skill_just_fired and op.skill:
                self.log.record(
                    f"t={self.elapsed:.1f}  {op.name} activates {op.skill.name}!"
                )
            if op._skill_just_ended and op.skill:
                self.log.record(
                    f"t={self.elapsed:.1f}  {op.name}'s {op.skill.name} ends"
                )
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
                # No blocker — enemy advances along path
                if enemy.advance(DT):
                    enemy.alive = False
                    self.lives -= 1
                    self._goal_reachers.add(id(enemy))
                    self.log.record(
                        f"t={self.elapsed:.1f}  {enemy.name} reached goal  "
                        f"lives={self.lives}/{self.max_lives}"
                    )

    def _cleanup_dead(self) -> None:
        for entity in list(self.operators) + list(self.enemies):
            if not entity.alive and entity in self.enemies and id(entity) not in self._goal_reachers:
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
        return not self.spawn_queue and all(not e.alive for e in self.enemies)

    def _is_lost(self) -> bool:
        all_ops_dead = bool(self.operators) and all(not op.alive for op in self.operators)
        return self.lives <= 0 or all_ops_dead
