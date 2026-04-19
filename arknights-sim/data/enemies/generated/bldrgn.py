"""巨翼兽 — generated from ArknightsGameData enemy_7010_bldrgn level 0.
motion=WALK  applyWay=ALL  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_7010_bldrgn
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_bldrgn(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='巨翼兽',
        faction=Faction.ENEMY,
        max_hp=750000,
        atk=2300,
        defence=700,
        res=50.0,
        atk_interval=3.5,
        move_speed=0.7,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
