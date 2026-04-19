"""伊莎玛拉之泪 — generated from ArknightsGameData enemy_2040_syrott level 0.
motion=WALK  applyWay=NONE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_2040_syrott
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_syrott(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='伊莎玛拉之泪',
        faction=Faction.ENEMY,
        max_hp=10000,
        atk=500,
        defence=1200,
        res=60.0,
        atk_interval=5.0,
        move_speed=1.0,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
