"""访问团术师长 — generated from ArknightsGameData enemy_1386_winmag_2 level 0.
motion=WALK  applyWay=RANGED  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1386_winmag_2
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_2_winmag(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='访问团术师长',
        faction=Faction.ENEMY,
        max_hp=8000,
        atk=600,
        defence=350,
        res=70.0,
        atk_interval=4.0,
        move_speed=0.7,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
