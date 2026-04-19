"""“织郁伯爵” — generated from ArknightsGameData enemy_6022_m2cnt level 0.
motion=WALK  applyWay=MELEE  lifeReduce=3
Regenerate: python tools/gen_enemies.py enemy_6022_m2cnt
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_m2cnt(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='“织郁伯爵”',
        faction=Faction.ENEMY,
        max_hp=90000,
        atk=750,
        defence=300,
        res=60.0,
        atk_interval=6.0,
        move_speed=0.45,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
