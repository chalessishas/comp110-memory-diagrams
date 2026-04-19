"""拟态机械 — generated from ArknightsGameData enemy_1565_mpprme level 0.
motion=WALK  applyWay=RANGED  lifeReduce=3
Regenerate: python tools/gen_enemies.py enemy_1565_mpprme
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_mpprme(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='拟态机械',
        faction=Faction.ENEMY,
        max_hp=25000,
        atk=600,
        defence=3000,
        res=75.0,
        atk_interval=4.0,
        move_speed=0.5,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
