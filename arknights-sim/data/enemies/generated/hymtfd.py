"""沙车 — generated from ArknightsGameData enemy_5006_hymtfd level 0.
motion=FLY  applyWay=ALL  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_5006_hymtfd
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_hymtfd(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='沙车',
        faction=Faction.ENEMY,
        max_hp=10000,
        atk=1500,
        defence=800,
        res=0.0,
        atk_interval=1.0,
        move_speed=2.7,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.AIRBORNE,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
