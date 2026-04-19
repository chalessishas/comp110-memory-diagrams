"""行天卫生间 — generated from ArknightsGameData enemy_10151_nspace level 0.
motion=FLY  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_10151_nspace
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_nspace(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='行天卫生间',
        faction=Faction.ENEMY,
        max_hp=15000,
        atk=800,
        defence=1000,
        res=0.0,
        atk_interval=4.0,
        move_speed=0.3,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.AIRBORNE,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
