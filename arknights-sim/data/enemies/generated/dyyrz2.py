"""桓君 — generated from ArknightsGameData enemy_2111_dyyrz2 level 0.
motion=WALK  applyWay=MELEE  lifeReduce=3
Regenerate: python tools/gen_enemies.py enemy_2111_dyyrz2
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_dyyrz2(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='桓君',
        faction=Faction.ENEMY,
        max_hp=100000,
        atk=1000,
        defence=400,
        res=60.0,
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
