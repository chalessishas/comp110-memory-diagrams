"""小雪伞 — generated from ArknightsGameData enemy_10143_xdmush level 0.
motion=WALK  applyWay=RANGED  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_10143_xdmush
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_xdmush(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='小雪伞',
        faction=Faction.ENEMY,
        max_hp=12000,
        atk=500,
        defence=600,
        res=0.0,
        atk_interval=3.5,
        move_speed=1.0,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
