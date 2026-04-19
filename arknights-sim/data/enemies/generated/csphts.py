"""不祥幻影 — generated from ArknightsGameData enemy_2017_csphts level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_2017_csphts
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_csphts(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='不祥幻影',
        faction=Faction.ENEMY,
        max_hp=10000,
        atk=750,
        defence=400,
        res=20.0,
        atk_interval=3.0,
        move_speed=0.6,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
