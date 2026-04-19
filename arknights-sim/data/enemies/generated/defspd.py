"""铁砧 — generated from ArknightsGameData enemy_1146_defspd level 0.
motion=FLY  applyWay=NONE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1146_defspd
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_defspd(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='铁砧',
        faction=Faction.ENEMY,
        max_hp=5000,
        atk=0,
        defence=80,
        res=50.0,
        atk_interval=1.0,
        move_speed=1.0,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.AIRBORNE,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
