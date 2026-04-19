"""同构碎片 — generated from ArknightsGameData enemy_1542_wdslm_3 level 0.
motion=WALK  applyWay=MELEE  lifeReduce=2
Regenerate: python tools/gen_enemies.py enemy_1542_wdslm_3
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_3_wdslm(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='同构碎片',
        faction=Faction.ENEMY,
        max_hp=100000,
        atk=550,
        defence=750,
        res=50.0,
        atk_interval=2.5,
        move_speed=0.5,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
