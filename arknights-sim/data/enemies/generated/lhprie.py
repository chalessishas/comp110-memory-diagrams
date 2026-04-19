"""恩慈祷者 — generated from ArknightsGameData enemy_18006_lhprie level 0.
motion=WALK  applyWay=RANGED  lifeReduce=3
Regenerate: python tools/gen_enemies.py enemy_18006_lhprie
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_lhprie(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='恩慈祷者',
        faction=Faction.ENEMY,
        max_hp=68000,
        atk=750,
        defence=400,
        res=65.0,
        atk_interval=4.2,
        move_speed=0.5,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
