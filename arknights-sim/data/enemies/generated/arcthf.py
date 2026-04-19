"""宝藏神偷 — generated from ArknightsGameData enemy_5502_arcthf level 0.
motion=WALK  applyWay=NONE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_5502_arcthf
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_arcthf(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='宝藏神偷',
        faction=Faction.ENEMY,
        max_hp=18000,
        atk=0,
        defence=50,
        res=0.0,
        atk_interval=10.0,
        move_speed=1.0,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
