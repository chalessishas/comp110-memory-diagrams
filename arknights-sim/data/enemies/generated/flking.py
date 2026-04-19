"""“墓碑” — generated from ArknightsGameData enemy_2008_flking level 0.
motion=WALK  applyWay=ALL  lifeReduce=30
Regenerate: python tools/gen_enemies.py enemy_2008_flking
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_flking(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='“墓碑”',
        faction=Faction.ENEMY,
        max_hp=60000,
        atk=2000,
        defence=330,
        res=55.0,
        atk_interval=3.5,
        move_speed=0.5,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
