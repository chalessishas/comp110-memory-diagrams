"""“终点” — generated from ArknightsGameData enemy_10071_ftprg level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_10071_ftprg
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_ftprg(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='“终点”',
        faction=Faction.ENEMY,
        max_hp=8500,
        atk=680,
        defence=300,
        res=40.0,
        atk_interval=1.8,
        move_speed=0.65,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
