"""“皇帝的利刃”，折戟者 — generated from ArknightsGameData enemy_3011_dyegrd level 0.
motion=WALK  applyWay=ALL  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_3011_dyegrd
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_dyegrd(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='“皇帝的利刃”，折戟者',
        faction=Faction.ENEMY,
        max_hp=40000,
        atk=1200,
        defence=500,
        res=40.0,
        atk_interval=4.0,
        move_speed=0.5,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
