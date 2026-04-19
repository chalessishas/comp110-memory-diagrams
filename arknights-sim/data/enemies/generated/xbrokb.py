"""游砂兽（家养版） — generated from ArknightsGameData enemy_7058_xbrokb level 0.
motion=WALK  applyWay=NONE  lifeReduce=2
Regenerate: python tools/gen_enemies.py enemy_7058_xbrokb
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_xbrokb(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='游砂兽（家养版）',
        faction=Faction.ENEMY,
        max_hp=50000,
        atk=400,
        defence=1500,
        res=20.0,
        atk_interval=5.0,
        move_speed=0.2,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
