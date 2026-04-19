"""操戈 — generated from ArknightsGameData enemy_10164_tjgxb level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_10164_tjgxb
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_tjgxb(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='操戈',
        faction=Faction.ENEMY,
        max_hp=4500,
        atk=400,
        defence=200,
        res=5.0,
        atk_interval=3.0,
        move_speed=1.0,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
