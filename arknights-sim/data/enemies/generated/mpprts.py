"""PRTS，“源代码” — generated from ArknightsGameData enemy_1564_mpprts level 0.
motion=WALK  applyWay=NONE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1564_mpprts
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_mpprts(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='PRTS，“源代码”',
        faction=Faction.ENEMY,
        max_hp=50000,
        atk=1000,
        defence=3000,
        res=75.0,
        atk_interval=1.0,
        move_speed=1.0,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
