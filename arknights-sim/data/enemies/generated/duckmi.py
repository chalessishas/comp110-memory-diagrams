"""鸭爵 — generated from ArknightsGameData enemy_2001_duckmi level 0.
motion=WALK  applyWay=NONE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_2001_duckmi
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_duckmi(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='鸭爵',
        faction=Faction.ENEMY,
        max_hp=18000,
        atk=100,
        defence=200,
        res=30.0,
        atk_interval=1.0,
        move_speed=0.4,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
