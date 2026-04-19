"""“睚” — generated from ArknightsGameData enemy_1538_ymmons level 0.
motion=WALK  applyWay=ALL  lifeReduce=2
Regenerate: python tools/gen_enemies.py enemy_1538_ymmons
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_ymmons(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='“睚”',
        faction=Faction.ENEMY,
        max_hp=65000,
        atk=600,
        defence=450,
        res=50.0,
        atk_interval=5.0,
        move_speed=0.3,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
