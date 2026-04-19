"""弧光镜卫 — generated from ArknightsGameData enemy_1329_cbshld level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1329_cbshld
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_cbshld(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='弧光镜卫',
        faction=Faction.ENEMY,
        max_hp=10000,
        atk=700,
        defence=3300,
        res=60.0,
        atk_interval=3.0,
        move_speed=0.75,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
