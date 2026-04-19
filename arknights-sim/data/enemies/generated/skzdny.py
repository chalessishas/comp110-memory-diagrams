"""菈玛莲 — generated from ArknightsGameData enemy_2071_skzdny level 0.
motion=WALK  applyWay=RANGED  lifeReduce=5
Regenerate: python tools/gen_enemies.py enemy_2071_skzdny
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_skzdny(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='菈玛莲',
        faction=Faction.ENEMY,
        max_hp=55000,
        atk=900,
        defence=500,
        res=70.0,
        atk_interval=3.9,
        move_speed=0.5,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
