"""“岁” — generated from ArknightsGameData enemy_2119_dyshhj level 0.
motion=FLY  applyWay=MELEE  lifeReduce=50
Regenerate: python tools/gen_enemies.py enemy_2119_dyshhj
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_dyshhj(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='“岁”',
        faction=Faction.ENEMY,
        max_hp=560000,
        atk=800,
        defence=800,
        res=50.0,
        atk_interval=4.0,
        move_speed=1.0,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.AIRBORNE,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
