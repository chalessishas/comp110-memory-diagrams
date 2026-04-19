"""阿利斯泰尔，帝国余晖 — generated from ArknightsGameData enemy_1559_vtlionk level 0.
motion=WALK  applyWay=RANGED  lifeReduce=15
Regenerate: python tools/gen_enemies.py enemy_1559_vtlionk
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_vtlionk(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='阿利斯泰尔，帝国余晖',
        faction=Faction.ENEMY,
        max_hp=81000,
        atk=920,
        defence=1030,
        res=20.0,
        atk_interval=8.2,
        move_speed=1.0,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
