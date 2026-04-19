"""披挂冰雪的少女 — generated from ArknightsGameData enemy_1574_xdagt level 0.
motion=WALK  applyWay=RANGED  lifeReduce=2
Regenerate: python tools/gen_enemies.py enemy_1574_xdagt
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_xdagt(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='披挂冰雪的少女',
        faction=Faction.ENEMY,
        max_hp=125000,
        atk=600,
        defence=600,
        res=40.0,
        atk_interval=7.0,
        move_speed=0.1,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
