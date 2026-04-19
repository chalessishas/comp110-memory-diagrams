"""拟南兽（闪光友方） — generated from ArknightsGameData enemy_7060_xbcasy level 0.
motion=WALK  applyWay=RANGED  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_7060_xbcasy
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_xbcasy(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='拟南兽（闪光友方）',
        faction=Faction.ENEMY,
        max_hp=25000,
        atk=900,
        defence=500,
        res=50.0,
        atk_interval=3.2,
        move_speed=1.0,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
