"""潜水员 — generated from ArknightsGameData enemy_1158_divman level 0.
motion=WALK  applyWay=RANGED  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1158_divman
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_divman(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='潜水员',
        faction=Faction.ENEMY,
        max_hp=3300,
        atk=240,
        defence=150,
        res=20.0,
        atk_interval=2.7,
        move_speed=0.9,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
