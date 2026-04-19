"""墨浪 — generated from ArknightsGameData enemy_1201_sfzhi level 0.
motion=WALK  applyWay=RANGED  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1201_sfzhi
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_sfzhi(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='墨浪',
        faction=Faction.ENEMY,
        max_hp=6000,
        atk=400,
        defence=400,
        res=30.0,
        atk_interval=2.2,
        move_speed=0.8,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
