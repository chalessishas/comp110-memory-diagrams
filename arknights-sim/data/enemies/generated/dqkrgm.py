"""雪境精锐 — generated from ArknightsGameData enemy_15006_dqkrgm level 0.
motion=WALK  applyWay=RANGED  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_15006_dqkrgm
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_dqkrgm(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='雪境精锐',
        faction=Faction.ENEMY,
        max_hp=15000,
        atk=600,
        defence=600,
        res=50.0,
        atk_interval=3.7,
        move_speed=0.9,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
