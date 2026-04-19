"""资深圣堂布道员 — generated from ArknightsGameData enemy_10090_hlgrd_2 level 0.
motion=WALK  applyWay=RANGED  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_10090_hlgrd_2
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_2_hlgrd(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='资深圣堂布道员',
        faction=Faction.ENEMY,
        max_hp=20000,
        atk=520,
        defence=400,
        res=30.0,
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
