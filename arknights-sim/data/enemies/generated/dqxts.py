"""最普通的鼷 — generated from ArknightsGameData enemy_15046_dqxts level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_15046_dqxts
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_dqxts(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='最普通的鼷',
        faction=Faction.ENEMY,
        max_hp=2000,
        atk=340,
        defence=0,
        res=0.0,
        atk_interval=0.8,
        move_speed=1.9,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
