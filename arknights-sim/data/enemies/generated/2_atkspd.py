"""破片U型 — generated from ArknightsGameData enemy_1145_atkspd_2 level 0.
motion=FLY  applyWay=RANGED  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1145_atkspd_2
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_2_atkspd(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='破片U型',
        faction=Faction.ENEMY,
        max_hp=8000,
        atk=350,
        defence=80,
        res=50.0,
        atk_interval=3.8,
        move_speed=1.0,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.AIRBORNE,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
