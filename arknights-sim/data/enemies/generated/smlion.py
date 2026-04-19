"""路加萨尔古斯，历法之王 — generated from ArknightsGameData enemy_2058_smlion level 0.
motion=WALK  applyWay=RANGED  lifeReduce=30
Regenerate: python tools/gen_enemies.py enemy_2058_smlion
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_smlion(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='路加萨尔古斯，历法之王',
        faction=Faction.ENEMY,
        max_hp=180000,
        atk=1000,
        defence=1000,
        res=90.0,
        atk_interval=4.0,
        move_speed=0.6,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
