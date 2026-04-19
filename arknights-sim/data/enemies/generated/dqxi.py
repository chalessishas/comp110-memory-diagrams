"""“自在” — generated from ArknightsGameData enemy_5054_dqxi level 0.
motion=WALK  applyWay=RANGED  lifeReduce=2
Regenerate: python tools/gen_enemies.py enemy_5054_dqxi
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_dqxi(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='“自在”',
        faction=Faction.ENEMY,
        max_hp=40000,
        atk=600,
        defence=800,
        res=55.0,
        atk_interval=4.0,
        move_speed=0.5,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
