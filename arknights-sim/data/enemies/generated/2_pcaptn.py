"""美声水手长 — generated from ArknightsGameData enemy_10049_pcaptn_2 level 0.
motion=WALK  applyWay=ALL  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_10049_pcaptn_2
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_2_pcaptn(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='美声水手长',
        faction=Faction.ENEMY,
        max_hp=30000,
        atk=850,
        defence=800,
        res=30.0,
        atk_interval=3.0,
        move_speed=0.45,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
