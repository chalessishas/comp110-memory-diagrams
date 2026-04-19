"""身形 — generated from ArknightsGameData enemy_2128_dysuib level 0.
motion=WALK  applyWay=NONE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_2128_dysuib
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_dysuib(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='身形',
        faction=Faction.ENEMY,
        max_hp=80000,
        atk=200,
        defence=1000,
        res=30.0,
        atk_interval=5.0,
        move_speed=0.6,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
