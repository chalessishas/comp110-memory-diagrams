"""雅气 — generated from ArknightsGameData enemy_1197_sfshu_2 level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1197_sfshu_2
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_2_sfshu(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='雅气',
        faction=Faction.ENEMY,
        max_hp=3350,
        atk=410,
        defence=70,
        res=0.0,
        atk_interval=2.0,
        move_speed=1.4,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
