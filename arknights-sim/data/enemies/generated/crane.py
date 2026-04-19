"""“贪婪捕手” — generated from ArknightsGameData enemy_6023_crane level 0.
motion=WALK  applyWay=RANGED  lifeReduce=3
Regenerate: python tools/gen_enemies.py enemy_6023_crane
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_crane(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='“贪婪捕手”',
        faction=Faction.ENEMY,
        max_hp=90000,
        atk=650,
        defence=1500,
        res=20.0,
        atk_interval=5.0,
        move_speed=0.6,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
