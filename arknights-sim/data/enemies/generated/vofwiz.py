"""术师囚犯 — generated from ArknightsGameData enemy_1120_vofwiz level 0.
motion=WALK  applyWay=NONE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1120_vofwiz
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_vofwiz(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='术师囚犯',
        faction=Faction.ENEMY,
        max_hp=9000,
        atk=300,
        defence=100,
        res=50.0,
        atk_interval=3.5,
        move_speed=0.5,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
