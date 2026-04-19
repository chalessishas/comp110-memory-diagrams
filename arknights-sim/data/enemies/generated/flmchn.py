"""缠身恶焰 — generated from ArknightsGameData enemy_8002_flmchn level 0.
motion=WALK  applyWay=NONE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_8002_flmchn
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_flmchn(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='缠身恶焰',
        faction=Faction.ENEMY,
        max_hp=8000,
        atk=100,
        defence=750,
        res=0.0,
        atk_interval=1.0,
        move_speed=1.0,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
