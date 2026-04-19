"""骑士领游荡者 — generated from ArknightsGameData enemy_1181_napkgt level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1181_napkgt
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_napkgt(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='骑士领游荡者',
        faction=Faction.ENEMY,
        max_hp=7500,
        atk=800,
        defence=550,
        res=20.0,
        atk_interval=2.5,
        move_speed=1.3,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
