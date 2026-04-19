"""高阶术师 — generated from ArknightsGameData enemy_1018_aoemag level 0.
motion=WALK  applyWay=RANGED  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1018_aoemag
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_aoemag(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='高阶术师',
        faction=Faction.ENEMY,
        max_hp=7000,
        atk=240,
        defence=120,
        res=50.0,
        atk_interval=3.8,
        move_speed=0.7,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
