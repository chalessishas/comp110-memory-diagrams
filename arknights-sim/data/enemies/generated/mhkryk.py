"""狡兽 — generated from ArknightsGameData enemy_1311_mhkryk level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1311_mhkryk
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_mhkryk(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='狡兽',
        faction=Faction.ENEMY,
        max_hp=20000,
        atk=1090,
        defence=480,
        res=0.0,
        atk_interval=1.8,
        move_speed=0.75,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
