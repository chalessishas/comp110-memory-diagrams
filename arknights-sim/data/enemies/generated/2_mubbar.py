"""“举重王”深水大力士 — generated from ArknightsGameData enemy_4050_mubbar_2 level 0.
motion=WALK  applyWay=ALL  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_4050_mubbar_2
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_2_mubbar(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='“举重王”深水大力士',
        faction=Faction.ENEMY,
        max_hp=32000,
        atk=680,
        defence=1200,
        res=0.0,
        atk_interval=6.0,
        move_speed=0.8,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
