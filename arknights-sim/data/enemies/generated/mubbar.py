"""深水大力士 — generated from ArknightsGameData enemy_4050_mubbar level 0.
motion=WALK  applyWay=ALL  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_4050_mubbar
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_mubbar(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='深水大力士',
        faction=Faction.ENEMY,
        max_hp=26000,
        atk=540,
        defence=950,
        res=0.0,
        atk_interval=6.0,
        move_speed=0.8,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
