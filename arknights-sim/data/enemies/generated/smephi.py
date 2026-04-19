"""梅菲斯特，“歌者” — generated from ArknightsGameData enemy_1514_smephi level 0.
motion=WALK  applyWay=RANGED  lifeReduce=2
Regenerate: python tools/gen_enemies.py enemy_1514_smephi
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_smephi(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='梅菲斯特，“歌者”',
        faction=Faction.ENEMY,
        max_hp=60000,
        atk=450,
        defence=450,
        res=30.0,
        atk_interval=4.0,
        move_speed=0.1,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
