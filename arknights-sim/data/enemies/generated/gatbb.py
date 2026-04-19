"""翠梦使者 — generated from ArknightsGameData enemy_7023_gatbb level 0.
motion=WALK  applyWay=RANGED  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_7023_gatbb
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_gatbb(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='翠梦使者',
        faction=Faction.ENEMY,
        max_hp=9500,
        atk=430,
        defence=350,
        res=10.0,
        atk_interval=2.0,
        move_speed=0.8,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
