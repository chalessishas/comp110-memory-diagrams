"""“偏执泡影” — generated from ArknightsGameData enemy_2037_sygirl level 0.
motion=WALK  applyWay=RANGED  lifeReduce=30
Regenerate: python tools/gen_enemies.py enemy_2037_sygirl
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_sygirl(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='“偏执泡影”',
        faction=Faction.ENEMY,
        max_hp=45000,
        atk=500,
        defence=700,
        res=70.0,
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
