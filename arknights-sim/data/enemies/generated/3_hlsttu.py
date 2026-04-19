"""“牧首” — generated from ArknightsGameData enemy_10091_hlsttu_3 level 0.
motion=WALK  applyWay=RANGED  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_10091_hlsttu_3
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_3_hlsttu(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='“牧首”',
        faction=Faction.ENEMY,
        max_hp=75000,
        atk=225,
        defence=150,
        res=50.0,
        atk_interval=1.2,
        move_speed=1.0,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
