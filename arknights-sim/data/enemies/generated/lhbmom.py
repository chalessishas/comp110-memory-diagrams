"""巨锹虫 — generated from ArknightsGameData enemy_18004_lhbmom level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_18004_lhbmom
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_lhbmom(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='巨锹虫',
        faction=Faction.ENEMY,
        max_hp=23500,
        atk=1250,
        defence=1050,
        res=10.0,
        atk_interval=5.5,
        move_speed=0.4,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
