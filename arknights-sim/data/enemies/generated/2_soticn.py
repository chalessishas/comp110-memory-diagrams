"""游击队迫击炮兵组长 — generated from ArknightsGameData enemy_1082_soticn_2 level 0.
motion=WALK  applyWay=RANGED  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1082_soticn_2
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_2_soticn(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='游击队迫击炮兵组长',
        faction=Faction.ENEMY,
        max_hp=6500,
        atk=590,
        defence=550,
        res=20.0,
        atk_interval=4.8,
        move_speed=0.6,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
