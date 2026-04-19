"""矩兽 — generated from ArknightsGameData enemy_2124_dyjsfg level 0.
motion=WALK  applyWay=NONE  lifeReduce=30
Regenerate: python tools/gen_enemies.py enemy_2124_dyjsfg
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_dyjsfg(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='矩兽',
        faction=Faction.ENEMY,
        max_hp=350000,
        atk=1500,
        defence=1000,
        res=10.0,
        atk_interval=6.0,
        move_speed=0.3,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
