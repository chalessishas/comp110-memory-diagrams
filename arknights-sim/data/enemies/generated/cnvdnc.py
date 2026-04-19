"""热烈舞团独舞者 — generated from ArknightsGameData enemy_10035_cnvdnc level 0.
motion=WALK  applyWay=RANGED  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_10035_cnvdnc
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_cnvdnc(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='热烈舞团独舞者',
        faction=Faction.ENEMY,
        max_hp=12000,
        atk=100,
        defence=300,
        res=10.0,
        atk_interval=1.0,
        move_speed=0.7,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
