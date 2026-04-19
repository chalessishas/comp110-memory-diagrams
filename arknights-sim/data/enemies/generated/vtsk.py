"""“帝国的甲胄” — generated from ArknightsGameData enemy_10027_vtsk level 0.
motion=WALK  applyWay=ALL  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_10027_vtsk
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_vtsk(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='“帝国的甲胄”',
        faction=Faction.ENEMY,
        max_hp=30000,
        atk=1020,
        defence=1800,
        res=5.0,
        atk_interval=5.0,
        move_speed=0.5,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
