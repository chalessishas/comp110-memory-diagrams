"""湮没之口 — generated from ArknightsGameData enemy_10063_cjdoor level 0.
motion=WALK  applyWay=NONE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_10063_cjdoor
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_cjdoor(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='湮没之口',
        faction=Faction.ENEMY,
        max_hp=25000,
        atk=330,
        defence=100,
        res=10.0,
        atk_interval=2.0,
        move_speed=0.9,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
