"""古德因纳夫先生 — generated from ArknightsGameData enemy_2084_skzcan level 0.
motion=WALK  applyWay=NONE  lifeReduce=5
Regenerate: python tools/gen_enemies.py enemy_2084_skzcan
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_skzcan(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='古德因纳夫先生',
        faction=Faction.ENEMY,
        max_hp=80000,
        atk=500,
        defence=1000,
        res=50.0,
        atk_interval=1.0,
        move_speed=0.2,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
