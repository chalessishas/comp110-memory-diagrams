"""畸变体傀儡 — generated from ArknightsGameData enemy_1130_infstr level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1130_infstr
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_infstr(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='畸变体傀儡',
        faction=Faction.ENEMY,
        max_hp=1900,
        atk=210,
        defence=100,
        res=0.0,
        atk_interval=2.0,
        move_speed=0.9,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
