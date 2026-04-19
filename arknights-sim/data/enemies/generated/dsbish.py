"""玛利图斯，“海嗣” — generated from ArknightsGameData enemy_1556_dsbish level 0.
motion=WALK  applyWay=RANGED  lifeReduce=2
Regenerate: python tools/gen_enemies.py enemy_1556_dsbish
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_dsbish(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='玛利图斯，“海嗣”',
        faction=Faction.ENEMY,
        max_hp=80000,
        atk=100,
        defence=0,
        res=90.0,
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
