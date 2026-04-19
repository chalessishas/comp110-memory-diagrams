"""多利，“羊之主” — generated from ArknightsGameData enemy_1545_shpkg level 0.
motion=WALK  applyWay=RANGED  lifeReduce=2
Regenerate: python tools/gen_enemies.py enemy_1545_shpkg
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_shpkg(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='多利，“羊之主”',
        faction=Faction.ENEMY,
        max_hp=60000,
        atk=750,
        defence=800,
        res=60.0,
        atk_interval=7.0,
        move_speed=0.35,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
