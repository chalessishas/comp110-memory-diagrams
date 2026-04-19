"""无垠回荡克雷松 — generated from ArknightsGameData enemy_2056_smedzi level 0.
motion=WALK  applyWay=RANGED  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_2056_smedzi
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_smedzi(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='无垠回荡克雷松',
        faction=Faction.ENEMY,
        max_hp=80000,
        atk=1000,
        defence=1500,
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
