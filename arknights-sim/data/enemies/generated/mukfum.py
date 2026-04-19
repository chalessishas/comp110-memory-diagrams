"""球德联击球手 — generated from ArknightsGameData enemy_4028_mukfum level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_4028_mukfum
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_mukfum(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='球德联击球手',
        faction=Faction.ENEMY,
        max_hp=30000,
        atk=1200,
        defence=500,
        res=20.0,
        atk_interval=3.0,
        move_speed=1.2,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
