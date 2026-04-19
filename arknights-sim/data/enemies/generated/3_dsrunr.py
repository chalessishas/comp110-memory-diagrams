"""猎食者的墓碑 — generated from ArknightsGameData enemy_1231_dsrunr_3 level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1231_dsrunr_3
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_3_dsrunr(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='猎食者的墓碑',
        faction=Faction.ENEMY,
        max_hp=100,
        atk=100,
        defence=0,
        res=0.0,
        atk_interval=1.0,
        move_speed=1.0,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
