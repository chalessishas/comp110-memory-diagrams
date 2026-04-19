"""暴鸰·G — generated from ArknightsGameData enemy_1040_bombd_2 level 0.
motion=FLY  applyWay=RANGED  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1040_bombd_2
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_2_bombd(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='暴鸰·G',
        faction=Faction.ENEMY,
        max_hp=6000,
        atk=1500,
        defence=220,
        res=30.0,
        atk_interval=5.0,
        move_speed=0.6,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.AIRBORNE,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
