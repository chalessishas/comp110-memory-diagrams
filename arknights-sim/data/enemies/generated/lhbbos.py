"""“老尖牙” — generated from ArknightsGameData enemy_18008_lhbbos level 0.
motion=WALK  applyWay=MELEE  lifeReduce=3
Regenerate: python tools/gen_enemies.py enemy_18008_lhbbos
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_lhbbos(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='“老尖牙”',
        faction=Faction.ENEMY,
        max_hp=97500,
        atk=1980,
        defence=1150,
        res=85.0,
        atk_interval=2.2,
        move_speed=0.4,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
