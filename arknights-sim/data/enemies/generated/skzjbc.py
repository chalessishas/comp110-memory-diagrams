"""托生莲座 — generated from ArknightsGameData enemy_2090_skzjbc level 0.
motion=FLY  applyWay=NONE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_2090_skzjbc
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_skzjbc(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='托生莲座',
        faction=Faction.ENEMY,
        max_hp=50000,
        atk=500,
        defence=2000,
        res=50.0,
        atk_interval=3.0,
        move_speed=0.8,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.AIRBORNE,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
