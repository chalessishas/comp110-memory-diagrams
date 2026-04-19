"""小八界 — generated from ArknightsGameData enemy_2125_dylnpp level 0.
motion=WALK  applyWay=NONE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_2125_dylnpp
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_dylnpp(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='小八界',
        faction=Faction.ENEMY,
        max_hp=25000,
        atk=500,
        defence=200,
        res=30.0,
        atk_interval=1.0,
        move_speed=0.6,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
