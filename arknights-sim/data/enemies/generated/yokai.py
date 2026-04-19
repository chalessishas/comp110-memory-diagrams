"""妖怪 — generated from ArknightsGameData enemy_1005_yokai level 0.
motion=FLY  applyWay=NONE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1005_yokai
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_yokai(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='妖怪',
        faction=Faction.ENEMY,
        max_hp=800,
        atk=0,
        defence=50,
        res=0.0,
        atk_interval=2.3,
        move_speed=0.9,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.AIRBORNE,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
