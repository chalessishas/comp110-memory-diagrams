"""“无根之怨” — generated from ArknightsGameData enemy_6018_carrier level 0.
motion=FLY  applyWay=NONE  lifeReduce=3
Regenerate: python tools/gen_enemies.py enemy_6018_carrier
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_carrier(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='“无根之怨”',
        faction=Faction.ENEMY,
        max_hp=96000,
        atk=300,
        defence=605,
        res=65.0,
        atk_interval=5.0,
        move_speed=0.4,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.AIRBORNE,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
