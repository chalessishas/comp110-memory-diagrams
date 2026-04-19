"""匪帮射手 — generated from ArknightsGameData enemy_1356_egun level 0.
motion=WALK  applyWay=RANGED  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1356_egun
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_egun(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='匪帮射手',
        faction=Faction.ENEMY,
        max_hp=9000,
        atk=200,
        defence=80,
        res=10.0,
        atk_interval=3.0,
        move_speed=0.7,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
