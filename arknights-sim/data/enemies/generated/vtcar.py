"""货运轨道车 — generated from ArknightsGameData enemy_10021_vtcar level 0.
motion=WALK  applyWay=NONE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_10021_vtcar
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_vtcar(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='货运轨道车',
        faction=Faction.ENEMY,
        max_hp=3500,
        atk=0,
        defence=150,
        res=0.0,
        atk_interval=10.0,
        move_speed=0.45,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
