"""灼藤 — generated from ArknightsGameData enemy_10067_ftsjc level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_10067_ftsjc
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_ftsjc(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='灼藤',
        faction=Faction.ENEMY,
        max_hp=13000,
        atk=800,
        defence=250,
        res=65.0,
        atk_interval=3.5,
        move_speed=0.85,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
