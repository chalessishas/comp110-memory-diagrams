"""坍缩构造体 — generated from ArknightsGameData enemy_2045_smdrn level 0.
motion=FLY  applyWay=RANGED  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_2045_smdrn
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_smdrn(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='坍缩构造体',
        faction=Faction.ENEMY,
        max_hp=3500,
        atk=200,
        defence=100,
        res=65.0,
        atk_interval=2.0,
        move_speed=2.0,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.AIRBORNE,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
