"""乌萨斯突袭弩手 — generated from ArknightsGameData enemy_1109_uabone level 0.
motion=WALK  applyWay=RANGED  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1109_uabone
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_uabone(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='乌萨斯突袭弩手',
        faction=Faction.ENEMY,
        max_hp=4000,
        atk=350,
        defence=200,
        res=20.0,
        atk_interval=2.3,
        move_speed=1.0,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
