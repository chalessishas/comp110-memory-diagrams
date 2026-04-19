"""“毒瘤” — generated from ArknightsGameData enemy_6014_crzgas level 0.
motion=FLY  applyWay=NONE  lifeReduce=2
Regenerate: python tools/gen_enemies.py enemy_6014_crzgas
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_crzgas(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='“毒瘤”',
        faction=Faction.ENEMY,
        max_hp=50000,
        atk=0,
        defence=600,
        res=30.0,
        atk_interval=1.0,
        move_speed=0.3,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.AIRBORNE,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
