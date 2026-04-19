"""纤核漂游者 — generated from ArknightsGameData enemy_1435_dsflys level 0.
motion=FLY  applyWay=RANGED  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1435_dsflys
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_dsflys(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='纤核漂游者',
        faction=Faction.ENEMY,
        max_hp=5100,
        atk=300,
        defence=80,
        res=30.0,
        atk_interval=3.5,
        move_speed=0.7,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.AIRBORNE,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
