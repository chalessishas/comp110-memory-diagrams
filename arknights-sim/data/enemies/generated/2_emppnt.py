"""帝国炮火中枢先兆者 — generated from ArknightsGameData enemy_1112_emppnt_2 level 0.
motion=FLY  applyWay=RANGED  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1112_emppnt_2
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_2_emppnt(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='帝国炮火中枢先兆者',
        faction=Faction.ENEMY,
        max_hp=16000,
        atk=1200,
        defence=800,
        res=50.0,
        atk_interval=5.0,
        move_speed=0.5,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.AIRBORNE,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
