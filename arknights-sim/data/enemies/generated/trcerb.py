"""“三头犬” — generated from ArknightsGameData enemy_1557_trcerb level 0.
motion=WALK  applyWay=ALL  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1557_trcerb
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_trcerb(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='“三头犬”',
        faction=Faction.ENEMY,
        max_hp=30000,
        atk=1000,
        defence=600,
        res=30.0,
        atk_interval=5.0,
        move_speed=0.4,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
