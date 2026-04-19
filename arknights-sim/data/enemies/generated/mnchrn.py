"""赞索斯，复仇者 — generated from ArknightsGameData enemy_1580_mnchrn level 0.
motion=WALK  applyWay=MELEE  lifeReduce=2
Regenerate: python tools/gen_enemies.py enemy_1580_mnchrn
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_mnchrn(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='赞索斯，复仇者',
        faction=Faction.ENEMY,
        max_hp=90000,
        atk=1200,
        defence=800,
        res=30.0,
        atk_interval=3.6,
        move_speed=0.5,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
