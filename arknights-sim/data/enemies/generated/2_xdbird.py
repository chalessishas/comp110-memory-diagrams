"""山谷雪灵 — generated from ArknightsGameData enemy_10140_xdbird_2 level 0.
motion=FLY  applyWay=RANGED  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_10140_xdbird_2
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_2_xdbird(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='山谷雪灵',
        faction=Faction.ENEMY,
        max_hp=6000,
        atk=300,
        defence=150,
        res=15.0,
        atk_interval=3.0,
        move_speed=0.6,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.AIRBORNE,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
