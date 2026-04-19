"""“米兰” — generated from ArknightsGameData enemy_6004_pleslm level 0.
motion=WALK  applyWay=MELEE  lifeReduce=3
Regenerate: python tools/gen_enemies.py enemy_6004_pleslm
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_pleslm(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='“米兰”',
        faction=Faction.ENEMY,
        max_hp=60000,
        atk=1000,
        defence=800,
        res=50.0,
        atk_interval=5.0,
        move_speed=0.5,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
