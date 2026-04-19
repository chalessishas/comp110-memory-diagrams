"""艺术的慈悲！ — generated from ArknightsGameData enemy_5008_cstrwd level 0.
motion=FLY  applyWay=NONE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_5008_cstrwd
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_cstrwd(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='艺术的慈悲！',
        faction=Faction.ENEMY,
        max_hp=100000000,
        atk=0,
        defence=0,
        res=0.0,
        atk_interval=1.0,
        move_speed=5.0,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.AIRBORNE,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
