"""“Misery”，静默之刃 — generated from ArknightsGameData enemy_8016_misery level 0.
motion=WALK  applyWay=ALL  lifeReduce=5
Regenerate: python tools/gen_enemies.py enemy_8016_misery
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_misery(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='“Misery”，静默之刃',
        faction=Faction.ENEMY,
        max_hp=60000,
        atk=1500,
        defence=700,
        res=20.0,
        atk_interval=2.0,
        move_speed=1.5,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
