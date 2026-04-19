"""转译基底·β — generated from ArknightsGameData enemy_10081_mpplai_2 level 0.
motion=WALK  applyWay=NONE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_10081_mpplai_2
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_2_mpplai(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='转译基底·β',
        faction=Faction.ENEMY,
        max_hp=4000,
        atk=200,
        defence=600,
        res=45.0,
        atk_interval=1.0,
        move_speed=1.0,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
