"""玩耍的卡尔顿 — generated from ArknightsGameData enemy_10106_mjcbat level 0.
motion=FLY  applyWay=RANGED  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_10106_mjcbat
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_mjcbat(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='玩耍的卡尔顿',
        faction=Faction.ENEMY,
        max_hp=3000,
        atk=70,
        defence=200,
        res=35.0,
        atk_interval=0.4,
        move_speed=0.3,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.AIRBORNE,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
