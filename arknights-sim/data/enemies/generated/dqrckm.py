"""“配重投石机” — generated from ArknightsGameData enemy_15043_dqrckm level 0.
motion=WALK  applyWay=MELEE  lifeReduce=2
Regenerate: python tools/gen_enemies.py enemy_15043_dqrckm
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_dqrckm(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='“配重投石机”',
        faction=Faction.ENEMY,
        max_hp=75000,
        atk=1500,
        defence=600,
        res=0.0,
        atk_interval=4.4,
        move_speed=0.5,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
