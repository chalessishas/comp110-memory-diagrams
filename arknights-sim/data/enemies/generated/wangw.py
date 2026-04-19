"""“执白者” — generated from ArknightsGameData enemy_3014_wangw level 0.
motion=WALK  applyWay=NONE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_3014_wangw
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_wangw(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='“执白者”',
        faction=Faction.ENEMY,
        max_hp=10000,
        atk=300,
        defence=250,
        res=0.0,
        atk_interval=3.0,
        move_speed=1.0,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
