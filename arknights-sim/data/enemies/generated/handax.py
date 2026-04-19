"""伐木机 — generated from ArknightsGameData enemy_1033_handax level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1033_handax
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_handax(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='伐木机',
        faction=Faction.ENEMY,
        max_hp=8000,
        atk=750,
        defence=80,
        res=30.0,
        atk_interval=3.3,
        move_speed=0.75,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
