"""小寄居蟹 — generated from ArknightsGameData enemy_5044_dqzeni level 0.
motion=WALK  applyWay=RANGED  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_5044_dqzeni
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_dqzeni(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='小寄居蟹',
        faction=Faction.ENEMY,
        max_hp=6000,
        atk=330,
        defence=200,
        res=10.0,
        atk_interval=2.5,
        move_speed=0.9,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
