"""香草翼兽（友方闪光） — generated from ArknightsGameData enemy_7061_xbsmiy level 0.
motion=FLY  applyWay=RANGED  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_7061_xbsmiy
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_xbsmiy(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='香草翼兽（友方闪光）',
        faction=Faction.ENEMY,
        max_hp=25000,
        atk=1600,
        defence=600,
        res=70.0,
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
