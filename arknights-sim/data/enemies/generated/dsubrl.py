"""深溟巢涌者 — generated from ArknightsGameData enemy_1234_dsubrl level 0.
motion=WALK  applyWay=RANGED  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1234_dsubrl
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_dsubrl(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='深溟巢涌者',
        faction=Faction.ENEMY,
        max_hp=10000,
        atk=140,
        defence=550,
        res=60.0,
        atk_interval=1.0,
        move_speed=0.8,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
