"""拟南兽（友方） — generated from ArknightsGameData enemy_7053_xbcasz level 0.
motion=WALK  applyWay=RANGED  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_7053_xbcasz
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_xbcasz(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='拟南兽（友方）',
        faction=Faction.ENEMY,
        max_hp=25000,
        atk=750,
        defence=450,
        res=40.0,
        atk_interval=3.2,
        move_speed=0.8,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
