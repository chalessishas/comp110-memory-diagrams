"""炙烤螺旋桨 — generated from ArknightsGameData enemy_10150_nsheat level 0.
motion=FLY  applyWay=RANGED  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_10150_nsheat
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_nsheat(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='炙烤螺旋桨',
        faction=Faction.ENEMY,
        max_hp=15000,
        atk=360,
        defence=200,
        res=60.0,
        atk_interval=4.5,
        move_speed=0.4,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.AIRBORNE,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
