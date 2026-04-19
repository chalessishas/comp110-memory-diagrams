"""重生术师 — generated from ArknightsGameData enemy_15016_dqdkma level 0.
motion=WALK  applyWay=RANGED  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_15016_dqdkma
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_dqdkma(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='重生术师',
        faction=Faction.ENEMY,
        max_hp=12000,
        atk=420,
        defence=450,
        res=50.0,
        atk_interval=4.0,
        move_speed=0.7,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
