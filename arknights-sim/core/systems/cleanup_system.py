"""Cleanup — 移除死亡单位，统计击杀."""
from __future__ import annotations
from ..types import Faction


def cleanup_system(world, dt: float) -> None:
    for u in world.units:
        if not u.alive and u.deployed and u.faction == Faction.ENEMY:
            # If died from damage (not goal leak), count as defeated
            if getattr(u, "_counted_death", False) is False:
                world.global_state.enemies_defeated += 1
                setattr(u, "_counted_death", True)
