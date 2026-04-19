"""投矛的士兵 — generated from ArknightsGameData enemy_10155_mntjsd level 0.
motion=WALK  applyWay=ALL  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_10155_mntjsd
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_mntjsd(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='投矛的士兵',
        faction=Faction.ENEMY,
        max_hp=4200,
        atk=360,
        defence=100,
        res=10.0,
        atk_interval=2.5,
        move_speed=0.8,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
