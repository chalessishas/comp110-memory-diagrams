"""啸天吸尘器·大力版 — generated from ArknightsGameData enemy_10148_nsmos_2 level 0.
motion=FLY  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_10148_nsmos_2
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_2_nsmos(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='啸天吸尘器·大力版',
        faction=Faction.ENEMY,
        max_hp=7000,
        atk=250,
        defence=200,
        res=50.0,
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
