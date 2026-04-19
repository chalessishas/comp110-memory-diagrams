"""沙堡设计师 — generated from ArknightsGameData enemy_1260_durmag_2 level 0.
motion=WALK  applyWay=RANGED  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1260_durmag_2
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_2_durmag(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='沙堡设计师',
        faction=Faction.ENEMY,
        max_hp=5000,
        atk=200,
        defence=300,
        res=50.0,
        atk_interval=1.5,
        move_speed=0.7,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
