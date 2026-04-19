"""卢西恩，“猩红血钻” — generated from ArknightsGameData enemy_2016_csphtm level 0.
motion=WALK  applyWay=MELEE  lifeReduce=30
Regenerate: python tools/gen_enemies.py enemy_2016_csphtm
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_csphtm(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='卢西恩，“猩红血钻”',
        faction=Faction.ENEMY,
        max_hp=80000,
        atk=1500,
        defence=600,
        res=40.0,
        atk_interval=3.0,
        move_speed=0.6,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
