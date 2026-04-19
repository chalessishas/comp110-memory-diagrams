"""“开怀畅饮” — generated from ArknightsGameData enemy_10039_cnvber level 0.
motion=WALK  applyWay=ALL  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_10039_cnvber
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_cnvber(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='“开怀畅饮”',
        faction=Faction.ENEMY,
        max_hp=22000,
        atk=900,
        defence=900,
        res=20.0,
        atk_interval=5.0,
        move_speed=1.2,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
