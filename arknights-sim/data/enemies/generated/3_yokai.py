"""威龙 — generated from ArknightsGameData enemy_1005_yokai_3 level 0.
motion=FLY  applyWay=RANGED  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1005_yokai_3
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_3_yokai(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='威龙',
        faction=Faction.ENEMY,
        max_hp=30000,
        atk=660,
        defence=170,
        res=0.0,
        atk_interval=3.8,
        move_speed=0.5,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.AIRBORNE,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
