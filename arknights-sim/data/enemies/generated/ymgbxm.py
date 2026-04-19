"""压力舒缓帮手 — generated from ArknightsGameData enemy_10119_ymgbxm level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_10119_ymgbxm
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_ymgbxm(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='压力舒缓帮手',
        faction=Faction.ENEMY,
        max_hp=35000,
        atk=3000,
        defence=1500,
        res=0.0,
        atk_interval=7.0,
        move_speed=0.5,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
