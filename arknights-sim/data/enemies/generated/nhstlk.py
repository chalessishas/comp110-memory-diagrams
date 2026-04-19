"""逐腐兽 — generated from ArknightsGameData enemy_1270_nhstlk level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1270_nhstlk
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_nhstlk(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='逐腐兽',
        faction=Faction.ENEMY,
        max_hp=12000,
        atk=550,
        defence=150,
        res=20.0,
        atk_interval=1.8,
        move_speed=1.4,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
