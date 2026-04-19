"""曼弗雷德 — generated from ArknightsGameData enemy_1528_manfri level 0.
motion=WALK  applyWay=RANGED  lifeReduce=2
Regenerate: python tools/gen_enemies.py enemy_1528_manfri
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_manfri(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='曼弗雷德',
        faction=Faction.ENEMY,
        max_hp=40000,
        atk=1000,
        defence=600,
        res=40.0,
        atk_interval=5.0,
        move_speed=0.5,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
