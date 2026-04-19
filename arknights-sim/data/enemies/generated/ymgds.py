"""冒失的小弟 — generated from ArknightsGameData enemy_10112_ymgds level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_10112_ymgds
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_ymgds(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='冒失的小弟',
        faction=Faction.ENEMY,
        max_hp=5000,
        atk=500,
        defence=80,
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
