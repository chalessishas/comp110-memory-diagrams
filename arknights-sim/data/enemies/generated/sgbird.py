"""“滑翔的玩具” — generated from ArknightsGameData enemy_10015_sgbird level 0.
motion=FLY  applyWay=NONE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_10015_sgbird
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_sgbird(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='“滑翔的玩具”',
        faction=Faction.ENEMY,
        max_hp=4000,
        atk=150,
        defence=50,
        res=10.0,
        atk_interval=2.0,
        move_speed=2.5,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.AIRBORNE,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
