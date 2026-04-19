"""思旧 — generated from ArknightsGameData enemy_10057_cjstel level 0.
motion=WALK  applyWay=RANGED  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_10057_cjstel
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_cjstel(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='思旧',
        faction=Faction.ENEMY,
        max_hp=25000,
        atk=350,
        defence=50,
        res=25.0,
        atk_interval=3.0,
        move_speed=1.0,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
