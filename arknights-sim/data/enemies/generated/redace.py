"""“红标”渗透者 — generated from ArknightsGameData enemy_1136_redace level 0.
motion=WALK  applyWay=RANGED  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1136_redace
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_redace(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='“红标”渗透者',
        faction=Faction.ENEMY,
        max_hp=6000,
        atk=400,
        defence=500,
        res=30.0,
        atk_interval=2.0,
        move_speed=1.3,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
