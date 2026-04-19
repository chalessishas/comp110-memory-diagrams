"""双月共主 — generated from ArknightsGameData enemy_2109_dypry2 level 0.
motion=WALK  applyWay=RANGED  lifeReduce=5
Regenerate: python tools/gen_enemies.py enemy_2109_dypry2
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_dypry2(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='双月共主',
        faction=Faction.ENEMY,
        max_hp=40000,
        atk=600,
        defence=300,
        res=60.0,
        atk_interval=3.5,
        move_speed=0.7,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
