"""W — generated from ArknightsGameData enemy_1504_cqbw level 0.
motion=WALK  applyWay=RANGED  lifeReduce=2
Regenerate: python tools/gen_enemies.py enemy_1504_cqbw
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_cqbw(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='W',
        faction=Faction.ENEMY,
        max_hp=10000,
        atk=470,
        defence=100,
        res=50.0,
        atk_interval=4.0,
        move_speed=1.2,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
