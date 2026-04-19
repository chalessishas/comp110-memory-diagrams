"""家族术师 — generated from ArknightsGameData enemy_1280_sgmag level 0.
motion=WALK  applyWay=RANGED  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1280_sgmag
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_sgmag(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='家族术师',
        faction=Faction.ENEMY,
        max_hp=4500,
        atk=320,
        defence=250,
        res=40.0,
        atk_interval=3.5,
        move_speed=0.8,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
