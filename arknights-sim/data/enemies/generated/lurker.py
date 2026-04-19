"""潜伏者 — generated from ArknightsGameData enemy_1009_lurker level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1009_lurker
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_lurker(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='潜伏者',
        faction=Faction.ENEMY,
        max_hp=2200,
        atk=300,
        defence=90,
        res=20.0,
        atk_interval=2.0,
        move_speed=1.0,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
