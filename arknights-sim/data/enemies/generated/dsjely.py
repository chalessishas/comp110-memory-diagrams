"""浮海飘航者 — generated from ArknightsGameData enemy_1150_dsjely level 0.
motion=FLY  applyWay=RANGED  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1150_dsjely
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_dsjely(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='浮海飘航者',
        faction=Faction.ENEMY,
        max_hp=3000,
        atk=220,
        defence=200,
        res=20.0,
        atk_interval=3.0,
        move_speed=0.75,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.AIRBORNE,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
