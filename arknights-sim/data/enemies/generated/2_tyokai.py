"""豪华赞助无人机 — generated from ArknightsGameData enemy_1105_tyokai_2 level 0.
motion=FLY  applyWay=NONE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1105_tyokai_2
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_2_tyokai(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='豪华赞助无人机',
        faction=Faction.ENEMY,
        max_hp=10000,
        atk=0,
        defence=300,
        res=40.0,
        atk_interval=1.0,
        move_speed=0.5,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.AIRBORNE,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
