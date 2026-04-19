"""饮啄 — generated from ArknightsGameData enemy_10059_cjgfod level 0.
motion=WALK  applyWay=NONE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_10059_cjgfod
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_cjgfod(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='饮啄',
        faction=Faction.ENEMY,
        max_hp=5,
        atk=100,
        defence=0,
        res=0.0,
        atk_interval=1.7,
        move_speed=0.7,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
