"""帝国前锋百战精锐 — generated from ArknightsGameData enemy_1113_empace_2 level 0.
motion=WALK  applyWay=ALL  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1113_empace_2
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_2_empace(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='帝国前锋百战精锐',
        faction=Faction.ENEMY,
        max_hp=15000,
        atk=1200,
        defence=800,
        res=50.0,
        atk_interval=4.5,
        move_speed=0.7,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
