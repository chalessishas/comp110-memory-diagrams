"""粉碎攻坚手 — generated from ArknightsGameData enemy_1045_hammer level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1045_hammer
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_hammer(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='粉碎攻坚手',
        faction=Faction.ENEMY,
        max_hp=10000,
        atk=1000,
        defence=1000,
        res=0.0,
        atk_interval=3.5,
        move_speed=0.5,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
