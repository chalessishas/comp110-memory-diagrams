"""Dor-1号失败品 — generated from ArknightsGameData enemy_1251_lysyta level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1251_lysyta
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_lysyta(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='Dor-1号失败品',
        faction=Faction.ENEMY,
        max_hp=2750,
        atk=310,
        defence=0,
        res=50.0,
        atk_interval=1.8,
        move_speed=1.5,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
