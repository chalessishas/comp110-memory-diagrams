"""引火的死魂灵 — generated from ArknightsGameData enemy_1553_lrdead level 0.
motion=WALK  applyWay=RANGED  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1553_lrdead
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_lrdead(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='引火的死魂灵',
        faction=Faction.ENEMY,
        max_hp=500000,
        atk=800,
        defence=200,
        res=50.0,
        atk_interval=3.5,
        move_speed=0.8,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
