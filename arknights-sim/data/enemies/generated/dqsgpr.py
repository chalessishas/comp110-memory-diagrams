"""标枪恐鱼 — generated from ArknightsGameData enemy_15030_dqsgpr level 0.
motion=WALK  applyWay=RANGED  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_15030_dqsgpr
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_dqsgpr(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='标枪恐鱼',
        faction=Faction.ENEMY,
        max_hp=12500,
        atk=700,
        defence=240,
        res=20.0,
        atk_interval=3.5,
        move_speed=0.75,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
