"""护盾高阶术师 — generated from ArknightsGameData enemy_1036_amraoe level 0.
motion=WALK  applyWay=RANGED  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1036_amraoe
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_amraoe(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='护盾高阶术师',
        faction=Faction.ENEMY,
        max_hp=8500,
        atk=380,
        defence=400,
        res=20.0,
        atk_interval=3.8,
        move_speed=0.7,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
