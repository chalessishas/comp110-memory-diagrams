"""狂暴宿主组长 — generated from ArknightsGameData enemy_1062_rager_2 level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1062_rager_2
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_2_rager(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='狂暴宿主组长',
        faction=Faction.ENEMY,
        max_hp=30000,
        atk=1750,
        defence=230,
        res=30.0,
        atk_interval=1.3,
        move_speed=1.2,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
