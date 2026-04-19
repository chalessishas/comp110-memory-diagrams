"""裹骸死士 — generated from ArknightsGameData enemy_1419_mmcike level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1419_mmcike
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_mmcike(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='裹骸死士',
        faction=Faction.ENEMY,
        max_hp=24000,
        atk=1500,
        defence=800,
        res=60.0,
        atk_interval=3.0,
        move_speed=0.8,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
