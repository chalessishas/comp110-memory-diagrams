"""莫菲丝 — generated from ArknightsGameData enemy_1569_ldevil level 0.
motion=WALK  applyWay=RANGED  lifeReduce=2
Regenerate: python tools/gen_enemies.py enemy_1569_ldevil
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_ldevil(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='莫菲丝',
        faction=Faction.ENEMY,
        max_hp=60000,
        atk=680,
        defence=580,
        res=35.0,
        atk_interval=2.8,
        move_speed=0.7,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
