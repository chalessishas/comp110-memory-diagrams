"""阿格尼尔神父 — generated from ArknightsGameData enemy_1284_sgprst level 0.
motion=WALK  applyWay=RANGED  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1284_sgprst
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_sgprst(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='阿格尼尔神父',
        faction=Faction.ENEMY,
        max_hp=22000,
        atk=900,
        defence=500,
        res=40.0,
        atk_interval=4.5,
        move_speed=1.0,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
