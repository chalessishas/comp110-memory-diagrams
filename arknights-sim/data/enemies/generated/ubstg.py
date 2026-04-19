"""被关押的学生 — generated from ArknightsGameData enemy_3016_ubstg level 0.
motion=WALK  applyWay=NONE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_3016_ubstg
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_ubstg(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='被关押的学生',
        faction=Faction.ENEMY,
        max_hp=1000,
        atk=100,
        defence=100,
        res=0.0,
        atk_interval=10.0,
        move_speed=0.75,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
