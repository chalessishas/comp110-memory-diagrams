"""街头乐队鼓手 — generated from ArknightsGameData enemy_15064_dqdru level 0.
motion=WALK  applyWay=RANGED  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_15064_dqdru
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_dqdru(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='街头乐队鼓手',
        faction=Faction.ENEMY,
        max_hp=10000,
        atk=250,
        defence=250,
        res=50.0,
        atk_interval=1.8,
        move_speed=0.7,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
