"""“皇帝的利刃” — generated from ArknightsGameData enemy_1115_embald level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1115_embald
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_embald(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='“皇帝的利刃”',
        faction=Faction.ENEMY,
        max_hp=50000,
        atk=0,
        defence=3000,
        res=90.0,
        atk_interval=1.0,
        move_speed=0.4,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
