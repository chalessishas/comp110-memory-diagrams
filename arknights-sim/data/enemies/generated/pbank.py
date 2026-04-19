"""移动电源 — generated from ArknightsGameData enemy_4003_pbank level 0.
motion=WALK  applyWay=NONE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_4003_pbank
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_pbank(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='移动电源',
        faction=Faction.ENEMY,
        max_hp=7500,
        atk=0,
        defence=250,
        res=30.0,
        atk_interval=3.0,
        move_speed=1.9,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
