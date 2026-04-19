"""榴弹佣兵 — generated from ArknightsGameData enemy_15015_dqmerr level 0.
motion=WALK  applyWay=ALL  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_15015_dqmerr
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_dqmerr(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='榴弹佣兵',
        faction=Faction.ENEMY,
        max_hp=3200,
        atk=500,
        defence=50,
        res=40.0,
        atk_interval=2.6,
        move_speed=0.9,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
