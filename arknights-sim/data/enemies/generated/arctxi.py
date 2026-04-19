"""“两栖号”船车 — generated from ArknightsGameData enemy_5505_arctxi level 0.
motion=WALK  applyWay=NONE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_5505_arctxi
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_arctxi(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='“两栖号”船车',
        faction=Faction.ENEMY,
        max_hp=4200,
        atk=500,
        defence=700,
        res=30.0,
        atk_interval=10.0,
        move_speed=0.7,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
