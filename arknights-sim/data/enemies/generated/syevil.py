"""接潮主教 — generated from ArknightsGameData enemy_2028_syevil level 0.
motion=WALK  applyWay=RANGED  lifeReduce=5
Regenerate: python tools/gen_enemies.py enemy_2028_syevil
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_syevil(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='接潮主教',
        faction=Faction.ENEMY,
        max_hp=40000,
        atk=600,
        defence=300,
        res=70.0,
        atk_interval=4.5,
        move_speed=0.4,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
