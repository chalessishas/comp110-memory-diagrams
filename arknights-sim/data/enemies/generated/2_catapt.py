"""“都应该砸” — generated from ArknightsGameData enemy_7003_catapt_2 level 0.
motion=WALK  applyWay=RANGED  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_7003_catapt_2
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_2_catapt(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='“都应该砸”',
        faction=Faction.ENEMY,
        max_hp=20000,
        atk=550,
        defence=400,
        res=0.0,
        atk_interval=5.0,
        move_speed=0.7,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
