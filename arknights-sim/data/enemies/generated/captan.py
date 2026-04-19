"""潘乔·萨拉斯 — generated from ArknightsGameData enemy_1522_captan level 0.
motion=WALK  applyWay=ALL  lifeReduce=2
Regenerate: python tools/gen_enemies.py enemy_1522_captan
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_captan(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='潘乔·萨拉斯',
        faction=Faction.ENEMY,
        max_hp=27000,
        atk=1000,
        defence=750,
        res=30.0,
        atk_interval=4.0,
        move_speed=1.0,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
