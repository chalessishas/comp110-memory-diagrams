"""清洗弹力球 — generated from ArknightsGameData enemy_1236_bouncy_2 level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1236_bouncy_2
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_2_bouncy(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='清洗弹力球',
        faction=Faction.ENEMY,
        max_hp=80000,
        atk=2000,
        defence=600,
        res=30.0,
        atk_interval=1.5,
        move_speed=1.2,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
