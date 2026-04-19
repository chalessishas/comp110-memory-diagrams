"""古老藤蔓 — generated from ArknightsGameData enemy_2053_smgia2 level 0.
motion=WALK  applyWay=MELEE  lifeReduce=5
Regenerate: python tools/gen_enemies.py enemy_2053_smgia2
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_smgia2(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='古老藤蔓',
        faction=Faction.ENEMY,
        max_hp=100000,
        atk=1200,
        defence=1200,
        res=40.0,
        atk_interval=2.5,
        move_speed=0.5,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
