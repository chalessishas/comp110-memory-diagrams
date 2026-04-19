"""Goal — 敌人到达终点扣命."""
from __future__ import annotations
from ..types import Faction


def goal_system(world, dt: float) -> None:
    for u in world.units:
        if not u.alive or u.faction != Faction.ENEMY or not u.path:
            continue
        max_progress = float(len(u.path) - 1)
        if u.path_progress >= max_progress:
            u.alive = False
            world.global_state.lose_life()
            world.log(f"{u.name} reached goal — lives={world.global_state.lives}")
