"""香草翼兽（家养版） — generated from ArknightsGameData enemy_7055_xbsmib level 0.
motion=FLY  applyWay=RANGED  lifeReduce=2
Regenerate: python tools/gen_enemies.py enemy_7055_xbsmib
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_xbsmib(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='香草翼兽（家养版）',
        faction=Faction.ENEMY,
        max_hp=150000,
        atk=1200,
        defence=900,
        res=70.0,
        atk_interval=6.0,
        move_speed=0.6,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.AIRBORNE,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
