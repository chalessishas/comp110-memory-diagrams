"""浪里玄条 — generated from ArknightsGameData enemy_10168_tjgly level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_10168_tjgly
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_tjgly(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='浪里玄条',
        faction=Faction.ENEMY,
        max_hp=35000,
        atk=550,
        defence=0,
        res=0.0,
        atk_interval=2.5,
        move_speed=1.2,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
