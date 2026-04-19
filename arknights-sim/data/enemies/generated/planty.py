"""“自然的妥协” — generated from ArknightsGameData enemy_6011_planty level 0.
motion=WALK  applyWay=MELEE  lifeReduce=3
Regenerate: python tools/gen_enemies.py enemy_6011_planty
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_planty(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='“自然的妥协”',
        faction=Faction.ENEMY,
        max_hp=100000,
        atk=1000,
        defence=400,
        res=30.0,
        atk_interval=4.0,
        move_speed=0.4,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
