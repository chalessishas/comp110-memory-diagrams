"""旷野流贼 — generated from ArknightsGameData enemy_7019_thief level 0.
motion=WALK  applyWay=NONE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_7019_thief
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_thief(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='旷野流贼',
        faction=Faction.ENEMY,
        max_hp=35000,
        atk=0,
        defence=200,
        res=10.0,
        atk_interval=1.0,
        move_speed=1.1,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
