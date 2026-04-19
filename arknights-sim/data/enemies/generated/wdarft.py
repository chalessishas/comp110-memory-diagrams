"""枯朽萃聚使徒 — generated from ArknightsGameData enemy_1321_wdarft level 0.
motion=FLY  applyWay=NONE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1321_wdarft
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_wdarft(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='枯朽萃聚使徒',
        faction=Faction.ENEMY,
        max_hp=30000,
        atk=500,
        defence=250,
        res=30.0,
        atk_interval=5.0,
        move_speed=0.3,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.AIRBORNE,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
