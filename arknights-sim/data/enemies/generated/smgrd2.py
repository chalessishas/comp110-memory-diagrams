"""“邪魔的利刃”，游荡者 — generated from ArknightsGameData enemy_2049_smgrd2 level 0.
motion=WALK  applyWay=RANGED  lifeReduce=5
Regenerate: python tools/gen_enemies.py enemy_2049_smgrd2
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_smgrd2(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='“邪魔的利刃”，游荡者',
        faction=Faction.ENEMY,
        max_hp=60000,
        atk=800,
        defence=300,
        res=30.0,
        atk_interval=4.0,
        move_speed=0.4,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
