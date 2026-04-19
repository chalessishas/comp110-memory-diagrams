"""巡游草叶 — generated from ArknightsGameData enemy_10064_ftyzss level 0.
motion=WALK  applyWay=RANGED  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_10064_ftyzss
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_ftyzss(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='巡游草叶',
        faction=Faction.ENEMY,
        max_hp=6500,
        atk=500,
        defence=150,
        res=50.0,
        atk_interval=2.4,
        move_speed=0.75,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
