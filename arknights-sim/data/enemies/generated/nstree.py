"""“自由的树” — generated from ArknightsGameData enemy_10152_nstree level 0.
motion=FLY  applyWay=RANGED  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_10152_nstree
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_nstree(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='“自由的树”',
        faction=Faction.ENEMY,
        max_hp=40000,
        atk=2500,
        defence=600,
        res=30.0,
        atk_interval=5.5,
        move_speed=0.4,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.AIRBORNE,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
