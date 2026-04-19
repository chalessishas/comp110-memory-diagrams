"""“独轮车玩具” — generated from ArknightsGameData enemy_10018_sgrobh level 0.
motion=WALK  applyWay=RANGED  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_10018_sgrobh
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_sgrobh(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='“独轮车玩具”',
        faction=Faction.ENEMY,
        max_hp=7500,
        atk=450,
        defence=280,
        res=50.0,
        atk_interval=4.5,
        move_speed=0.7,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
