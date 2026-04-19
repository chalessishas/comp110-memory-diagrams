"""“花匠” — generated from ArknightsGameData enemy_1544_cledub level 0.
motion=WALK  applyWay=NONE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1544_cledub
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_cledub(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='“花匠”',
        faction=Faction.ENEMY,
        max_hp=800,
        atk=100,
        defence=0,
        res=0.0,
        atk_interval=1.0,
        move_speed=0.5,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
