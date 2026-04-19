"""矢量战术装备 — generated from ArknightsGameData enemy_8008_eltswd level 0.
motion=WALK  applyWay=NONE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_8008_eltswd
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_eltswd(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='矢量战术装备',
        faction=Faction.ENEMY,
        max_hp=20000,
        atk=100,
        defence=1000,
        res=20.0,
        atk_interval=1.0,
        move_speed=1.0,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
