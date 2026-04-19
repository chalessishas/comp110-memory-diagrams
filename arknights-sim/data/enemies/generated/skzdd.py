"""博卓卡斯替，圣卫铳骑 — generated from ArknightsGameData enemy_2082_skzdd level 0.
motion=WALK  applyWay=ALL  lifeReduce=30
Regenerate: python tools/gen_enemies.py enemy_2082_skzdd
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_skzdd(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='博卓卡斯替，圣卫铳骑',
        faction=Faction.ENEMY,
        max_hp=150000,
        atk=3000,
        defence=5000,
        res=80.0,
        atk_interval=3.8,
        move_speed=0.35,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
