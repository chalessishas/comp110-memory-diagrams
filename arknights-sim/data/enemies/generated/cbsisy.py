"""“十字路口”量产型 — generated from ArknightsGameData enemy_1331_cbsisy level 0.
motion=WALK  applyWay=RANGED  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1331_cbsisy
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_cbsisy(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='“十字路口”量产型',
        faction=Faction.ENEMY,
        max_hp=15000,
        atk=190,
        defence=800,
        res=10.0,
        atk_interval=0.6,
        move_speed=0.8,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
