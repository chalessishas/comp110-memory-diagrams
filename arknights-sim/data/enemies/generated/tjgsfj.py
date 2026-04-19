"""挟潮 — generated from ArknightsGameData enemy_10167_tjgsfj level 0.
motion=WALK  applyWay=RANGED  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_10167_tjgsfj
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_tjgsfj(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='挟潮',
        faction=Faction.ENEMY,
        max_hp=8000,
        atk=250,
        defence=50,
        res=40.0,
        atk_interval=4.5,
        move_speed=0.5,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
