"""掀天汽水桶 — generated from ArknightsGameData enemy_10149_nscan level 0.
motion=FLY  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_10149_nscan
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_nscan(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='掀天汽水桶',
        faction=Faction.ENEMY,
        max_hp=11000,
        atk=550,
        defence=400,
        res=10.0,
        atk_interval=3.5,
        move_speed=0.3,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.AIRBORNE,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
