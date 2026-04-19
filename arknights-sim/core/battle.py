from __future__ import annotations
from dataclasses import dataclass, field
from math import sqrt
from typing import Dict, List, Optional, Set
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
    dp: float = 0.0           # current deployment points
    dp_rate: float = 1.0      # DP gained per simulated second

    lives: int = field(init=False)
    elapsed: float = field(init=False, default=0.0)
    log: BattleLog = field(default_factory=BattleLog)
    _goal_reachers: Set[int] = field(init=False, default_factory=set)        # id(enemy)
    _logged_dead: Set[int] = field(init=False, default_factory=set)          # id(entity)
    _block_assignments: Dict[int, List[Enemy]] = field(init=False, default_factory=dict)  # id(op) → enemies
    _pending_deploy: List[Operator] = field(init=False, default_factory=list)  # queued until DP available

    def __post_init__(self) -> None:
        self.lives = self.max_lives
        self.spawn_queue = sorted(self.spawn_queue, key=lambda e: e.time)

    def deploy(self, op: Operator) -> bool:
        """Attempt to deploy op now. Returns True if deployed, False if insufficient DP."""
        if self.dp < op.cost - 1e-9:   # epsilon absorbs float accumulation error
            return False
        self.dp -= op.cost
        if op not in self.operators:
            self.operators.append(op)
        self.log.record(f"t={self.elapsed:.1f}  {op.name} deployed  dp={self.dp:.1f}")
        return True

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
        self.dp += self.dp_rate * DT
        self._spawn_waves()
        self._compute_block_assignments()
        self._resolve_operators()
        self._resolve_enemies()
        self._cleanup_dead()

    def _compute_block_assignments(self) -> None:
        """Assign live enemies to melee operators up to their block capacity."""
        self._block_assignments = {id(op): [] for op in self.operators
                                   if op.alive and op.block > 0 and op.attack_range == "melee"}
        assigned: Set[int] = set()
        for op in self.operators:
            if not op.alive or op.block == 0 or op.attack_range != "melee":
                continue
            slots = op.block
            for enemy in self.enemies:
                if slots == 0:
                    break
                if enemy.alive and id(enemy) not in assigned:
                    self._block_assignments[id(op)].append(enemy)
                    assigned.add(id(enemy))
                    slots -= 1

    def _spawn_waves(self) -> None:
        while self.spawn_queue and self.spawn_queue[0].time <= self.elapsed:
            self.enemies.append(self.spawn_queue.pop(0).enemy)

    def _resolve_operators(self) -> None:
        for op in self.operators:
            if not op.alive:
                continue
            if op.attack_type == "heal":
                target = self._heal_target(op)
            else:
                target = self._blocked_enemy(op)
            op.update_skill(DT, has_target=target is not None)
            if op._skill_just_fired and op.skill:
                self.log.record(
                    f"t={self.elapsed:.1f}  {op.name} activates {op.skill.name}!"
                )
            if op._skill_just_ended and op.skill:
                self.log.record(
                    f"t={self.elapsed:.1f}  {op.name}'s {op.skill.name} ends"
                )
            if target and op.tick(DT):
                dmg = op.attack(target)
                if op.attack_type == "heal":
                    self.log.record(
                        f"t={self.elapsed:.1f}  {op.name} heals {target.name}  "
                        f"+{dmg}hp  ({target.hp}/{target.max_hp})"
                    )
                else:
                    self.log.record(
                        f"t={self.elapsed:.1f}  {op.name} → {target.name}  -{dmg}hp  "
                        f"({target.hp}/{target.max_hp})"
                    )
                if op.splash_radius > 0:
                    self._apply_splash(op, target)

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
            if (not entity.alive
                    and entity in self.enemies
                    and id(entity) not in self._goal_reachers
                    and id(entity) not in self._logged_dead):
                self.log.record(f"t={self.elapsed:.1f}  {entity.name} defeated")
                self._logged_dead.add(id(entity))

    def _blocked_enemy(self, op: Operator) -> Optional[Enemy]:
        """Return a live enemy for this operator to attack.

        Ranged operators can hit any live enemy (shoot over melee).
        Melee operators only attack enemies assigned to their block slot.
        """
        if op.attack_range == "ranged":
            live = [e for e in self.enemies if e.alive
                    and (not e.is_invisible or op.has_true_sight)]
            return max(live, key=lambda e: e._path_progress) if live else None
        # melee: first alive enemy in the block assignment
        for enemy in self._block_assignments.get(id(op), []):
            if enemy.alive:
                return enemy
        return None

    def _apply_splash(self, op: Operator, primary: Enemy) -> None:
        """Deal AOE damage to enemies within op.splash_radius tiles of primary."""
        primary_pos = primary.tile_pos
        if primary_pos is None:
            return
        px, py = primary_pos
        for enemy in self.enemies:
            if not enemy.alive or enemy is primary:
                continue
            epos = enemy.tile_pos
            if epos is None:
                continue
            dist = sqrt((epos[0] - px) ** 2 + (epos[1] - py) ** 2)
            if dist <= op.splash_radius:
                raw = op.effective_atk()
                if op.attack_type == "magic":
                    splash_dmg = enemy.take_magic(raw)
                else:
                    splash_dmg = enemy.take_physical(raw)
                self.log.record(
                    f"t={self.elapsed:.1f}  {op.name} splash → {enemy.name}  "
                    f"-{splash_dmg}hp  ({enemy.hp}/{enemy.max_hp})"
                )

    def _heal_target(self, op: Operator) -> Optional[Operator]:
        """Return most-injured living operator (lowest hp/max_hp); None if all full."""
        injured = [o for o in self.operators if o.alive and o.hp < o.max_hp]
        return min(injured, key=lambda o: o.hp / o.max_hp) if injured else None

    def _blocking_operator(self, enemy: Enemy) -> Optional[Operator]:
        """Return the melee operator physically blocking this enemy, if any."""
        for op in self.operators:
            if not op.alive:
                continue
            if enemy in self._block_assignments.get(id(op), []):
                return op
        return None

    def _is_won(self) -> bool:
        return not self.spawn_queue and all(not e.alive for e in self.enemies)

    def _is_lost(self) -> bool:
        all_ops_dead = bool(self.operators) and all(not op.alive for op in self.operators)
        return self.lives <= 0 or all_ops_dead
