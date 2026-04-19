"""“小惊喜” — generated from ArknightsGameData enemy_2012_csbln level 0.
motion=FLY  applyWay=NONE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_2012_csbln
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_csbln(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='“小惊喜”',
        faction=Faction.ENEMY,
        max_hp=4000,
        atk=400,
        defence=0,
        res=0.0,
        atk_interval=1.0,
        move_speed=0.5,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.AIRBORNE,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
