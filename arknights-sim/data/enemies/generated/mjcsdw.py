"""“破茧之梦” — generated from ArknightsGameData enemy_10110_mjcsdw level 0.
motion=FLY  applyWay=RANGED  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_10110_mjcsdw
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_mjcsdw(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='“破茧之梦”',
        faction=Faction.ENEMY,
        max_hp=30000,
        atk=140,
        defence=800,
        res=40.0,
        atk_interval=2.2,
        move_speed=1.0,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.AIRBORNE,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
