"""R-11突击动力装甲 — generated from ArknightsGameData enemy_1256_lyacpa level 0.
motion=WALK  applyWay=RANGED  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1256_lyacpa
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_lyacpa(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='R-11突击动力装甲',
        faction=Faction.ENEMY,
        max_hp=25000,
        atk=1200,
        defence=1200,
        res=20.0,
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
