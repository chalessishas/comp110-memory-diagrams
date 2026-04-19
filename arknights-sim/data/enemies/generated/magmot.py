"""术师快艇 — generated from ArknightsGameData enemy_1162_magmot level 0.
motion=WALK  applyWay=RANGED  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1162_magmot
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_magmot(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='术师快艇',
        faction=Faction.ENEMY,
        max_hp=12000,
        atk=300,
        defence=200,
        res=0.0,
        atk_interval=3.5,
        move_speed=1.1,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
