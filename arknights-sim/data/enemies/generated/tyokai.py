"""赞助无人机 — generated from ArknightsGameData enemy_1105_tyokai level 0.
motion=FLY  applyWay=NONE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1105_tyokai
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_tyokai(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='赞助无人机',
        faction=Faction.ENEMY,
        max_hp=5000,
        atk=0,
        defence=150,
        res=20.0,
        atk_interval=1.0,
        move_speed=1.0,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.AIRBORNE,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
