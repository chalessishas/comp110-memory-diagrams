"""啸天吸尘器 — generated from ArknightsGameData enemy_10148_nsmos level 0.
motion=FLY  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_10148_nsmos
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_nsmos(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='啸天吸尘器',
        faction=Faction.ENEMY,
        max_hp=6000,
        atk=200,
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
