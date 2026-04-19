"""蔓德拉 — generated from ArknightsGameData enemy_1523_mandra level 0.
motion=WALK  applyWay=ALL  lifeReduce=2
Regenerate: python tools/gen_enemies.py enemy_1523_mandra
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_mandra(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='蔓德拉',
        faction=Faction.ENEMY,
        max_hp=50000,
        atk=640,
        defence=520,
        res=35.0,
        atk_interval=1.8,
        move_speed=0.4,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
