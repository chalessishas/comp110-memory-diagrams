"""眩光记录员 — generated from ArknightsGameData enemy_4052_mulaze level 0.
motion=FLY  applyWay=RANGED  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_4052_mulaze
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_mulaze(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='眩光记录员',
        faction=Faction.ENEMY,
        max_hp=29000,
        atk=730,
        defence=600,
        res=50.0,
        atk_interval=3.0,
        move_speed=0.9,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.AIRBORNE,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
