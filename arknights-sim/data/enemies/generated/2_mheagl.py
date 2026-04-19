"""迅猛锋羽兽 — generated from ArknightsGameData enemy_1308_mheagl_2 level 0.
motion=WALK  applyWay=RANGED  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1308_mheagl_2
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_2_mheagl(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='迅猛锋羽兽',
        faction=Faction.ENEMY,
        max_hp=12000,
        atk=550,
        defence=80,
        res=5.0,
        atk_interval=2.5,
        move_speed=0.65,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
