"""绸缪 — generated from ArknightsGameData enemy_10055_cjgost level 0.
motion=WALK  applyWay=NONE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_10055_cjgost
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_cjgost(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='绸缪',
        faction=Faction.ENEMY,
        max_hp=9000,
        atk=100,
        defence=350,
        res=50.0,
        atk_interval=1.7,
        move_speed=1.0,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
