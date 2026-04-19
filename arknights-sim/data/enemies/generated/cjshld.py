"""“果腹” — generated from ArknightsGameData enemy_10052_cjshld level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_10052_cjshld
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_cjshld(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='“果腹”',
        faction=Faction.ENEMY,
        max_hp=5000,
        atk=550,
        defence=4000,
        res=90.0,
        atk_interval=3.0,
        move_speed=0.5,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
