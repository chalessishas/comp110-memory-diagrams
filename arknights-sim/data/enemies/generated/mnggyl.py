"""疑问的雕像 — generated from ArknightsGameData enemy_10157_mnggyl level 0.
motion=FLY  applyWay=RANGED  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_10157_mnggyl
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_mnggyl(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='疑问的雕像',
        faction=Faction.ENEMY,
        max_hp=6000,
        atk=450,
        defence=600,
        res=50.0,
        atk_interval=4.0,
        move_speed=0.75,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.AIRBORNE,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
