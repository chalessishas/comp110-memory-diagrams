"""“复仇者” — generated from ArknightsGameData enemy_1539_reid level 0.
motion=WALK  applyWay=MELEE  lifeReduce=2
Regenerate: python tools/gen_enemies.py enemy_1539_reid
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_reid(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='“复仇者”',
        faction=Faction.ENEMY,
        max_hp=23000,
        atk=800,
        defence=650,
        res=60.0,
        atk_interval=3.0,
        move_speed=0.65,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
