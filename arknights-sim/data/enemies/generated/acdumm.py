"""假想敌：弦 — generated from ArknightsGameData enemy_9022_acdumm level 0.
motion=WALK  applyWay=RANGED  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_9022_acdumm
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_acdumm(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='假想敌：弦',
        faction=Faction.ENEMY,
        max_hp=85000,
        atk=120,
        defence=700,
        res=50.0,
        atk_interval=5.0,
        move_speed=1.0,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
