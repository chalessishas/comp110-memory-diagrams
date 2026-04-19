"""可汗片影 — generated from ArknightsGameData enemy_2060_smshdw level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_2060_smshdw
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_smshdw(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='可汗片影',
        faction=Faction.ENEMY,
        max_hp=4000,
        atk=700,
        defence=500,
        res=30.0,
        atk_interval=3.0,
        move_speed=1.1,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
