"""战争幽灵 — generated from ArknightsGameData enemy_1144_merlgd level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1144_merlgd
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_merlgd(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='战争幽灵',
        faction=Faction.ENEMY,
        max_hp=10000,
        atk=1100,
        defence=500,
        res=60.0,
        atk_interval=3.0,
        move_speed=1.2,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
