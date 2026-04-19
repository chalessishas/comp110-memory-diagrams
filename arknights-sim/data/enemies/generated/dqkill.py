"""杰斯顿·威廉姆斯 — generated from ArknightsGameData enemy_5055_dqkill level 0.
motion=WALK  applyWay=ALL  lifeReduce=2
Regenerate: python tools/gen_enemies.py enemy_5055_dqkill
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_dqkill(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='杰斯顿·威廉姆斯',
        faction=Faction.ENEMY,
        max_hp=25000,
        atk=700,
        defence=400,
        res=20.0,
        atk_interval=4.0,
        move_speed=0.6,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
