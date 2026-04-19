"""“雪牝” — generated from ArknightsGameData enemy_2014_csicer level 0.
motion=WALK  applyWay=RANGED  lifeReduce=3
Regenerate: python tools/gen_enemies.py enemy_2014_csicer
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_csicer(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='“雪牝”',
        faction=Faction.ENEMY,
        max_hp=40000,
        atk=700,
        defence=300,
        res=30.0,
        atk_interval=4.0,
        move_speed=0.6,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
