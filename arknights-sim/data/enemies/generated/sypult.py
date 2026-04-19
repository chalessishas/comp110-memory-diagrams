"""投嗣育母 — generated from ArknightsGameData enemy_2023_sypult level 0.
motion=WALK  applyWay=RANGED  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_2023_sypult
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_sypult(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='投嗣育母',
        faction=Faction.ENEMY,
        max_hp=16000,
        atk=600,
        defence=600,
        res=10.0,
        atk_interval=8.0,
        move_speed=0.4,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
