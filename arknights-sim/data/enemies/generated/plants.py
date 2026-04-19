"""小型共生体 — generated from ArknightsGameData enemy_6012_plants level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_6012_plants
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_plants(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='小型共生体',
        faction=Faction.ENEMY,
        max_hp=3000,
        atk=350,
        defence=200,
        res=10.0,
        atk_interval=1.7,
        move_speed=0.8,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
