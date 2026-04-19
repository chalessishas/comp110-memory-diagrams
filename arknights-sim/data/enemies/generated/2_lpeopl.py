"""修道院居民 — generated from ArknightsGameData enemy_3005_lpeopl_2 level 0.
motion=FLY  applyWay=NONE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_3005_lpeopl_2
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_2_lpeopl(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='修道院居民',
        faction=Faction.ENEMY,
        max_hp=5000,
        atk=0,
        defence=50,
        res=0.0,
        atk_interval=1.0,
        move_speed=0.65,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.AIRBORNE,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
