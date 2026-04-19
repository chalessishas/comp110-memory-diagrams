"""采掘机 — generated from ArknightsGameData enemy_7033_xbdrcar level 0.
motion=WALK  applyWay=NONE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_7033_xbdrcar
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_xbdrcar(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='采掘机',
        faction=Faction.ENEMY,
        max_hp=5000,
        atk=1,
        defence=0,
        res=0.0,
        atk_interval=0.1,
        move_speed=1.5,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
