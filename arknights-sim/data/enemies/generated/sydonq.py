"""最后的骑士 — generated from ArknightsGameData enemy_2038_sydonq level 0.
motion=WALK  applyWay=MELEE  lifeReduce=30
Regenerate: python tools/gen_enemies.py enemy_2038_sydonq
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_sydonq(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='最后的骑士',
        faction=Faction.ENEMY,
        max_hp=100000,
        atk=2000,
        defence=4000,
        res=70.0,
        atk_interval=3.5,
        move_speed=0.6,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
