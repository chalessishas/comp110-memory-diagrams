"""斑斓虫 — generated from ArknightsGameData enemy_18007_lhbque level 0.
motion=WALK  applyWay=RANGED  lifeReduce=3
Regenerate: python tools/gen_enemies.py enemy_18007_lhbque
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_lhbque(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='斑斓虫',
        faction=Faction.ENEMY,
        max_hp=138000,
        atk=950,
        defence=0,
        res=70.0,
        atk_interval=7.3,
        move_speed=0.3,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
