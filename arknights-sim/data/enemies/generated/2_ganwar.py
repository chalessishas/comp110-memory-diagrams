"""精干打手 — generated from ArknightsGameData enemy_1056_ganwar_2 level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1056_ganwar_2
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_2_ganwar(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='精干打手',
        faction=Faction.ENEMY,
        max_hp=4200,
        atk=380,
        defence=300,
        res=0.0,
        atk_interval=0.4,
        move_speed=0.95,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
