"""云中墨贼 — generated from ArknightsGameData enemy_10169_tjgtsz level 0.
motion=FLY  applyWay=RANGED  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_10169_tjgtsz
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_tjgtsz(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='云中墨贼',
        faction=Faction.ENEMY,
        max_hp=10000,
        atk=450,
        defence=450,
        res=20.0,
        atk_interval=4.0,
        move_speed=1.3,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.AIRBORNE,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
