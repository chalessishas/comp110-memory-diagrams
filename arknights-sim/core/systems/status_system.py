"""Status decay — 减少所有状态/buff 的剩余时间，过期移除."""
from __future__ import annotations
from ..state.unit_state import UnitState


def status_decay_system(world, dt: float) -> None:
    now = world.global_state.elapsed
    for u in world.units:
        if not u.alive:
            continue
        # keep while expires_at + epsilon >= now — guards floating-point accumulation
        # (e.g. 20 × 0.1 = 2.0000000000000004, not 2.0)
        u.statuses = [s for s in u.statuses if s.expires_at + 1e-9 >= now]
        u.buffs = [b for b in u.buffs if b.expires_at + 1e-9 >= now]
