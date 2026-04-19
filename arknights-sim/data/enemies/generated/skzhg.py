"""“放逐的黑棺” — generated from ArknightsGameData enemy_2083_skzhg level 0.
motion=WALK  applyWay=NONE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_2083_skzhg
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_skzhg(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='“放逐的黑棺”',
        faction=Faction.ENEMY,
        max_hp=8000,
        atk=0,
        defence=500,
        res=50.0,
        atk_interval=5.0,
        move_speed=1.0,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
