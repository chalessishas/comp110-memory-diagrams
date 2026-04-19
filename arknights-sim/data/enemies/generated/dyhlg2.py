"""文衡君 — generated from ArknightsGameData enemy_2113_dyhlg2 level 0.
motion=WALK  applyWay=MELEE  lifeReduce=3
Regenerate: python tools/gen_enemies.py enemy_2113_dyhlg2
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_dyhlg2(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='文衡君',
        faction=Faction.ENEMY,
        max_hp=24000,
        atk=600,
        defence=600,
        res=60.0,
        atk_interval=2.5,
        move_speed=0.7,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
