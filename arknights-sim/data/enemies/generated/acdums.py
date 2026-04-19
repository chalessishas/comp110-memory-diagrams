"""“裂管之音”/“断弦之音” — generated from ArknightsGameData enemy_9023_acdums level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_9023_acdums
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_acdums(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='“裂管之音”/“断弦之音”',
        faction=Faction.ENEMY,
        max_hp=10,
        atk=200,
        defence=0,
        res=0.0,
        atk_interval=4.0,
        move_speed=0.8,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
