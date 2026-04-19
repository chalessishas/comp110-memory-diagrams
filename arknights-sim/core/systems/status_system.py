"""Status decay — 减少所有状态/buff 的剩余时间，过期移除."""
from __future__ import annotations
from ..state.unit_state import UnitState


def status_decay_system(world, dt: float) -> None:
    now = world.global_state.elapsed
    for u in world.units:
        if not u.alive:
            continue
        # drop expired statuses
        u.statuses = [s for s in u.statuses if s.expires_at > now]
        # drop expired buffs
        u.buffs = [b for b in u.buffs if b.expires_at > now]
