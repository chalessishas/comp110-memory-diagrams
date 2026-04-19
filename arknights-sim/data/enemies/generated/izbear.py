"""下班的高普尼克 — generated from ArknightsGameData enemy_5075_izbear level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_5075_izbear
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_izbear(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='下班的高普尼克',
        faction=Faction.ENEMY,
        max_hp=30000,
        atk=2000,
        defence=200,
        res=50.0,
        atk_interval=3.5,
        move_speed=0.5,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
