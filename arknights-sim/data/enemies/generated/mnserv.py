"""英雄的理想 — generated from ArknightsGameData enemy_10161_mnserv level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_10161_mnserv
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_mnserv(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='英雄的理想',
        faction=Faction.ENEMY,
        max_hp=22000,
        atk=1100,
        defence=330,
        res=50.0,
        atk_interval=3.0,
        move_speed=0.7,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
