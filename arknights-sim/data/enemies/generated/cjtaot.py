"""无餍 — generated from ArknightsGameData enemy_1562_cjtaot level 0.
motion=WALK  applyWay=ALL  lifeReduce=2
Regenerate: python tools/gen_enemies.py enemy_1562_cjtaot
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_cjtaot(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='无餍',
        faction=Faction.ENEMY,
        max_hp=45000,
        atk=900,
        defence=500,
        res=40.0,
        atk_interval=4.0,
        move_speed=0.45,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
