"""“惘核” — generated from ArknightsGameData enemy_10128_fearpj level 0.
motion=FLY  applyWay=RANGED  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_10128_fearpj
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_fearpj(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='“惘核”',
        faction=Faction.ENEMY,
        max_hp=5000,
        atk=700,
        defence=100,
        res=50.0,
        atk_interval=1.0,
        move_speed=0.8,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.AIRBORNE,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
