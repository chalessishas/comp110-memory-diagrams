"""梁 — generated from ArknightsGameData enemy_2122_dybgzd level 0.
motion=FLY  applyWay=NONE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_2122_dybgzd
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_dybgzd(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='梁',
        faction=Faction.ENEMY,
        max_hp=10,
        atk=800,
        defence=400,
        res=20.0,
        atk_interval=2.0,
        move_speed=1.2,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.AIRBORNE,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
