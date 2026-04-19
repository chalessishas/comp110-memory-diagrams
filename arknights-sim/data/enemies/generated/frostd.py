"""寒霜 — generated from ArknightsGameData enemy_1042_frostd level 0.
motion=FLY  applyWay=NONE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1042_frostd
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_frostd(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='寒霜',
        faction=Faction.ENEMY,
        max_hp=6500,
        atk=100,
        defence=600,
        res=30.0,
        atk_interval=1.0,
        move_speed=0.9,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.AIRBORNE,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
