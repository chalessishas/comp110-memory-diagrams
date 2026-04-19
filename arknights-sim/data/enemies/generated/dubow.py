"""深池狙击手 — generated from ArknightsGameData enemy_1167_dubow level 0.
motion=WALK  applyWay=RANGED  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1167_dubow
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_dubow(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='深池狙击手',
        faction=Faction.ENEMY,
        max_hp=3800,
        atk=250,
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
