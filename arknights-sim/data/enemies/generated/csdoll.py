"""伤心的大锁 — generated from ArknightsGameData enemy_2018_csdoll level 0.
motion=WALK  applyWay=RANGED  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_2018_csdoll
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_csdoll(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='伤心的大锁',
        faction=Faction.ENEMY,
        max_hp=300000,
        atk=800,
        defence=700,
        res=60.0,
        atk_interval=4.0,
        move_speed=0.1,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
