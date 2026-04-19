"""玻璃球打手 — generated from ArknightsGameData enemy_15027_dqmtrs level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_15027_dqmtrs
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_dqmtrs(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='玻璃球打手',
        faction=Faction.ENEMY,
        max_hp=4000,
        atk=800,
        defence=250,
        res=20.0,
        atk_interval=3.2,
        move_speed=0.9,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
