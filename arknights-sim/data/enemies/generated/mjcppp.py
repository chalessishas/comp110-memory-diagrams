"""浅睡的臼齿 — generated from ArknightsGameData enemy_10103_mjcppp level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_10103_mjcppp
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_mjcppp(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='浅睡的臼齿',
        faction=Faction.ENEMY,
        max_hp=3000,
        atk=300,
        defence=120,
        res=5.0,
        atk_interval=1.5,
        move_speed=0.3,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
