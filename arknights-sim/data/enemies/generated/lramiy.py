"""演出阿米娅 — generated from ArknightsGameData enemy_3008_lramiy level 0.
motion=FLY  applyWay=NONE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_3008_lramiy
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_lramiy(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='演出阿米娅',
        faction=Faction.ENEMY,
        max_hp=20000,
        atk=1500,
        defence=2000,
        res=80.0,
        atk_interval=1.0,
        move_speed=0.3,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.AIRBORNE,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
