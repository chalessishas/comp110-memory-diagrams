"""殉亡魂灵圣杯 — generated from ArknightsGameData enemy_1430_lrrook_2 level 0.
motion=FLY  applyWay=NONE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1430_lrrook_2
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_2_lrrook(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='殉亡魂灵圣杯',
        faction=Faction.ENEMY,
        max_hp=125000,
        atk=0,
        defence=0,
        res=30.0,
        atk_interval=4.0,
        move_speed=0.5,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.AIRBORNE,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
