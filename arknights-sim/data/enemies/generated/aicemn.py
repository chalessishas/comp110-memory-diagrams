"""冰晶射手 — generated from ArknightsGameData enemy_9005_aicemn level 0.
motion=WALK  applyWay=RANGED  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_9005_aicemn
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_aicemn(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='冰晶射手',
        faction=Faction.ENEMY,
        max_hp=16000,
        atk=400,
        defence=300,
        res=30.0,
        atk_interval=5.5,
        move_speed=0.7,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
