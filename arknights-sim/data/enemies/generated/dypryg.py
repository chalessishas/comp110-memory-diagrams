"""夕娥 — generated from ArknightsGameData enemy_2108_dypryg level 0.
motion=WALK  applyWay=RANGED  lifeReduce=5
Regenerate: python tools/gen_enemies.py enemy_2108_dypryg
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_dypryg(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='夕娥',
        faction=Faction.ENEMY,
        max_hp=36000,
        atk=400,
        defence=200,
        res=60.0,
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
