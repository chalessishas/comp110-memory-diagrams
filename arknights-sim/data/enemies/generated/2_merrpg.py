"""反装甲步兵组长 — generated from ArknightsGameData enemy_1143_merrpg_2 level 0.
motion=WALK  applyWay=ALL  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1143_merrpg_2
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_2_merrpg(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='反装甲步兵组长',
        faction=Faction.ENEMY,
        max_hp=4800,
        atk=750,
        defence=50,
        res=40.0,
        atk_interval=2.6,
        move_speed=0.9,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
