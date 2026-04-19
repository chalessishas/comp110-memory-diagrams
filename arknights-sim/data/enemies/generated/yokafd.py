"""无人机龙哥（暂命名） — generated from ArknightsGameData enemy_5005_yokafd level 0.
motion=FLY  applyWay=RANGED  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_5005_yokafd
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_yokafd(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='无人机龙哥（暂命名）',
        faction=Faction.ENEMY,
        max_hp=50000,
        atk=400,
        defence=350,
        res=30.0,
        atk_interval=3.0,
        move_speed=1.0,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.AIRBORNE,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
