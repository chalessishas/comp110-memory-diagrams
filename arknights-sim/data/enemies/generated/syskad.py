"""伊莎玛拉，腐化之心 — generated from ArknightsGameData enemy_2039_syskad level 0.
motion=WALK  applyWay=RANGED  lifeReduce=30
Regenerate: python tools/gen_enemies.py enemy_2039_syskad
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_syskad(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='伊莎玛拉，腐化之心',
        faction=Faction.ENEMY,
        max_hp=90000,
        atk=1600,
        defence=1200,
        res=70.0,
        atk_interval=6.0,
        move_speed=0.6,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
