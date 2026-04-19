"""坚冰AS.T — generated from ArknightsGameData enemy_1188_krgdrn_2 level 0.
motion=FLY  applyWay=RANGED  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1188_krgdrn_2
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_2_krgdrn(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='坚冰AS.T',
        faction=Faction.ENEMY,
        max_hp=7000,
        atk=350,
        defence=150,
        res=20.0,
        atk_interval=3.0,
        move_speed=0.7,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.AIRBORNE,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
