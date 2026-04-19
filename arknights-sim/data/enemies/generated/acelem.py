"""假想敌：淤困 — generated from ArknightsGameData enemy_9007_acelem level 0.
motion=WALK  applyWay=NONE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_9007_acelem
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_acelem(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='假想敌：淤困',
        faction=Faction.ENEMY,
        max_hp=36000,
        atk=600,
        defence=200,
        res=40.0,
        atk_interval=1.0,
        move_speed=0.5,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
