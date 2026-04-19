"""二手廉价无人机 — generated from ArknightsGameData enemy_4002_syokai level 0.
motion=FLY  applyWay=NONE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_4002_syokai
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_syokai(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='二手廉价无人机',
        faction=Faction.ENEMY,
        max_hp=5000,
        atk=0,
        defence=100,
        res=20.0,
        atk_interval=1.0,
        move_speed=0.7,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.AIRBORNE,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
