"""依然“狼之主” — generated from ArknightsGameData enemy_15023_dqwlfm level 0.
motion=WALK  applyWay=ALL  lifeReduce=3
Regenerate: python tools/gen_enemies.py enemy_15023_dqwlfm
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_dqwlfm(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='依然“狼之主”',
        faction=Faction.ENEMY,
        max_hp=50000,
        atk=1000,
        defence=1300,
        res=60.0,
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
