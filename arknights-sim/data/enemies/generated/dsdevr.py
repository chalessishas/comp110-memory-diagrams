"""屠谕者，大群意志 — generated from ArknightsGameData enemy_1529_dsdevr level 0.
motion=WALK  applyWay=ALL  lifeReduce=3
Regenerate: python tools/gen_enemies.py enemy_1529_dsdevr
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_dsdevr(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='屠谕者，大群意志',
        faction=Faction.ENEMY,
        max_hp=10000,
        atk=800,
        defence=700,
        res=0.0,
        atk_interval=2.0,
        move_speed=0.8,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
