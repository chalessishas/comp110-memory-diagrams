"""大君之赐 — generated from ArknightsGameData enemy_5050_dqomg level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_5050_dqomg
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_dqomg(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='大君之赐',
        faction=Faction.ENEMY,
        max_hp=3000,
        atk=680,
        defence=200,
        res=20.0,
        atk_interval=4.0,
        move_speed=0.7,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
