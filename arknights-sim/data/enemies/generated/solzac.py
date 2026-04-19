"""“晨音” — generated from ArknightsGameData enemy_6029_solzac level 0.
motion=WALK  applyWay=RANGED  lifeReduce=3
Regenerate: python tools/gen_enemies.py enemy_6029_solzac
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_solzac(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='“晨音”',
        faction=Faction.ENEMY,
        max_hp=60000,
        atk=800,
        defence=700,
        res=40.0,
        atk_interval=6.0,
        move_speed=0.3,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
