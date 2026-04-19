"""运输汽艇 — generated from ArknightsGameData enemy_18001_lhship level 0.
motion=FLY  applyWay=NONE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_18001_lhship
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_lhship(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='运输汽艇',
        faction=Faction.ENEMY,
        max_hp=5500,
        atk=100,
        defence=100,
        res=0.0,
        atk_interval=1.0,
        move_speed=0.5,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.AIRBORNE,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
