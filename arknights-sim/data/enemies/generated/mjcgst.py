"""沃尔夫之影 — generated from ArknightsGameData enemy_10109_mjcgst level 0.
motion=WALK  applyWay=RANGED  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_10109_mjcgst
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_mjcgst(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='沃尔夫之影',
        faction=Faction.ENEMY,
        max_hp=15000,
        atk=520,
        defence=0,
        res=50.0,
        atk_interval=2.4,
        move_speed=0.6,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
