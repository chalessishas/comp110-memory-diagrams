"""Mon2tr — generated from ArknightsGameData enemy_2078_skzmst level 0.
motion=WALK  applyWay=MELEE  lifeReduce=5
Regenerate: python tools/gen_enemies.py enemy_2078_skzmst
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_skzmst(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='Mon2tr',
        faction=Faction.ENEMY,
        max_hp=50000,
        atk=800,
        defence=1000,
        res=0.0,
        atk_interval=5.0,
        move_speed=0.39,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
