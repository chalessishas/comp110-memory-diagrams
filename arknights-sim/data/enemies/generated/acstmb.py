"""“破胄之锤” — generated from ArknightsGameData enemy_9015_acstmb level 0.
motion=FLY  applyWay=ALL  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_9015_acstmb
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_acstmb(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='“破胄之锤”',
        faction=Faction.ENEMY,
        max_hp=250000,
        atk=350,
        defence=3500,
        res=10.0,
        atk_interval=8.0,
        move_speed=0.5,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.AIRBORNE,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
