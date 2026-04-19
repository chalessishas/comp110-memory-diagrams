"""锈锤战士 — generated from ArknightsGameData enemy_2006_flsnip level 0.
motion=WALK  applyWay=RANGED  lifeReduce=30
Regenerate: python tools/gen_enemies.py enemy_2006_flsnip
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_flsnip(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='锈锤战士',
        faction=Faction.ENEMY,
        max_hp=40000,
        atk=1200,
        defence=550,
        res=40.0,
        atk_interval=5.0,
        move_speed=0.4,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
