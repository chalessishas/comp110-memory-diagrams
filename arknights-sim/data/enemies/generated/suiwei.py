"""岁·尾 — generated from ArknightsGameData enemy_1585_suiwei level 0.
motion=WALK  applyWay=NONE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1585_suiwei
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_suiwei(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='岁·尾',
        faction=Faction.ENEMY,
        max_hp=300000,
        atk=800,
        defence=2000,
        res=60.0,
        atk_interval=0.3,
        move_speed=1.0,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
