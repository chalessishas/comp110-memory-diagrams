"""凋零骑士 — generated from ArknightsGameData enemy_1513_dekght_2 level 0.
motion=WALK  applyWay=RANGED  lifeReduce=2
Regenerate: python tools/gen_enemies.py enemy_1513_dekght_2
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_2_dekght(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='凋零骑士',
        faction=Faction.ENEMY,
        max_hp=40000,
        atk=500,
        defence=600,
        res=70.0,
        atk_interval=4.0,
        move_speed=0.65,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
