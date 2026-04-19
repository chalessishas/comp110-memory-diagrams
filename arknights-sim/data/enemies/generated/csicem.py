"""“霜牡” — generated from ArknightsGameData enemy_2015_csicem level 0.
motion=WALK  applyWay=MELEE  lifeReduce=3
Regenerate: python tools/gen_enemies.py enemy_2015_csicem
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_csicem(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='“霜牡”',
        faction=Faction.ENEMY,
        max_hp=60000,
        atk=1200,
        defence=300,
        res=30.0,
        atk_interval=6.0,
        move_speed=0.6,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
