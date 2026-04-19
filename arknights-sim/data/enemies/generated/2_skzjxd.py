"""圆仔 — generated from ArknightsGameData enemy_2085_skzjxd_2 level 0.
motion=WALK  applyWay=NONE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_2085_skzjxd_2
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_2_skzjxd(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='圆仔',
        faction=Faction.ENEMY,
        max_hp=13000,
        atk=500,
        defence=0,
        res=50.0,
        atk_interval=1.0,
        move_speed=0.35,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
