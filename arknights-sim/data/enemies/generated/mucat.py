"""重锤补给员 — generated from ArknightsGameData enemy_4008_mucat level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_4008_mucat
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_mucat(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='重锤补给员',
        faction=Faction.ENEMY,
        max_hp=30000,
        atk=480,
        defence=2000,
        res=70.0,
        atk_interval=1.7,
        move_speed=1.4,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
