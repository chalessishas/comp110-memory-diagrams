"""纵尘者 — generated from ArknightsGameData enemy_7030_skodo level 0.
motion=WALK  applyWay=MELEE  lifeReduce=30
Regenerate: python tools/gen_enemies.py enemy_7030_skodo
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_skodo(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='纵尘者',
        faction=Faction.ENEMY,
        max_hp=750000,
        atk=1600,
        defence=2500,
        res=70.0,
        atk_interval=8.0,
        move_speed=0.6,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
