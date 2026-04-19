"""Passive talent system — fires on_tick hooks for all deployed alive allies each tick."""
from __future__ import annotations
from ..types import Faction
from .talent_registry import fire_on_tick


def passive_talent_system(world, dt: float) -> None:
    for u in world.units:
        if not u.alive or not u.deployed or not u.talents:
            continue
        if u.faction != Faction.ALLY:
            continue
        fire_on_tick(world, u, dt)
