"""战术弩手 — generated from ArknightsGameData enemy_1141_merbow level 0.
motion=WALK  applyWay=RANGED  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1141_merbow
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_merbow(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='战术弩手',
        faction=Faction.ENEMY,
        max_hp=3100,
        atk=320,
        defence=260,
        res=40.0,
        atk_interval=2.4,
        move_speed=0.9,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
