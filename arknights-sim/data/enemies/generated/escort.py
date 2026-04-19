"""播种无人机 — generated from ArknightsGameData enemy_6019_escort level 0.
motion=FLY  applyWay=RANGED  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_6019_escort
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_escort(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='播种无人机',
        faction=Faction.ENEMY,
        max_hp=6500,
        atk=340,
        defence=250,
        res=50.0,
        atk_interval=4.5,
        move_speed=0.5,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.AIRBORNE,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
