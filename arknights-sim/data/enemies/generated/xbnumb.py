"""放归驮兽（圈养） — generated from ArknightsGameData enemy_7050_xbnumb level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_7050_xbnumb
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_xbnumb(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='放归驮兽（圈养）',
        faction=Faction.ENEMY,
        max_hp=40000,
        atk=1800,
        defence=0,
        res=0.0,
        atk_interval=5.0,
        move_speed=0.6,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
