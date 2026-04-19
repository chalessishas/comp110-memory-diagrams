"""战场观测炮手 — generated from ArknightsGameData enemy_1408_scotcn level 0.
motion=WALK  applyWay=RANGED  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1408_scotcn
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_scotcn(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='战场观测炮手',
        faction=Faction.ENEMY,
        max_hp=8000,
        atk=400,
        defence=450,
        res=20.0,
        atk_interval=4.5,
        move_speed=0.6,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
