"""深池重甲卫士 — generated from ArknightsGameData enemy_1170_dushld level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1170_dushld
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_dushld(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='深池重甲卫士',
        faction=Faction.ENEMY,
        max_hp=7000,
        atk=700,
        defence=750,
        res=0.0,
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
