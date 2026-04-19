"""时光守卫 — generated from ArknightsGameData enemy_7026_xbele level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_7026_xbele
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_xbele(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='时光守卫',
        faction=Faction.ENEMY,
        max_hp=700000,
        atk=1150,
        defence=2000,
        res=20.0,
        atk_interval=3.0,
        move_speed=0.4,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
