"""“物欲拮抗者” — generated from ArknightsGameData enemy_1532_minima level 0.
motion=FLY  applyWay=RANGED  lifeReduce=2
Regenerate: python tools/gen_enemies.py enemy_1532_minima
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_minima(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='“物欲拮抗者”',
        faction=Faction.ENEMY,
        max_hp=55000,
        atk=500,
        defence=600,
        res=50.0,
        atk_interval=5.0,
        move_speed=0.5,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.AIRBORNE,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
