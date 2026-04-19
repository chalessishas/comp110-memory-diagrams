"""“人间烟火” — generated from ArknightsGameData enemy_10061_cjglon level 0.
motion=WALK  applyWay=NONE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_10061_cjglon
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_cjglon(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='“人间烟火”',
        faction=Faction.ENEMY,
        max_hp=100,
        atk=8000,
        defence=0,
        res=0.0,
        atk_interval=1.6,
        move_speed=3.0,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
