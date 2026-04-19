"""深池塑能术师队长 — generated from ArknightsGameData enemy_1176_dusocr_2 level 0.
motion=WALK  applyWay=NONE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1176_dusocr_2
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_2_dusocr(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='深池塑能术师队长',
        faction=Faction.ENEMY,
        max_hp=20000,
        atk=0,
        defence=550,
        res=50.0,
        atk_interval=5.0,
        move_speed=0.3,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
