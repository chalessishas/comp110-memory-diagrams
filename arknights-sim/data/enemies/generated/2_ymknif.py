"""山海众游勇 — generated from ArknightsGameData enemy_1296_ymknif_2 level 0.
motion=WALK  applyWay=RANGED  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1296_ymknif_2
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_2_ymknif(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='山海众游勇',
        faction=Faction.ENEMY,
        max_hp=6000,
        atk=480,
        defence=200,
        res=20.0,
        atk_interval=2.5,
        move_speed=0.8,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
