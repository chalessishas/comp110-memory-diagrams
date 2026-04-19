"""深池狙击队长 — generated from ArknightsGameData enemy_1167_dubow_2 level 0.
motion=WALK  applyWay=RANGED  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1167_dubow_2
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_2_dubow(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='深池狙击队长',
        faction=Faction.ENEMY,
        max_hp=5000,
        atk=380,
        defence=150,
        res=0.0,
        atk_interval=2.3,
        move_speed=1.1,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
