"""红宝石飞翼 — generated from ArknightsGameData enemy_4041_mundr level 0.
motion=FLY  applyWay=NONE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_4041_mundr
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_mundr(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='红宝石飞翼',
        faction=Faction.ENEMY,
        max_hp=600,
        atk=100,
        defence=0,
        res=0.0,
        atk_interval=1.0,
        move_speed=1.0,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.AIRBORNE,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
