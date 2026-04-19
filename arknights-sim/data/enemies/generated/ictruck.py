"""“超甜微笑” — generated from ArknightsGameData enemy_6015_ictruck level 0.
motion=WALK  applyWay=MELEE  lifeReduce=2
Regenerate: python tools/gen_enemies.py enemy_6015_ictruck
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_ictruck(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='“超甜微笑”',
        faction=Faction.ENEMY,
        max_hp=80000,
        atk=1100,
        defence=1400,
        res=60.0,
        atk_interval=5.0,
        move_speed=1.3,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
