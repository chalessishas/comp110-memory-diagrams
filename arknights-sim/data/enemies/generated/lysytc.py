"""Dor-3号改造体 — generated from ArknightsGameData enemy_1253_lysytc level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1253_lysytc
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_lysytc(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='Dor-3号改造体',
        faction=Faction.ENEMY,
        max_hp=5000,
        atk=500,
        defence=1000,
        res=50.0,
        atk_interval=3.0,
        move_speed=0.8,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
