"""宣泄暴力的摄影师 — generated from ArknightsGameData enemy_10101_crgun_2 level 0.
motion=WALK  applyWay=ALL  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_10101_crgun_2
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_2_crgun(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='宣泄暴力的摄影师',
        faction=Faction.ENEMY,
        max_hp=45000,
        atk=1400,
        defence=300,
        res=40.0,
        atk_interval=5.0,
        move_speed=0.6,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
