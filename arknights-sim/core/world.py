"""World — 战斗世界中枢.

持有所有状态容器 + 事件队列 + 按 TickPhase 编排 Systems 调用.

用法：
    world = World(tile_grid=..., global_state=...)
    world.add_unit(make_silverash())
    world.run(max_seconds=300.0)
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

from .events.event_queue import EventQueue
from .state.global_state import GlobalState
from .state.tile_state import TileGrid
from .state.unit_state import UnitState
from .types import DT, TICK_PHASE_ORDER, TICK_RATE, Faction, TickPhase, TileType


SystemFn = Callable[["World", float], None]   # (world, dt) -> None


@dataclass
class World:
    tile_grid: TileGrid
    global_state: GlobalState = field(default_factory=GlobalState)
    event_queue: EventQueue = field(default_factory=EventQueue)
    units: List[UnitState] = field(default_factory=list)

    # Systems 按 phase 分桶注册 — run() 时按 TICK_PHASE_ORDER 跑
    _systems: Dict[TickPhase, List[SystemFn]] = field(default_factory=dict)

    # 日志
    log_entries: List[str] = field(default_factory=list)

    # --------------------------------------------------------------------
    # System registration
    # --------------------------------------------------------------------

    def register_system(self, phase: TickPhase, fn: SystemFn) -> None:
        self._systems.setdefault(phase, []).append(fn)

    def unregister_all_systems(self) -> None:
        self._systems.clear()

    # --------------------------------------------------------------------
    # Unit management
    # --------------------------------------------------------------------

    def add_unit(self, unit: UnitState) -> None:
        self.units.append(unit)

    def allies(self) -> List[UnitState]:
        return [u for u in self.units if u.alive and u.faction == Faction.ALLY]

    def enemies(self) -> List[UnitState]:
        return [u for u in self.units if u.alive and u.faction == Faction.ENEMY]

    def unit_by_id(self, unit_id: int) -> Optional[UnitState]:
        for u in self.units:
            if u.unit_id == unit_id:
                return u
        return None

    # --------------------------------------------------------------------
    # Tick loop
    # --------------------------------------------------------------------

    def deploy(self, unit: UnitState) -> bool:
        """Spend DP and mark unit as deployed. Returns False if invalid."""
        if self.global_state.elapsed < unit.redeploy_available_at - 1e-9:
            return False  # still in redeploy cooldown
        if not self.global_state.try_spend_dp(unit.cost):
            return False
        # Tile type enforcement: melee on GROUND, ranged on ELEVATED
        if unit.position is not None and self.tile_grid is not None:
            tx, ty = round(unit.position[0]), round(unit.position[1])
            tile = self.tile_grid.get(tx, ty)
            if tile is not None:
                if tile.type in (TileType.BLOCKED, TileType.HOLE):
                    self.global_state.dp += unit.cost   # refund
                    return False
                if unit.attack_range_melee and tile.type == TileType.ELEVATED:
                    self.global_state.dp += unit.cost   # refund
                    return False  # melee cannot deploy on elevated
                if not unit.attack_range_melee and tile.type == TileType.GROUND:
                    self.global_state.dp += unit.cost   # refund
                    return False  # ranged cannot deploy on ground
        unit.deployed = True
        unit.deploy_time = self.global_state.elapsed
        unit.redeploy_available_at = 0.0
        if unit not in self.units:
            self.units.append(unit)
        self.log(f"{unit.name} deployed  dp={self.global_state.dp}")
        return True

    def retreat(self, unit: UnitState) -> None:
        """Remove operator from field, start redeploy cooldown, refund half DP."""
        if not unit.alive or not unit.deployed or unit.faction == Faction.ENEMY:
            return  # dead units and enemies cannot retreat
        unit.deployed = False
        unit.redeploy_available_at = self.global_state.elapsed + unit.redeploy_cd
        # Arknights refunds 50% of DP cost on retreat (floor)
        refund = unit.cost // 2
        self.global_state.dp += refund
        self.log(
            f"{unit.name} retreated  cd={unit.redeploy_cd:.0f}s  "
            f"refund={refund}  dp={self.global_state.dp}"
        )

    def tick(self, dt: float = DT) -> None:
        self.global_state.elapsed += dt
        self.global_state.tick_count += 1
        self.global_state.tick_dp(dt)
        for phase in TICK_PHASE_ORDER:
            for fn in self._systems.get(phase, ()):
                fn(self, dt)
        # Special: EVENT_QUEUE phase also dispatches due events
        self.event_queue.dispatch_due(self, self.global_state.elapsed)

    def run(self, max_seconds: float = 300.0) -> str:
        max_ticks = int(max_seconds * TICK_RATE)
        for _ in range(max_ticks):
            self.tick()
            if self.is_lost:
                return "loss"
            if self.is_won:
                return "win"
        return "timeout"

    # --------------------------------------------------------------------
    # Win / loss
    # --------------------------------------------------------------------

    @property
    def is_lost(self) -> bool:
        return self.global_state.is_defeat

    @property
    def is_won(self) -> bool:
        """No enemies alive AND no more spawns queued (spawns are EventQueue events)."""
        if any(u.alive for u in self.enemies()):
            return False
        # Check if any spawn events are still pending
        ev = self.event_queue.peek()
        if ev is not None and ev.kind == "spawn":
            return False
        return True

    # --------------------------------------------------------------------
    # Logging
    # --------------------------------------------------------------------

    def log(self, msg: str) -> None:
        t = self.global_state.elapsed
        self.log_entries.append(f"t={t:.1f}  {msg}")
