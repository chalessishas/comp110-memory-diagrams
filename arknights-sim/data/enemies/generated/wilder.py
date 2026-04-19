"""无阻冲锋官 — generated from ArknightsGameData enemy_7012_wilder level 0.
motion=WALK  applyWay=MELEE  lifeReduce=30
Regenerate: python tools/gen_enemies.py enemy_7012_wilder
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_wilder(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='无阻冲锋官',
        faction=Faction.ENEMY,
        max_hp=700000,
        atk=1100,
        defence=400,
        res=10.0,
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
