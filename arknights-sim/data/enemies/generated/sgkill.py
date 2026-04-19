"""家族灭迹人 — generated from ArknightsGameData enemy_1283_sgkill level 0.
motion=WALK  applyWay=RANGED  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1283_sgkill
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_sgkill(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='家族灭迹人',
        faction=Faction.ENEMY,
        max_hp=12000,
        atk=800,
        defence=800,
        res=45.0,
        atk_interval=3.0,
        move_speed=0.9,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
