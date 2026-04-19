"""马特奥的亲卫 — generated from ArknightsGameData enemy_1409_bdguad_3 level 0.
motion=WALK  applyWay=ALL  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1409_bdguad_3
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_3_bdguad(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='马特奥的亲卫',
        faction=Faction.ENEMY,
        max_hp=18000,
        atk=1100,
        defence=1000,
        res=30.0,
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
