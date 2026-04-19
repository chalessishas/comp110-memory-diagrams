"""枣大刀 — generated from ArknightsGameData enemy_2112_dyhlgy level 0.
motion=WALK  applyWay=MELEE  lifeReduce=3
Regenerate: python tools/gen_enemies.py enemy_2112_dyhlgy
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_dyhlgy(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='枣大刀',
        faction=Faction.ENEMY,
        max_hp=35000,
        atk=800,
        defence=800,
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
