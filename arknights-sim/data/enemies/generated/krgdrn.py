"""坚冰 — generated from ArknightsGameData enemy_1188_krgdrn level 0.
motion=FLY  applyWay=RANGED  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1188_krgdrn
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_krgdrn(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='坚冰',
        faction=Faction.ENEMY,
        max_hp=5000,
        atk=300,
        defence=100,
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
