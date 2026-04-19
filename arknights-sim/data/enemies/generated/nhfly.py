"""枯朽之种 — generated from ArknightsGameData enemy_1269_nhfly level 0.
motion=FLY  applyWay=RANGED  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1269_nhfly
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_nhfly(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='枯朽之种',
        faction=Faction.ENEMY,
        max_hp=1200,
        atk=750,
        defence=0,
        res=0.0,
        atk_interval=1.0,
        move_speed=0.6,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.AIRBORNE,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
