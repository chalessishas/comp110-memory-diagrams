"""隐形术师组长 — generated from ArknightsGameData enemy_1023_jmage_2 level 0.
motion=WALK  applyWay=RANGED  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1023_jmage_2
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_2_jmage(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='隐形术师组长',
        faction=Faction.ENEMY,
        max_hp=4200,
        atk=400,
        defence=130,
        res=50.0,
        atk_interval=4.0,
        move_speed=0.8,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
