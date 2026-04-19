"""“召毁者” — generated from ArknightsGameData enemy_7013_slwazd level 0.
motion=WALK  applyWay=RANGED  lifeReduce=30
Regenerate: python tools/gen_enemies.py enemy_7013_slwazd
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_slwazd(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='“召毁者”',
        faction=Faction.ENEMY,
        max_hp=400000,
        atk=600,
        defence=500,
        res=70.0,
        atk_interval=3.5,
        move_speed=0.8,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
