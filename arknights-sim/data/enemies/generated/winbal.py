"""访问团突击新兵 — generated from ArknightsGameData enemy_1382_winbal level 0.
motion=WALK  applyWay=RANGED  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1382_winbal
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_winbal(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='访问团突击新兵',
        faction=Faction.ENEMY,
        max_hp=5500,
        atk=400,
        defence=100,
        res=10.0,
        atk_interval=3.0,
        move_speed=0.7,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
