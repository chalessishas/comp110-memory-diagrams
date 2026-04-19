"""圣徒伊比利亚 — generated from ArknightsGameData enemy_2027_syudg2 level 0.
motion=WALK  applyWay=RANGED  lifeReduce=5
Regenerate: python tools/gen_enemies.py enemy_2027_syudg2
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_syudg2(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='圣徒伊比利亚',
        faction=Faction.ENEMY,
        max_hp=70000,
        atk=2200,
        defence=400,
        res=20.0,
        atk_interval=4.0,
        move_speed=0.5,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
