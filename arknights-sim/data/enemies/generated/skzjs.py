"""恐卡兹 — generated from ArknightsGameData enemy_2065_skzjs level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_2065_skzjs
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_skzjs(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='恐卡兹',
        faction=Faction.ENEMY,
        max_hp=15000,
        atk=800,
        defence=350,
        res=50.0,
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
