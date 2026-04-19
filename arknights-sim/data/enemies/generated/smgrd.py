"""“邪魔的利刃” — generated from ArknightsGameData enemy_2048_smgrd level 0.
motion=WALK  applyWay=RANGED  lifeReduce=5
Regenerate: python tools/gen_enemies.py enemy_2048_smgrd
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_smgrd(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='“邪魔的利刃”',
        faction=Faction.ENEMY,
        max_hp=50000,
        atk=800,
        defence=300,
        res=30.0,
        atk_interval=4.0,
        move_speed=0.6,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
