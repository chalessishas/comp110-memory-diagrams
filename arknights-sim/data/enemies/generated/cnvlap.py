"""“狂欢之主” — generated from ArknightsGameData enemy_1560_cnvlap level 0.
motion=FLY  applyWay=ALL  lifeReduce=2
Regenerate: python tools/gen_enemies.py enemy_1560_cnvlap
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_cnvlap(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='“狂欢之主”',
        faction=Faction.ENEMY,
        max_hp=60000,
        atk=425,
        defence=500,
        res=30.0,
        atk_interval=5.0,
        move_speed=1.0,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.AIRBORNE,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
