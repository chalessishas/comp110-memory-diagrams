"""残党乐团指挥家 — generated from ArknightsGameData enemy_1379_ltncdt level 0.
motion=WALK  applyWay=RANGED  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1379_ltncdt
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_ltncdt(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='残党乐团指挥家',
        faction=Faction.ENEMY,
        max_hp=23000,
        atk=350,
        defence=550,
        res=60.0,
        atk_interval=3.0,
        move_speed=0.65,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
