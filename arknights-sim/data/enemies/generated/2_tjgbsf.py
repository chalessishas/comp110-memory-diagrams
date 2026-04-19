"""扶潮·归 — generated from ArknightsGameData enemy_10173_tjgbsf_2 level 0.
motion=WALK  applyWay=RANGED  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_10173_tjgbsf_2
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_2_tjgbsf(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='扶潮·归',
        faction=Faction.ENEMY,
        max_hp=9600,
        atk=300,
        defence=100,
        res=40.0,
        atk_interval=4.5,
        move_speed=0.5,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
