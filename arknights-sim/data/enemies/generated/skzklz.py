"""凯尔希 — generated from ArknightsGameData enemy_2076_skzklz level 0.
motion=WALK  applyWay=MELEE  lifeReduce=5
Regenerate: python tools/gen_enemies.py enemy_2076_skzklz
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_skzklz(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='凯尔希',
        faction=Faction.ENEMY,
        max_hp=50000,
        atk=1000,
        defence=500,
        res=50.0,
        atk_interval=2.0,
        move_speed=0.39,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
