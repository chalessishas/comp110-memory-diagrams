"""盐风主教昆图斯 — generated from ArknightsGameData enemy_1521_dslily level 0.
motion=WALK  applyWay=RANGED  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1521_dslily
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_dslily(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='盐风主教昆图斯',
        faction=Faction.ENEMY,
        max_hp=100000,
        atk=380,
        defence=500,
        res=50.0,
        atk_interval=3.5,
        move_speed=0.1,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
