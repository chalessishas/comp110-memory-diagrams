"""“不朽之人” — generated from ArknightsGameData enemy_7009_mtmoun level 0.
motion=WALK  applyWay=ALL  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_7009_mtmoun
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_mtmoun(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='“不朽之人”',
        faction=Faction.ENEMY,
        max_hp=900000,
        atk=4500,
        defence=1000,
        res=0.0,
        atk_interval=7.0,
        move_speed=0.5,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
