"""开天汽水瓶 — generated from ArknightsGameData enemy_10146_nscola level 0.
motion=FLY  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_10146_nscola
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_nscola(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='开天汽水瓶',
        faction=Faction.ENEMY,
        max_hp=5000,
        atk=350,
        defence=100,
        res=10.0,
        atk_interval=3.0,
        move_speed=0.3,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.AIRBORNE,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
