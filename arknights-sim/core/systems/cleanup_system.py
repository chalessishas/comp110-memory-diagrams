"""Cleanup — 移除死亡单位，统计击杀，派发 on_death 钩子."""
from __future__ import annotations
from ..types import Faction
from .talent_registry import fire_on_death


def cleanup_system(world, dt: float) -> None:
    for u in list(world.units):
        if not u.alive and u.deployed and u.faction == Faction.ENEMY:
            # If died from damage (not goal leak), count as defeated
            if not u.counted_death:
                world.global_state.enemies_defeated += 1
                u.counted_death = True

        # Dispatch on_death for any unit that just died this tick
        if getattr(u, "_just_died", False):
            u._just_died = False
            fire_on_death(world, u)
