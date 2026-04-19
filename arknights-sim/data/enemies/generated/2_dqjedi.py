"""弧光武士 — generated from ArknightsGameData enemy_5045_dqjedi_2 level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_5045_dqjedi_2
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_2_dqjedi(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='弧光武士',
        faction=Faction.ENEMY,
        max_hp=14000,
        atk=800,
        defence=650,
        res=50.0,
        atk_interval=3.0,
        move_speed=0.75,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
