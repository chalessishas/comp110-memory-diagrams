"""无忧货运帮手 — generated from ArknightsGameData enemy_10075_mpwrj level 0.
motion=FLY  applyWay=NONE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_10075_mpwrj
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_mpwrj(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='无忧货运帮手',
        faction=Faction.ENEMY,
        max_hp=2500,
        atk=1000,
        defence=200,
        res=30.0,
        atk_interval=1.0,
        move_speed=1.2,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.AIRBORNE,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
