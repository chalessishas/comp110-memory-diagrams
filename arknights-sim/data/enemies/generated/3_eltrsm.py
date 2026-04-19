"""“迷迭香”，虚实之握 — generated from ArknightsGameData enemy_8007_eltrsm_3 level 0.
motion=WALK  applyWay=ALL  lifeReduce=5
Regenerate: python tools/gen_enemies.py enemy_8007_eltrsm_3
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_3_eltrsm(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='“迷迭香”，虚实之握',
        faction=Faction.ENEMY,
        max_hp=50000,
        atk=2000,
        defence=1000,
        res=50.0,
        atk_interval=4.0,
        move_speed=0.4,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
